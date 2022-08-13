
from pyrogram import Client as Clinton
from pyrogram import filters
from config import Config
from database.access import clinton

@Clinton.on_message(filters.private & filters.command('total'))
async def stats(bot, update):
    if update.from_user.id != Config.OWNER_ID:
        return 
    total_users = await clinton.total_users_count()
    await update.reply_text(text=f"<b>Total users:</b> {total_users}", quote=True)
