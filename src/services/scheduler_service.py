from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from src.services.ad_service import AdService
from src.services.message_service import MessageService
from src.utils.logger import log_info, log_error, log_warning
from src.repositories.data_repository import DataRepository

async def send_random_ad(context: ContextTypes.DEFAULT_TYPE) -> None:
    """定时发送随机广告到所有广告群"""
    try:
        # 创建新的 data_manager 实例
        data_manager = DataRepository(context.application)
        ad_service = AdService(data_manager)
        message_service = MessageService(data_manager)

        # 获取随机广告
        ad = await ad_service.get_random_ad()
        if not ad:
            log_info("没有可用的广告")
            return

        # 获取所有广告群
        ad_groups = await message_service.get_ad_groups()
        if not ad_groups:
            log_warning("没有广告投放群组")
            return

        # 创建广告按钮，每行两个按钮
        keyboard = []
        row = []
        for i, button in enumerate(ad.buttons):
            row.append(InlineKeyboardButton(button['text'], url=button['url']))
            # 每两个按钮或最后一个按钮时，添加到键盘
            if len(row) == 2 or i == len(ad.buttons) - 1:
                keyboard.append(row)
                row = []
        reply_markup = InlineKeyboardMarkup(keyboard)

        # 向每个广告群发送广告
        for group in ad_groups:
            try:
                # 根据媒体类型发送不同的消息
                if ad.media_type == 'photo':
                    await context.bot.send_photo(
                        chat_id=group.id,
                        photo=ad.media_id,
                        caption=ad.ad_text,
                        reply_markup=reply_markup
                    )
                elif ad.media_type == 'video':
                    await context.bot.send_video(
                        chat_id=group.id,
                        video=ad.media_id,
                        caption=ad.ad_text,
                        reply_markup=reply_markup
                    )
                
                log_info(f"成功发送广告到群组 {group.title} ({group.id})")
            except Exception as e:
                log_error(e, f"发送广告到群组 {group.title} ({group.id}) 失败")
                continue

    except Exception as e:
        log_error(e, "定时发送广告任务失败")


async def send_next_ad(context: ContextTypes.DEFAULT_TYPE) -> None:
    """定时发送随机广告到所有广告群"""
    try:
        # 创建新的 data_manager 实例
        data_manager = DataRepository(context.application)
        ad_service = AdService(data_manager)
        message_service = MessageService(data_manager)

        # 获取下一个广告
        ad = await ad_service.get_next_ad()
        if not ad:
            log_info("没有可用的广告")
            return

        # 获取所有广告群
        ad_groups = await message_service.get_ad_groups()
        if not ad_groups:
            log_warning("没有广告投放群组")
            return

        # 创建广告按钮，每行两个按钮
        keyboard = []
        row = []
        for i, button in enumerate(ad.buttons):
            row.append(InlineKeyboardButton(button['text'], url=button['url']))
            # 每两个按钮或最后一个按钮时，添加到键盘
            if len(row) == 2 or i == len(ad.buttons) - 1:
                keyboard.append(row)
                row = []
        reply_markup = InlineKeyboardMarkup(keyboard)

        # 向每个广告群发送广告
        for group in ad_groups:
            try:
                # 根据媒体类型发送不同的消息
                if ad.media_type == 'photo':
                    await context.bot.send_photo(
                        chat_id=group.id,
                        photo=ad.media_id,
                        caption=ad.ad_text,
                        reply_markup=reply_markup
                    )
                elif ad.media_type == 'video':
                    await context.bot.send_video(
                        chat_id=group.id,
                        video=ad.media_id,
                        caption=ad.ad_text,
                        reply_markup=reply_markup
                    )
                
                log_info(f"成功发送广告到群组 {group.title} ({group.id})")
            except Exception as e:
                log_error(e, f"发送广告到群组 {group.title} ({group.id}) 失败")
                continue

    except Exception as e:
        log_error(e, "定时发送广告任务失败")