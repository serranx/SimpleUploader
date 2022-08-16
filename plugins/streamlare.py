
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
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
        }
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    #dl_url = soup.find_all("https://larecontent.com/download").get("href")
    dl_url = soup.find_all("https://larecontent.com/download")
    filename = "idjfbxno"
    return "{}|{}".format(dl_url, filename)