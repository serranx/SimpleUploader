
import requests
import asyncio
import aiohttp
import os
import time
import math
from datetime import datetime
from bs4 import BeautifulSoup
from config import Config
from translation import Translation
from plugins.custom_thumbnail import *
from helper_funcs.display_progress import progress_for_pyrogram, humanbytes, TimeFormatter

async def get(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.content, "html.parser")
    try:
	    dl_url = soup.find("a", class_="uk-button uk-button-danger").get("href")
    except:
    	try:
		    error_msg = soup.find("p", class_="uk-text-danger uk-text-center").get_text()
		    print(error_msg)
	    except Exception as e:
	    	print("Unknown error.\n"+str(e))
    filename = "test.mp4"
    print dl_url, filename