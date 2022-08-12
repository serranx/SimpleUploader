
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import os
from config import Config
from translation import Translation
from pyrogram import filters
from database.adduser import AddUser
from pyrogram import Client as Clinton
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@Clinton.on_message(filters.private & filters.command(["test"]))
async def test(bot, update):
    path = Config.DOWNLOAD_LOCATION + str(update.chat.id) + "/"
    try:
        files = os.listdir(path)
        joined_files = "\n".join(files)
        await bot.send_message(
            chat_id=update.chat.id,
            text=str(joined_files),
            parse_mode="html",
            reply_to_message_id=update.message_id
        )
    except:
        await bot.send_message(
            chat_id=update.chat.id,
            text="No files found.",
            parse_mode="html",
            reply_to_message_id=update.message_id
        )
        
@Clinton.on_message(filters.private & filters.command(["cancel"]))
async def cancel_process(bot, update):
    save_ytdl_json_path = Config.DOWNLOAD_LOCATION + str(update.chat.id) + ".json"
    if os.path.exists(save_ytdl_json_path):
        os.remove(save_ytdl_json_path)
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.PROCESS_CANCELLED,
            parse_mode="html",
            disable_web_page_preview=True,
            reply_to_message_id=update.message_id
        )
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.NO_PROCESS_FOUND,
            parse_mode="html",
            disable_web_page_preview=True,
            reply_to_message_id=update.message_id
        )

@Clinton.on_message(filters.private & filters.reply & filters.text)
async def edit_caption(bot, update):
    try:
        await bot.send_cached_media(
            chat_id=update.chat.id,
            file_id=update.reply_to_message.video.file_id,
            reply_to_message_id=update.message_id,
            caption=update.text
        )
    except:
        try:
            await bot.send_cached_media(
                chat_id=update.chat.id,
                file_id=update.reply_to_message.audio.file_id,
                reply_to_message_id=update.message_id,
                caption=update.text
            )
        except:
            try:
                await bot.send_cached_media(
                    chat_id=update.chat.id,
                    file_id=update.reply_to_message.document.file_id,
                    reply_to_message_id=update.message_id,
                    caption=update.text
                )
            except:
                pass

@Clinton.on_message(filters.private & filters.command(["help"]))
async def help_user(bot, update):
    await AddUser(bot, update)
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.HELP_USER,
        parse_mode="html",
        disable_web_page_preview=True,
        reply_to_message_id=update.message_id
    )

@Clinton.on_message(filters.private & filters.command(["addcaption"]))
async def add_caption_help(bot, update):
    await AddUser(bot, update)
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.ADD_CAPTION_HELP,
        parse_mode="html",
        reply_to_message_id=update.message_id
    )

@Clinton.on_message(filters.private & filters.command(["start"]))
async def start(bot, update):
    await AddUser(bot, update)
    await bot.send_message(
        chat_id=update.chat.id,
        text=Translation.START_TEXT.format(update.from_user.first_name),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Source code ⚡", url="https://github.com/wywxz/SimpleUploaderBot"),
                    InlineKeyboardButton("Developer 👨‍⚖️", url="https://t.me/SimpleBotsX"),
                ],
            ]
        ),
        reply_to_message_id=update.message_id
    )
