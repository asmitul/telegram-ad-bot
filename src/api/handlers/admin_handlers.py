from telegram import Update
from telegram.ext import ContextTypes
from src.services.admin_service import AdminService
from src.api.handlers.base_handler import BaseHandler, admin_required
from src.utils.logger import log_telegram, log_error
from src.services.message_service import MessageService
from src.models.chat_group import ChatGroup

class AdminHandler(BaseHandler):
    def __init__(self, application):
        super().__init__(application)
        self.admin_service = AdminService(self.repository)
    
    async def handle_admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /admin 命令"""
        if not update.effective_user:
            return
            
        # 检查是否有管理员，如果没有则将第一个使用此命令的用户设为管理员
        admins = await self.admin_service.get_all_admins()
        if not admins:
            success = await self.admin_service.add_admin(
                update.effective_user.id,
                update.effective_user.username
            )
            if success:
                await self.send_success_message(
                    update,
                    f"您已被设置为首位管理员！\n"
                    f"ID: {update.effective_user.id}"
                )
                return
        
        # 如果已经有管理员，则需要管理员权限
        if not await self.admin_service.is_admin(update.effective_user.id):
            await self.send_error_message(update, "您不是管理员")
            return
        
        # 处理添加新管理员
        if context.args:
            try:
                new_admin_id = int(context.args[0])
                if await self.admin_service.add_admin(new_admin_id):
                    await self.send_success_message(
                        update,
                        f"已添加新管理员 {new_admin_id}"
                    )
                else:
                    await self.send_error_message(
                        update,
                        "添加管理员失败"
                    )
            except ValueError:
                await self.send_error_message(
                    update,
                    "无效的用户ID格式。请使用数字ID。"
                )
            return
        
        # 显示管理员列表
        admins = await self.admin_service.get_all_admins()
        admin_list = "\n".join([
            f"- ID: {admin.id} | Username: @{admin.username or 'None'}"
            for admin in admins
        ])
        await update.message.reply_text(
            f"📋 管理员列表：\n{admin_list}"
        )
        log_telegram(f"User {update.message.from_user.id} listed all admins")
    
    @admin_required
    async def handle_remove_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /remove_admin 命令"""
        if not context.args:
            await self.send_error_message(
                update,
                "请提供要移除的管理员ID\n"
                "用法: /remove_admin <admin_id>"
            )
            return
            
        try:
            admin_id = int(context.args[0])
            if await self.admin_service.remove_admin(admin_id):
                await self.send_success_message(
                    update,
                    f"已移除管理员 {admin_id}"
                )
            else:
                await self.send_error_message(
                    update,
                    "移除管理员失败"
                )
        except ValueError:
            await self.send_error_message(
                update,
                "无效的用户ID格式"
            )
    
    # 设置目标群组
    @admin_required
    async def handle_set_target_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /set_target 命令"""
        if not context.args:
            await self.send_error_message(
                update,
                "请提供目标群组ID\n"
                "用法: /set_target <群组ID>"
            )
            return

        try:
            target_group_id = int(context.args[0])
            
            # 获取群组信息
            group = await self.repository.get_group(target_group_id)
            if not group:
                # 如果群组不存在，创建新的群组记录
                group = ChatGroup(
                    id=target_group_id,
                    title="Target Group",  # 可以后续更新
                    type="supergroup",
                    is_ad_group=True
                )
            else:
                # 如果群组存在，更新其广告群状态
                group.is_ad_group = True
            
            # 保存群组信息
            success = await self.repository.save_group(group)
            
            # 设置为目标群组
            if success:
                await self.repository.set_target_group(target_group_id)
            
            # 验证保存结果
            saved_group = await self.repository.get_group(target_group_id)
            
            if success and saved_group and saved_group.is_ad_group:
                await self.send_success_message(
                    update, 
                    f"已成功设置目标群组ID为：{target_group_id}，并将其标记为广告群"
                )
            else:
                await self.send_error_message(update, "设置目标群组失败")
                
        except ValueError:
            await self.send_error_message(update, "无效的群组ID，请提供正确的数字ID。")

    # 设置目标频道
    @admin_required
    async def handle_set_target_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /set_target_channel 命令"""
        if not context.args:
            await self.send_error_message(
                update,
                "请提供目标频道ID\n"
                "用法: /set_target_channel <频道ID>"
            )
            return

        try:
            target_channel_id = int(context.args[0])
            await self.repository.set_target_channel(target_channel_id)
            await self.send_success_message(update, f"已成功设置目标频道ID为：{target_channel_id}")
        except ValueError:
            await self.send_error_message(update, "无效的频道ID，请提供正确的数字ID。")

    async def handle_help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /help 命令"""
        help_text = (
            "🤖 可用命令列表\n\n"
            "管理员命令:\n"
            "• /admin - 初始化管理员或添加新管理员\n"
            "• /remove_admin - 移除管理员\n"
            "• /set_target - 设置目标群组\n"
            "• /show_target - 显示当前目标群组\n"
            "• /set_target_channel - 设置目标频道\n"
            "• /show_target_channel - 显示当前目标频道\n"
            "• /toggle_verification - 开启/关闭频道验证功能\n\n"
            "广告管理命令:\n"
            "• /add_ad - 添加新广告\n"
            "• /list_ads - 查看所有广告\n"
            "• /delete_ad - 删除指定广告\n\n"
            "禁言管理命令:\n"
            "• /add_banned_word - 添加禁言词\n"
            "• /list_banned_words - 查看所有禁言词\n"
            "• /delete_banned_word - 删除禁言词\n\n"
            "其他命令:\n"
            "• /help - 显示此帮助信息\n"
            "• /getid - 获取当前群组ID"
        )
        
        await update.message.reply_text(help_text)

    @admin_required
    async def handle_show_target(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /show_target 命令"""
        try:
            target_group_id = await self.repository.get_target_group_id()
            if not target_group_id:
                await self.send_error_message(update, "未设置目标群组")
                return
            
            # 获取群组信息
            group = await self.repository.get_group(target_group_id)
            if group:
                await update.message.reply_text(
                    f"当前目标群组信息：\n"
                    f"• ID: {group.id}\n"
                    f"• 标题: {group.title}\n"
                    f"• 类型: {group.type}\n"
                    f"• 是否为广告群: {'是' if group.is_ad_group else '否'}"
                )
            else:
                await update.message.reply_text(
                    f"📍 当前目标群组ID：{target_group_id}\n"
                    "⚠️ 注意：未找到该群组的详细信息"
                )
        except Exception as e:
            log_error(e, "获取目标群组信息失败")
            await self.send_error_message(update, "获取目标群组信息失败")

    @admin_required
    async def handle_show_target_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /show_target_channel 命令"""
        try:
            target_channel_id = await self.repository.get_target_channel_id()
            if not target_channel_id:
                await self.send_error_message(update, "未设置目标频道")
                return
            
            try:
                # 尝试获取频道信息
                channel = await context.bot.get_chat(target_channel_id)
                await update.message.reply_text(
                    f"📍 当前目标频道信息：\n"
                    f"• ID: {channel.id}\n"
                    f"• 标题: {channel.title}\n"
                    f"• 类型: {channel.type}\n"
                    f"• 用户名: @{channel.username or '无'}"
                )
            except Exception as e:
                await update.message.reply_text(
                    f"📍 当前目标频道ID：{target_channel_id}\n"
                    "⚠️ 注意：无法获取该频道的详细信息"
                )
        except Exception as e:
            log_error(e, "获取目标频道信息失败")
            await self.send_error_message(update, "获取目标频道信息失败")

    @admin_required
    async def handle_toggle_verification(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /toggle_verification 命令"""
        try:
            current_status = await self.repository.get_channel_verification_status()
            new_status = not current_status
            
            if await self.repository.set_channel_verification(new_status):
                status_text = "启用" if new_status else "禁用"
                await self.send_success_message(
                    update,
                    f"已{status_text}频道验证功能"
                )
            else:
                await self.send_error_message(update, "切换频道验证状态失败")
        except Exception as e:
            await self.send_error_message(update, f"操作失败: {str(e)}")

    async def handle_get_id(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /getid 命令"""
        if not update.effective_chat:
            return
        
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        chat_title = update.effective_chat.title if update.effective_chat.title else "私聊"
        
        await update.message.reply_text(
            f"📝 群组信息：\n"
            f"• ID: {chat_id}\n"
            f"• 类型: {chat_type}\n"
            f"• 标题: {chat_title}"
        )