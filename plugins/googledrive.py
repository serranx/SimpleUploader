
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import sys, requests, urllib.parse, filetype, os, time, shutil, tldextract, asyncio, aiohttp, json, math
from config import Config
from datetime import datetime
from database.adduser import AddUser
from translation import Translation
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram import Client as Clinton
from database.access import clinton
from helper_funcs.display_progress import humanbytes
from helper_funcs.help_uploadbot import DownLoadFile
from helper_funcs.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from plugins.custom_thumbnail import *

async def get(url):
    if Config.HTTP_PROXY != "":
        command_to_exec = [
            "yt-dlp",
            "--no-warnings",
            "--youtube-skip-dash-manifest",
            "-j",
            url,
            "--proxy", Config.HTTP_PROXY
        ]
    else:
        command_to_exec = [
            "yt-dlp",
            "--no-warnings",
            "--youtube-skip-dash-manifest",
            "-j",
            url
        ]
    process = await asyncio.create_subprocess_exec(
        *command_to_exec,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    
    x_reponse = t_response
    if "\n" in x_reponse:
        x_reponse, _ = x_reponse.split("\n")
    response_json = json.loads(x_reponse)
    title = response_json["title"]
    response_json = response_json["formats"][-1]
    response_json["title"] = title
    return response_json
        
async def download(bot, update):
    cb_data = update.data
    tg_send_type, youtube_dl_url, filename = cb_data.split("|")
    description = filename
    start = datetime.now()
    dl_info = await update.reply_text(
        text=Translation.DOWNLOAD_START.format(filename),
        reply_to_message_id=update.message_id
    )
    tmp_directory_for_each_user = Config.DOWNLOAD_LOCATION + str(update.chat.id)
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    download_directory = tmp_directory_for_each_user + "/" + filename
    command_to_exec = [
        "yt-dlp",
        "-c",
        "--max-filesize", str(Config.TG_MAX_FILE_SIZE),
        "--embed-subs",
        "-f", "source",
        "--hls-prefer-ffmpeg", youtube_dl_url,
        "-o", download_directory
    ]
    if Config.HTTP_PROXY != "":
        command_to_exec.append("--proxy")
        command_to_exec.append(Config.HTTP_PROXY)
    command_to_exec.append("--no-warnings")
    start = datetime.now()
    try:
        process = await asyncio.create_subprocess_exec(
            *command_to_exec,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except Exception as e:
        await update.reply_text(
            str(e)
        )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    e_response = stderr.decode().strip()
    t_response = stdout.decode().strip()
    #logger.info(e_response)
    #logger.info(t_response)
    ad_string_to_replace = "please report this issue on https://yt-dl.org/bug . Make sure you are using the latest version; see  https://yt-dl.org/update  on how to update. Be sure to call youtube-dl with the --verbose flag and include its complete output."
    if e_response and ad_string_to_replace in e_response:
        error_message = e_response.replace(ad_string_to_replace, "")
        await bot.edit_message_text(
            chat_id=update.chat.id,
            message_id=dl_info.message_id,
            text=error_message
        )
        return False
    if t_response:
        # logger.info(t_response)
        end_one = datetime.now()
        time_taken_for_download = (end_one -start).seconds
        file_size = Config.TG_MAX_FILE_SIZE + 1
        try:
            file_size = os.stat(download_directory).st_size
        except FileNotFoundError as exc:
            download_directory = os.path.splitext(download_directory)[0] + "." + "mkv"
            file_size = os.stat(download_directory).st_size
        if file_size > Config.TG_MAX_FILE_SIZE:
            await bot.edit_message_text(
                chat_id=update.chat.id,
                text=Translation.RCHD_TG_API_LIMIT.format(time_taken_for_download, humanbytes(file_size)),
                message_id=dl_info.message_id
            )
        else:
            await bot.edit_message_text(
                text=Translation.UPLOAD_START,
                chat_id=update.chat.id,
                message_id=dl_info.message_id
            )
            # ref: message from @Sources_codes
            start_time = time.time()
            # try to upload file
            if tg_send_type == "audio":
                duration = await Mdata03(download_directory)
                thumbnail = await Gthumb01(bot, update)
                await bot.send_audio(
                    chat_id=update.chat.id,
                    audio=download_directory,
                    caption=description,
                    parse_mode="HTML",
                    duration=duration,
                    thumb=thumbnail,
                    reply_to_message_id=update.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update,
                        custom_file_name,
                        start_time
                    )
                )
            elif tg_send_type == "file":
                thumbnail = await Gthumb01(bot, update)
                await bot.send_document(
                    chat_id=update.chat.id,
                    document=download_directory,
                    thumb=thumbnail,
                    caption=description,
                    parse_mode="HTML",
                    reply_to_message_id=update.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update,
                        custom_file_name,
                        start_time
                    )
                )
            elif tg_send_type == "vm":
                width, duration = await Mdata02(download_directory)
                thumbnail = await Gthumb02(bot, update, duration, download_directory)
                await bot.send_video_note(
                    chat_id=update.chat.id,
                    video_note=download_directory,
                    duration=duration,
                    length=width,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update,
                        custom_file_name,
                        start_time
                    )
                )
            elif tg_send_type == "video":
                 width, height, duration = await Mdata01(download_directory)
                 thumbnail = await Gthumb02(bot, update, duration, download_directory)
                 await bot.send_video(
                    chat_id=update.chat.id,
                    video=download_directory,
                    caption=description,
                    parse_mode="HTML",
                    duration=duration,
                    width=width,
                    height=height,
                    thumb=thumbnail,
                    supports_streaming=True,
                    reply_to_message_id=update.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        update,
                        custom_file_name,
                        start_time
                    )
                )
            else:
                logger.info("Did this happen? :\\")
            end_two = datetime.now()
            time_taken_for_upload = (end_two - end_one).seconds
            try:
                os.remove(download_directory)
                os.remove(thumbnail)
            except:
                pass
            await bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(time_taken_for_download, time_taken_for_upload),
                chat_id=update.chat.id,
                message_id=dl_info.message_id,
                disable_web_page_preview=True
            )
            logger.info("✅ " + filename)
            logger.info("✅ Downloaded in: " + str(time_taken_for_download))
            logger.info("✅ Uploaded in: " + str(time_taken_for_upload))

