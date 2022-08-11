
import os
from pyrogram import filters
from pyrogram import Client as Clinton
from plugins.youtube_dl_button import youtube_dl_call_back
from plugins.dl_button import ddl_call_back
from . import fembed

@Clinton.on_callback_query(filters.regex('^X0$'))
async def delt(bot, update):
    await update.message.delete(True)

@Clinton.on_callback_query()
async def button(bot, update):
    cb_data = update.data
    if "|" in cb_data:
        if "fembed" in cb_data.split("|")[0]:
            await fembed.download(bot, update)
        else:
            await youtube_dl_call_back(bot, update)
    elif "=" in cb_data:
        await ddl_call_back(bot, update)