
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import os, re, random, string, json, requests
from bs4 import BeautifulSoup
from config import Config
from translation import Translation
from pyrogram import filters
from pyrogram import Client as Clinton
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from . import zplayer
from . import googledrive
from . import fembed
from . import mediafire
import lk21

@Clinton.on_message(filters.regex(pattern="slwatch.co"))
async def dl_streamlare(bot, message):
    custom_filename = None
    info_msg = await message.reply_text(
        "<b>Processing...⏳</b>", 
        quote=True
    )
    if " * " in message.text:
        try:
            url, custom_filename = message.text.split(" * ")
        except:
            await bot.edit_message_text(
                text=Translation.INCORRECT_REQUEST,
                chat_id=message.chat.id,
                message_id=info_msg.message_id
            )
            return
    else:
        url = message.text
    try:
        response_sl = await streamlare.get(url)
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=info_msg.message_id,
            text=str(response_sl)
        )
        return
    except Exception as e:
        await bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=info_msg.message_id,
            text=str(e)
        )
        return
    dl_url, file_title = response_sl.split("|")
    ext = "mp4"
    if custom_filename is not None:
        if custom_filename.endswith("." + ext):
            filename = custom_filename
        else:
            filename = custom_filename + "." + ext
    else:
        filename = file_title
    message.data = "{}|{}".format(dl_url, filename)
    await message.reply_text(dl_url, quote=True)
    #await streamlare.download(bot, message, info_msg)
    
@Clinton.on_message(filters.regex(pattern="drive.google.com"))
async def dl_googledrive(bot, message):
    custom_filename = None
    info_msg = await message.reply_text(
        "<b>Processing...⏳</b>", 
        quote=True
    )
    if " * " in message.text:
        try:
            url, custom_filename = message.text.split(" * ")
        except:
            await info_msg.edit_text(
                Translation.INCORRECT_REQUEST
            )
            return
    else:
        url = message.text
    if "folders" in url:
        await info_msg.edit_text(
            "<b>Sorry, but I can't upload folders 😕</b>"
        )
        return
    try:
        response_gd = await googledrive.get(url)
    except:
        await info_msg.edit_text(
            text=Translation.NO_FILE_FOUND
        )
        return
    file_title = response_gd["title"]
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
    message.data = "{}|{}|{}".format(send_type, url, filename)
    await googledrive.download(bot, message, info_msg)

@Clinton.on_message(filters.regex(pattern="fembed.com|fembed-hd.com|femax20.com|vanfem.com|suzihaza.com|embedsito.com|owodeuwu.xyz|plusto.link"))
async def dl_fembed(bot, message):
    info_msg = await message.reply_text(
        "<b>Processing... ⏳</b>", 
        quote=True
    )
    bypasser = lk21.Bypass()
    if " * " in message.text:
        url = message.text.split(" * ")[0]
        url = "https://fembed.com/f/" + url.split("/")[-1]
    else:
        url = message.text
        url = "https://fembed.com/f/" + url.split("/")[-1]
    response_fembed = bypasser.bypass_url(url)
    formats = []
    item_id = 0
    try:
        req = requests.get(url)
        soup = BeautifulSoup(req.content, 'html.parser')
        filename = soup.find("h1", class_="title").get_text()
        filename = filename.split("." + filename.split(".")[-1])[0]
        for item in response_fembed:
            formats.append({
                "id": item_id,
                "title": filename,
                "format": item["key"].split("/")[0],
                "ext": item["key"].split("/")[1],
                "url": item["value"]
            })
            item_id += 1
    except:
        await info_msg.edit_text(
            text=Translation.NO_FILE_FOUND
        )
        return
    inline_keyboard = []
    json_name = "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
    tmp_directory_for_each_user = Config.DOWNLOAD_LOCATION + str(message.from_user.id)
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
        await info_msg.edit_text(
            text=Translation.FORMAT_SELECTION,
            reply_markup=InlineKeyboardMarkup(inline_keyboard),
            parse_mode="html"
        )
    except Exception as e:
        await info_msg.delete(True)
        await message.reply_text(
            text=str(e),
            quote=True
        )
        return
    
@Clinton.on_message(filters.regex(pattern="mediafire.com/"))
async def dl_mediafire(bot, message):
    custom_filename = None
    info_msg = await message.reply_text(
        "<b>Processing... ⏳</b>",
        quote=True
    )
    if " * " in message.text:
        try:
            url, custom_filename = message.text.split(" * ")
        except:
            await info_msg.edit_text(
                Translation.INCORRECT_REQUEST
            )
            return
    else:
        url = message.text
    if re.search("download[0-9]*\.mediafire\.com", url):
        url_parts = url.split("/")
        url = "https://www.mediafire.com/file/" + url_parts[-2] + "/" + url_parts[-1] + "/file"
    if "?dkey=" in url:
        url = url.split("?dkey=")[0]
    try:
        dl_url, filename = await mediafire.get(url)
    except:
        await info_msg.edit_text(
            Translation.NO_FILE_FOUND
        )
        return
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
    message.data = "{}|{}|{}".format(send_type, dl_url, filename)
    await mediafire.download(bot, message, info_msg)