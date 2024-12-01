from telegram import Update
from telegram.ext import ContextTypes
from src.api.handlers.base_handler import BaseHandler, admin_required
from src.services.banned_word_service import BannedWordService

class BannedWordHandler(BaseHandler):
    def __init__(self, application):
        super().__init__(application)
        self.banned_word_service = BannedWordService(self.repository)
    
    @admin_required
    async def handle_add_banned_word(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理添加禁言词命令"""
        if not context.args:
            await self.send_error_message(
                update,
                "请提供要禁用的关键词\n"
                "用法: /add_banned_word <关键词>"
            )
            return
        
        word = ' '.join(context.args).lower()
        if await self.banned_word_service.add_banned_word(word, update.effective_user.id):
            await self.send_success_message(update, f"已添加禁言词: {word}")
        else:
            await self.send_error_message(update, "添加禁言词失败")
    
    @admin_required
    async def handle_list_banned_words(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理列出禁言词命令"""
        banned_words = await self.banned_word_service.get_all_banned_words()
        if not banned_words:
            await update.message.reply_text("当前没有禁言词")
            return
        
        words_list = "\n".join([f"- {word.word}" for word in banned_words])
        await update.message.reply_text(
            f"📋 禁言词列表：\n{words_list}\n\n"
            "删除禁言词请使用：\n"
            "/delete_banned_word <关键词>"
        )
    
    @admin_required
    async def handle_delete_banned_word(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """处理删除禁言词命令"""
        if not context.args:
            await self.send_error_message(
                update,
                "请提供要删除的关键词\n"
                "用法: /delete_banned_word <关键词>"
            )
            return
        
        word = ' '.join(context.args).lower()
        if await self.banned_word_service.delete_banned_word(word):
            await self.send_success_message(update, f"已删除禁言词: {word}")
        else:
            await self.send_error_message(update, f"删除失败：未找到禁言词 {word}") 