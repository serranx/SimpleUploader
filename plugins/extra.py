
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import os, re, random, string, json, requests
from bs4 import BeautifulSoup
from config import Config
from translation import Translation
from pyrogram import filters
from pyrogram import Client
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from helper_funcs.display_progress import ContentLength
from . import googledrive
from . import fembed
from . import mediafire
import lk21

@Client.on_message(filters.regex(pattern="drive.google.com"))
async def dl_googledrive(bot, message):
    custom_file_name = None
    info_msg = await message.reply_text(
        "<b>Processing...⏳</b>", 
        quote=True
    )
    if " * " in message.text:
        try:
            url, custom_file_name = message.text.split(" * ")
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
            Translation.NO_FILE_FOUND
        )
        return
    file_title = response_gd["title"]
    ext = response_gd["ext"]
    if custom_file_name is not None:
        if custom_file_name.endswith("." + ext):
            filename = custom_file_name
        else:
            filename = custom_file_name + "." + ext
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

@Client.on_message(filters.regex(pattern="fembed.com|fembed-hd.com|femax20.com|vanfem.com|suzihaza.com|embedsito.com|owodeuwu.xyz|plusto.link"))
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
        req = requests.get(url, stream=True)
        soup = BeautifulSoup(req.content, "html.parser")
        filename = soup.find("h1", class_="title").get_text()
        filename = filename.split("." + filename.split(".")[-1])[0]
        for item in response_fembed:
            filesize = ContentLength(item["value"])
            formats.append({
                "id": item_id,
                "title": filename,
                "format": item["key"].split("/")[0],
                "ext": item["key"].split("/")[1],
                "filesize": filesize,
                "url": item["value"]
            })
            item_id += 1
    except Exception as e:
        await info_msg.edit_text(
            Translation.NO_FILE_FOUND + "\n\n" + str(e)
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
                "🎥 video " + item["format"] + " " + item["filesize"],
                callback_data=(cb_string_video).encode("UTF-8")
            ),
            InlineKeyboardButton(
                "📄 file " + item["ext"] + " " + item["filesize"],
                callback_data=(cb_string_file).encode("UTF-8")
            )
        ])
    try:
        await info_msg.edit_text(
            Translation.FORMAT_SELECTION,
            reply_markup=InlineKeyboardMarkup(inline_keyboard)
        )
    except Exception as e:
        await info_msg.edit_text(
            str(e)
        )
        return
    
@Client.on_message(filters.regex(pattern="mediafire.com/"))
async def dl_mediafire(bot, message):
    custom_file_name = None
    info_msg = await message.reply_text(
        "<b>Processing... ⏳</b>",
        quote=True
    )
    if " * " in message.text:
        try:
            url, custom_file_name = message.text.split(" * ")
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
    if custom_file_name is not None:
        if "\n" in custom_file_name:
            filename = custom_file_name.split("\n")[0]
        if custom_file_name.endswith("." + ext):
            filename = custom_file_name
        else:
            filename = custom_file_name + "." + ext
    if ext in Config.VIDEO_FORMATS:
        send_type = "video"
    elif ext in Config.AUDIO_FORMATS:
        send_type = "audio"
    else:
        send_type = "file"
    message.data = "{}|{}|{}".format(send_type, dl_url, filename)
    await mediafire.download(bot, message, info_msg)