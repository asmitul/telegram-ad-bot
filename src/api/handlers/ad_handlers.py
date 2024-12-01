from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.services.ad_service import AdService
from src.api.handlers.base_handler import BaseHandler, admin_required
from src.utils.logger import log_info, log_error

class AdHandler(BaseHandler):
    def __init__(self, application):
        super().__init__(application)
        self.ad_service = AdService(self.repository)
    
    @admin_required
    async def handle_add_ad(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /add_ad 命令"""
        context.user_data['waiting_for_ad'] = True
        await update.message.reply_text(
            "📝 请按以下步骤添加广告：\n"
            "1. 发送广告图片或视频\n"
            "2. 回复该媒体，使用以下格式：\n\n"
            "欢迎语\n"
            "广告语\n"
            "按钮文字|按钮链接"
        )
    
    async def handle_ad_media(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理广告媒体和文本"""
        if not context.user_data.get('waiting_for_ad'):
            return
            
        if update.message.photo or update.message.video:
            # 存储媒体信息
            media_id = update.message.photo[-1].file_id if update.message.photo else update.message.video.file_id
            media_type = 'photo' if update.message.photo else 'video'
            
            context.user_data['temp_ad'] = {
                'media_id': media_id,
                'media_type': media_type
            }
            await self.send_success_message(
                update,
                "媒体已收到，请回复此消息添加文本内容\n\n"
                "格式示例：\n"
                "欢迎语\n\n\n"
                "广告语\n可以包含多行\n\n\n"
                "按钮1文字|按钮1链接;按钮2文字|按钮2链接"
            )
            
        elif update.message.reply_to_message and context.user_data.get('temp_ad'):
            try:
                # 使用双换行符分割文本内容
                parts = update.message.text.split('\n\n\n')
                if len(parts) != 3:
                    raise ValueError("文本格式错误：需要包含欢迎语、广告语和按钮信息，用三个换行符分隔")
                
                welcome_text = parts[0].strip()
                ad_text = parts[1].strip()
                buttons_info = parts[2].strip()
                
                # 解析按钮信息
                buttons = []
                for button_info in buttons_info.split(';'):
                    try:
                        button_text, button_url = button_info.strip().split('|')
                        buttons.append({
                            'text': button_text.strip(),
                            'url': button_url.strip()
                        })
                    except ValueError:
                        raise ValueError("按钮格式错误：每个按钮应为 '按钮文字|按钮链接'，多个按钮用分号分隔")
                
                if not buttons:
                    raise ValueError("至少需要一个按钮")
                
                # 创建广告
                ad = await self.ad_service.create_ad(
                    media_id=context.user_data['temp_ad']['media_id'],
                    media_type=context.user_data['temp_ad']['media_type'],
                    welcome_text=welcome_text,
                    ad_text=ad_text,
                    buttons=buttons  # 现在传递按钮列表
                )
                
                if ad:
                    await self.send_success_message(update, "广告添加成功！")
                else:
                    await self.send_error_message(update, "广告添加失败")
                    
            except ValueError as e:
                await self.send_error_message(
                    update,
                    f"格式错误：{str(e)}\n\n"
                    "正确格式示例：\n"
                    "欢迎语\n\n\n"
                    "广告语\n可以包含多行\n\n\n"
                    "按钮1|链接1;按钮2|链接2"
                )
            finally:
                # 清理临时数据
                context.user_data.pop('temp_ad', None)
                context.user_data['waiting_for_ad'] = False
    
    @admin_required
    async def handle_list_ads(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /list_ads 命令"""
        ads = await self.ad_service.get_all_ads()
        if not ads:
            await update.message.reply_text("📝 当前没有广告")
            return
            
        for ad in ads:
            # 格式化按钮信息
            buttons_info = "\n".join([
                f"- {btn['text']} -> {btn['url']}"
                for btn in ad.buttons
            ])
            
            message = (
                f"📢 广告\n"
                f"ID: {ad.id}\n"
                f"类型: {ad.media_type}\n"
                f"欢迎语: {ad.welcome_text}\n"
                f"广告语: {ad.ad_text}\n"
                f"按钮列表:\n{buttons_info}\n"
                f"创建时间: {ad.created_at.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            await update.message.reply_text(message)
            
        # 添加使用说明
        usage = (
            "💡 删除广告请使用：\n"
            "/delete_ad <广告ID>\n"
            "例如：/delete_ad 550e8400-e29b-41d4-a716-446655440000"
        )
        await update.message.reply_text(usage)
    
    @admin_required
    async def handle_delete_ad(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理 /delete_ad 命令"""
        if not context.args:
            await self.send_error_message(
                update,
                "请提供要删除的广告ID\n"
                "用法: /delete_ad <ad_id>\n"
                "提示：使用 /list_ads 查看所有广告及其ID"
            )
            return
            
        try:
            ad_id = context.args[0]
            if await self.ad_service.delete_ad(ad_id):
                await self.send_success_message(
                    update,
                    f"已删除广告 {ad_id}"
                )
            else:
                await self.send_error_message(
                    update,
                    f"删除广告失败：未找到ID为 {ad_id} 的广告"
                )
        except Exception as e:
            await self.send_error_message(
                update,
                f"删除广告时出错: {str(e)}"
            )