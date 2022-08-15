
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import os, re, random, string, json
from config import Config
from translation import Translation
from pyrogram import filters
from pyrogram import Client as Clinton
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from . import googledrive
from . import fembed
from . import mediafire
import lk21

@Clinton.on_message(filters.regex(pattern="drive\.google\.com"))
async def dl_googledrive(bot, update):
    custom_filename = None
    msg_info = await update.reply_text(
        "<b>Processing... ⏳</b>", 
        quote=True
    )
    if " * " in update.text:
        try:
            url, custom_filename = update.text.split(" * ")
        except:
            await bot.edit_message_text(
                text=Translation.INCORRECT_REQUEST,
                chat_id=update.chat.id,
                message_id=msg_info.message_id
            )
            return False
    else:
        url = update.text
    if "folders" in url:
        await bot.edit_message_text(
            text="<b>Sorry, but I can't upload folders 😕</b>",
            chat_id=update.chat.id,
            message_id=msg_info.message_id
        )
        return
    try:
        response_gd = await googledrive.get(url)
    except:
        await bot.edit_message_text(
            chat_id=update.chat.id,
            message_id=msg_info.message_id,
            text=Translation.NO_FILE_FOUND
        )
        return
    file_title = response_gd["title"]
    dl_url = response_gd["url"]
    ext = response_gd["ext"]
    if custom_filename is not None:
        if custom_filename.endswith("." + ext):
            filename = custom_filename
        else:
            filename = custom_filename + "." + ext
    else:
        filename = file_title
    if ext in Config.VIDEO_FORMATS:
        send_type = "video"
    elif ext in Config.AUDIO_FORMATS:
        send_type = "audio"
    else:
        send_type = "file"
    update.data = "{}|{}|{}".format(send_type, url, filename)
    #await processing.delete(True)
    await googledrive.download(bot, update, msg_info)

@Clinton.on_message(filters.regex(pattern="fembed\.com|fembed-hd\.com|femax20\.com|vanfem\.com|suzihaza\.com|embedsito\.com|owodeuwu\.xyz|plusto\.link"))
async def dl_fembed(bot, update):
    processing = await update.reply_text(
        "<b>Processing... ⏳</b>", 
        quote=True
    )
    bypasser = lk21.Bypass()
    if " * " in update.text:
        url = update.text.split(" * ")[0]
        url = "https://fembed.com/f/" + url.split("/")[-1]
    else:
        url = update.text
        url = "https://fembed.com/f/" + url.split("/")[-1]
    response_fembed = bypasser.bypass_url(url)
    formats = []
    item_id = 0
    try:
        for item in response_fembed:
            formats.append({
                "id": item_id,
                "ext": item["key"].split("/")[1],
                "format": item["key"].split("/")[0],
                "url": item["value"],
            })
            item_id += 1
    except:
        await bot.edit_message_text(
            chat_id=update.chat.id,
            message_id=processing.message_id,
            text=Translation.NO_FILE_FOUND
        )
        return
    inline_keyboard = []
    json_name = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    tmp_directory_for_each_user = Config.DOWNLOAD_LOCATION + str(update.from_user.id)
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    save_ytdl_json_path = tmp_directory_for_each_user + "/" + json_name + ".json"
    with open(save_ytdl_json_path, "w", encoding="utf8") as outfile:
        json.dump(formats, outfile, ensure_ascii=False)
    for item in formats:
        cb_string_video = "{}|{}|{}|{}".format("fembed", "video", item["id"], json_name)
        cb_string_file = "{}|{}|{}|{}".format("fembed", "file", item["id"], json_name)
        inline_keyboard.append([
            InlineKeyboardButton(
                "🎥 video " + item["format"],
                callback_data=(cb_string_video).encode("UTF-8")
            ),
            InlineKeyboardButton(
                "📄 file " + item["ext"],
                callback_data=(cb_string_file).encode("UTF-8")
            )
        ])
    try:
        await bot.edit_message_text(
            chat_id=update.chat.id,
            message_id=processing.message_id,
            text=Translation.FORMAT_SELECTION,
            reply_markup=InlineKeyboardMarkup(inline_keyboard),
            parse_mode="html"
        )
    except Exception as e:
        await update.reply_text(
            text=str(e),
            quote=True
        )
        return
    
@Clinton.on_message(filters.regex(pattern="mediafire\.com/"))
async def dl_mediafire(bot, update):
    custom_filename = None
    msg_info = await update.reply_text(
        "<b>Processing... ⏳</b>",
        quote=True
    )
    if " * " in update.text:
        try:
            url, custom_filename = update.text.split(" * ")
        except:
            await bot.edit_message_text(
                text=Translation.INCORRECT_REQUEST,
                chat_id=update.chat.id,
                message_id=msg_info.message_id
            )
            return
    else:
        url = update.text
    if re.search("download[0-9]*\.mediafire\.com", url):
        url_parts = url.split("/")
        url = "https://www.mediafire.com/file/" + url_parts[-2] + "/" + url_parts[-1] + "/file"
    if "?dkey=" in url:
        url = url.split("?dkey=")[0]
    try:
        response_mf = await mediafire.get(url)
    except:
        await bot.edit_message_text(
            chat_id=update.chat.id,
            message_id=msg_info.message_id,
            text=Translation.NO_FILE_FOUND
        )
        return
    dl_url, filename = response_mf.split("|")
    ext = filename.split(".")[-1]
    if custom_filename is not None:
        if "\n" in custom_filename:
            filename = custom_filename.split("\n")[0]
        if custom_filename.endswith("." + ext):
            filename = custom_filename
        else:
            filename = custom_filename + "." + ext
    if ext in Config.VIDEO_FORMATS:
        send_type = "video"
    elif ext in Config.AUDIO_FORMATS:
        send_type = "audio"
    else:
        send_type = "file"
    update.data = "{}|{}|{}".format(send_type, dl_url, filename)
    await mediafire.download(bot, update, msg_info)