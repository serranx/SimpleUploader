
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import os, re, random, string, json
from config import Config
# the Strings used for this "thing"
from translation import Translation
from pyrogram import filters
from database.adduser import AddUser
from pyrogram import Client as Clinton
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from . import googledrive
from . import mediafire
from . import fembed
#from . import dl_button
import lk21

@Clinton.on_message(filters.regex(pattern="drive.google\.com"))
async def dl_googledrive(bot, update):
    video_formats = ["mp4", "mkv", "webm", "avi", "wmv", "mov"]
    audio_formats = ["mp3", "m4a"]
    processing = await update.reply_text("<b>Processing... ⏳</b>", reply_to_message_id=update.message_id)
    if " * " in update.text:
        try:
            url, custom_filename = update.text.split(" * ")
        except:
            await bot.edit_message_text(
                text=Translation.INCORRECT_REQUEST,
                chat_id=update.chat.id,
                message_id=processing.message_id
            )
    else:
        url = update.text
    response_gd = await googledrive.get(bot, update, url)
    logger.info(response_gd)
    try:
        await update.reply_text(
            str(response_gd)
        )
    except Exception as e:
        await update.reply_text(
            str(e)
        )
    dl_link = response_gd["url"]
    dl_ext = response_gd["ext"]
    if custom_filename is not None:
        filename = custom_filename
    else:
        filename = response_gd["title"]
    if dl_ext in video_formats:
        send_type = "video"
    elif dl_ext in audio_formats:
        send_type = "audio"
    else:
        send_type = "file"
    update.data = "{}|{}|{}|{}".format(send_type, dl_link, dl_ext, filename)
    await processing.delete(True)
    await googledrive.download(bot, update)

@Clinton.on_message(filters.regex(pattern="fembed\.com|fembed-hd\.com|femax20\.com|vanfem\.com|suzihaza\.com|embedsito\.com|owodeuwu\.xyz|plusto\.link"))
async def dl_fembed(bot, update):
    processing = await update.reply_text(
        "<b>Processing... ⏳</b>", 
        reply_to_message_id=update.message_id
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
                "url": item["value"]
            })
            item_id += 1
    except:
        await bot.edit_message_text(
            chat_id=update.chat.id,
            message_id=processing.message_id,
            text="<b>I couldn't find any video 🤕</b>"
        )
        return False
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
    await processing.delete(True)
    try:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.FORMAT_SELECTION,
            reply_markup=InlineKeyboardMarkup(inline_keyboard),
            parse_mode="html",
            reply_to_message_id=update.message_id
        )
    except Exception as e:
        await bot.send_message(
            chat_id=update.chat.id,
            text=str(e)
        )
    
@Clinton.on_message(filters.regex(pattern="\.mediafire\.com/"))
async def dl_mediafire(bot, update):
    video_formats = ["mp4", "mkv", "webm", "avi", "wmv", "mov"]
    audio_formats = ["mp3", "m4a"]
    processing = await update.reply_text("<b>Processing... ⏳</b>", reply_to_message_id=update.message_id)
    if " * " in update.text:
      try:
        url, custom_filename = update.text.split(" * ")
      except:
        await bot.edit_message_text(
          text=Translation.INCORRECT_REQUEST,
          chat_id=update.chat.id,
          message_id=processing.message_id
        )
      if re.search("download[0-9]*\.mediafire\.com", url):
        url_parts = url.split("/")
        url = "https://www.mediafire.com/file/" + url_parts[-2] + "/" + url_parts[-1] + "/file"
      r = await mediafire.get(url)
      dl_link, filename = r.split("|")
      dl_ext = filename.split(".")[-1]
      filename = custom_filename
    else:
      url = update.text
      if re.search("download[0-9]*\.mediafire\.com", url):
        url_parts = url.split("/")
        url = "https://www.mediafire.com/file/" + url_parts[-2] + "/" + url_parts[-1] + "/file"
      r = await mediafire.get(url)
      dl_link, filename = r.split("|")
      dl_ext = filename.split(".")[-1]
    if dl_ext in video_formats:
      send_type = "video"
    elif dl_ext in audio_formats:
      send_type = "audio"
    else:
      send_type = "file"
    update.data = "{}|{}|{}|{}".format(send_type, dl_link, dl_ext, filename)
    await processing.delete(True)
    await mediafire.download(bot, update)
