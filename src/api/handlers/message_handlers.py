from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from src.models.chat_group import ChatGroup
from src.services.ad_service import AdService
from src.services.message_service import MessageService
from src.api.handlers.base_handler import BaseHandler
from src.utils.logger import log_info, log_error, log_warning
from datetime import datetime
import asyncio
from src.services.banned_word_service import BannedWordService

class MessageHandler(BaseHandler):
    def __init__(self, application):
        super().__init__(application)
        self.message_service = MessageService(self.repository)
        self.banned_word_service = BannedWordService(self.repository)

    # handle_bot_error
    async def handle_bot_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理错误"""
        # 记录错误信息
        log_error(f"Bot encountered error: {context.error}")
        
        try:
            # 获取第一个管理员
            admins = await self.repository.get_all_admins()
            if not admins:
                log_warning("No admin users found to send error notification")
                return
            
            first_admin = admins[0]
            
            # 向第一个管理员发送错误通知
            await context.bot.send_message(
                chat_id=first_admin.id,
                text=f"🚨 机器人遇到错误:\n{str(context.error)}\n\n"
                     f"发生时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
        except Exception as e:
            # 如果发送错误消息时出现问题，记录该错误
            log_error(f"Failed to send error message to admin: {e}")
    
    async def handle_new_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理新消息"""
        if not update.effective_chat or not update.effective_user or not update.message or not update.message.text:
            return
        
        chat = update.effective_chat
        user = update.effective_user
        
        # 检查消息是否包含禁言词
        if await self.banned_word_service.check_message(update.message.text):
            try:
                await update.message.delete()
                warning = await context.bot.send_message(
                    chat_id=chat.id,
                    text=f"⚠️ {user.first_name}，您的消息包含禁用词，已被删除。"
                )
                asyncio.create_task(self._delete_message_later(warning, 10))
                return
            except Exception as e:
                log_error(e, "处理禁言消息失败")
        
        log_info(f"收到群组 {chat.title} ({chat.id}) 的消息")
        
        # 获取并更新群组信息
        existing_group = await self.repository.get_group(chat.id)
        if existing_group:
            existing_group.title = chat.title
            existing_group.type = chat.type
            group = existing_group
        else:
            group = ChatGroup(
                id=chat.id,
                title=chat.title,
                type=chat.type,
                is_ad_group=False
            )
        
        await self.repository.save_group(group)
        
        # 如果是广告群，检查用户是否关注了目标频道
        if group.is_ad_group and update.message:
            # 先检查频道验证功能是否启用
            verification_enabled = await self.repository.get_channel_verification_status()
            if not verification_enabled:
                return

            settings = self.repository.app.bot_data.get('settings', {})
            target_channel_id = settings.get('target_channel_id')
            
            if not target_channel_id:
                log_warning("未设置目标频道ID")
                return
            
            log_info(f"检查用户 {user.id} 的频道订阅状态，目标频道: {target_channel_id}")
            
            is_subscribed = await self.message_service.check_channel_subscription(user.id, context.bot)
            if not is_subscribed:
                try:
                    # 尝试获取频道信息
                    try:
                        channel = await context.bot.get_chat(target_channel_id)
                        log_info(f"成功获取频道信息: {channel.title} ({channel.id})")
                    except Exception as e:
                        log_error(e, f"获取频道信息失败: {target_channel_id}")
                        # 如果获取频道信息失败，仍然尝试创建链接
                        channel = None
                    
                    # 创建频道链接
                    if channel and channel.username:
                        channel_link = f"https://t.me/{channel.username}"
                    else:
                        # 移除 -100 前缀（如果存在）
                        clean_channel_id = str(target_channel_id)
                        if clean_channel_id.startswith('-100'):
                            clean_channel_id = clean_channel_id[4:]
                        channel_link = f"https://t.me/c/{clean_channel_id}"
                    
                    log_info(f"创建的频道链接: {channel_link}")
                    
                    # 创建提醒消息的按钮
                    keyboard = [[InlineKeyboardButton("点击关注频道", url=channel_link)]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    # 发送提醒消息
                    reminder = await context.bot.send_message(
                        chat_id=chat.id,
                        text=f"⚠️ 亲爱的 {user.first_name}，\n"
                             "您需要先关注我们的频道才能在群内发言。\n"
                             "关注后即可正常发言！",
                        reply_markup=reply_markup
                    )
                    
                    # 删除用户的消息
                    try:
                        await update.message.delete()
                    except Exception as e:
                        log_error(e, "删除消息失败")
                    
                    # 设置定时删除提醒消息
                    asyncio.create_task(self._delete_message_later(reminder, 30))
                    
                except Exception as e:
                    log_error(e, "发送频道订阅提醒失败")
    
    async def _delete_message_later(self, message, delay_seconds: int):
        """延迟删除消息"""
        await asyncio.sleep(delay_seconds)
        try:
            await message.delete()
        except Exception as e:
            log_error(e, "删除提醒消息失败")
    
    async def handle_join_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理加入请求"""
        # 实现加入请求的处理逻辑
        pass

    async def handle_new_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理新成员加入群组的事件"""
        if not update.message or not update.message.new_chat_members:
            return

        try:
            # 获取广告服务实例
            ad_service = AdService(self.repository)
            
            # 获取一个随机广告
            ad = await ad_service.get_random_ad()
            if not ad:
                return

            # 为每个新成员发送欢迎消息
            for new_member in update.message.new_chat_members:
                # 如果是机器人自己，则跳过
                if new_member.id == context.bot.id:
                    continue

                # 创建欢迎消息的按钮，每行两个按钮
                keyboard = []
                row = []
                for i, button in enumerate(ad.buttons):
                    row.append(InlineKeyboardButton(button['text'], url=button['url']))
                    # 每两个按钮或最后一个按钮时，添加到键盘
                    if len(row) == 2 or i == len(ad.buttons) - 1:
                        keyboard.append(row)
                        row = []
                reply_markup = InlineKeyboardMarkup(keyboard)

                # 格式化欢迎消息
                welcome_text = ad.welcome_text.format(
                    name=new_member.first_name,
                    username=new_member.username or new_member.first_name
                )

                # 根据广告类型发送不同的媒体消息
                if ad.media_type == 'photo':
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=ad.media_id,
                        caption=f"{welcome_text}\n\n{ad.ad_text}",
                        reply_markup=reply_markup
                    )
                elif ad.media_type == 'video':
                    await context.bot.send_video(
                        chat_id=update.effective_chat.id,
                        video=ad.media_id,
                        caption=f"{welcome_text}\n\n{ad.ad_text}",
                        reply_markup=reply_markup
                    )

                log_info(f"已向新成员 {new_member.first_name} (ID: {new_member.id}) 发送欢迎消息")

        except Exception as e:
            log_error(e, "处理新成员消息时出错")