import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
import sys, requests, urllib.parse, filetype, os, time, shutil, tldextract, asyncio, json, math
from config import Config
from database.adduser import AddUser
from translation import Translation
logging.getLogger("pyrogram").setLevel(logging.WARNING)
from pyrogram import filters
from pyrogram import Client as Clinton
from database.access import clinton
from helper_funcs.display_progress import humanbytes
from helper_funcs.help_uploadbot import DownLoadFile
from helper_funcs.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import UserNotParticipant

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
    if t_response:
        x_reponse = t_response
        if "\n" in x_reponse:
            x_reponse, _ = x_reponse.split("\n")
        response_json = json.loads(x_reponse)
        title = response_json["title"]
        response_json = response_json["formats"][-1]
        response_json["title"] = title
        logger.info(response_json)
        return response_json
        
async def download(bot, update):
    cb_data = update.data
    send_type, dl_link, filename = cb_data.split("|")
    description = filename
    start = datetime.now()
    dl_info = await bot.send_message(
        chat_id=update.chat.id,
        text="<b>Google Drive link detected...</b> ⌛",
        reply_to_message_id=update.message_id
    )
    tmp_directory_for_each_user = Config.DOWNLOAD_LOCATION + str(update.chat.id)
    if not os.path.isdir(tmp_directory_for_each_user):
        os.makedirs(tmp_directory_for_each_user)
    download_directory = tmp_directory_for_each_user + "/" + filename
    command_to_exec = []
    async with aiohttp.ClientSession() as session:
        c_time = time.time()
        try:
            await download_coroutine(
                bot,
                session,
                dl_link,
                download_directory,
                update.chat.id,
                dl_info.message_id,
                c_time
            )
        except asyncio.TimeoutError:
            await bot.edit_message_text(
                text=Translation.SLOW_URL_DECED,
                chat_id=update.chat.id,
                message_id=dl_info.message_id
            )
            return False
    if os.path.exists(download_directory):
        end_one = datetime.now()
        time_taken_for_download = (end_one - start).seconds
        await bot.edit_message_text(
            text=Translation.UPLOAD_START,
            chat_id=update.chat.id,
            message_id=dl_info.message_id
        )
        file_size = Config.TG_MAX_FILE_SIZE + 1
        try:
            file_size = os.stat(download_directory).st_size
        except FileNotFoundError as exc:
            download_directory = os.path.splitext(download_directory)[0] + "." + "mkv"
            # https://stackoverflow.com/a/678242/4723940
            file_size = os.stat(download_directory).st_size
        if file_size > Config.TG_MAX_FILE_SIZE:
            await bot.edit_message_text(
                chat_id=update.chat.id,
                text=Translation.RCHD_TG_API_LIMIT.format(time_taken_for_download, humanbytes(file_size)),
                message_id=dl_info.message_id
            )
        else:
            # ref: message from @SOURCES_CODES
            start_time = time.time()
            # try to upload file
            if send_type == "audio":
                duration = await Mdata03(download_directory)
                thumb_image_path = await Gthumb01(bot, update)
                await bot.send_audio(
                    chat_id=update.chat.id,
                    audio=download_directory,
                    caption=description,
                    duration=duration,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        dl_info,
                        filename,
                        start_time
                    )
                )
            elif send_type == "file":
                  thumb_image_path = await Gthumb01(bot, update)
                  await bot.send_document(
                    chat_id=update.chat.id,
                    document=download_directory,
                    thumb=thumb_image_path,
                    caption=description,
                    reply_to_message_id=update.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        dl_info,
                        filename,
                        start_time
                    )
                )
            elif send_type == "vm":
                width, duration = await Mdata02(download_directory)
                thumb_image_path = await Gthumb02(bot, update, duration, download_directory)
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
                        dl_info,
                        filename,
                        start_time
                    )
                )
            elif send_type == "video":
                width, height, duration = await Mdata01(download_directory)
                thumb_image_path = await Gthumb02(bot, update, duration, download_directory)
                await bot.send_video(
                    chat_id=update.chat.id,
                    video=download_directory,
                    caption=description,
                    duration=duration,
                    width=width,
                    height=height,
                    supports_streaming=True,
                    thumb=thumb_image_path,
                    reply_to_message_id=update.message_id,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Translation.UPLOAD_START,
                        dl_info,
                        filename,
                        start_time
                    )
                )
            end_two = datetime.now()
            try:
                os.remove(download_directory)
                os.remove(thumb_image_path)
            except:
                pass
            time_taken_for_upload = (end_two - end_one).seconds
            await bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG_WITH_TS.format(time_taken_for_download, time_taken_for_upload),
                chat_id=update.chat.id,
                message_id=dl_info.message_id,
                disable_web_page_preview=True
            )
            print(dl_info)
            logger.info("✅ " + filename)
            logger.info("✅ Downloaded in: " + str(time_taken_for_download))
            logger.info("✅ Uploaded in: " + str(time_taken_for_upload))
    else:
        await bot.edit_message_text(
            text=Translation.NO_VOID_FORMAT_FOUND.format("Incorrect Link"),
            chat_id=update.chat.id,
            message_id=dl_info.message_id,
            disable_web_page_preview=True
        )

async def download_coroutine(bot, session, url, file_name, chat_id, message_id, start):
    downloaded = 0
    display_message = ""
    async with session.get(url, timeout=Config.PROCESS_MAX_TIMEOUT) as response:
        total_length = int(response.headers["Content-Length"])
        content_type = response.headers["Content-Type"]
        if "text" in content_type and total_length < 500:
            return await response.release()
        with open(file_name, "wb") as f_handle:
            while True:
                chunk = await response.content.read(Config.CHUNK_SIZE)
                if not chunk:
                    break
                f_handle.write(chunk)
                downloaded += Config.CHUNK_SIZE
                now = time.time()
                diff = now - start
                if round(diff % 5.00) == 0 or downloaded == total_length:
                    percentage = downloaded * 100 / total_length
                    speed = downloaded / diff
                    elapsed_time = round(diff) * 1000
                    time_to_completion = round(
                        (total_length - downloaded) / speed) * 1000
                    estimated_total_time = elapsed_time + time_to_completion
                    try:
                        progress = "<b>Downloading to my server...</b> 📥\n[{0}{1}] {2}%\n📁 <i>{3}</i>\n\n".format(
                            ''.join(["●" for i in range(math.floor(percentage / 5))]),
                            ''.join(["○" for i in range(20 - math.floor(percentage / 5))]),
                            round(percentage, 2),
                            file_name.split("/")[-1]
                        )
                        current_message = progress + """🔹<b>Finished ✅:</b> {0} of {1}
 🔹<b>Speed 🚀:</b> {2}/s
🔹<b>Time left 🕒:</b> {3}

<i><b>Note: </b>fembed links are very slow, so be patient.</i>""".format(
                            humanbytes(downloaded),
                            humanbytes(total_length),
                            humanbytes(speed),
                            TimeFormatter(time_to_completion)
                        )
                        if current_message != display_message:
                            await bot.edit_message_text(
                                chat_id,
                                message_id,
                                text=current_message
                            )
                            display_message = current_message
                    except Exception as e:
                        logger.info(str(e))
                        pass
        return await response.release()