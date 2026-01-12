import requests
import os
import re
import io
import asyncio
import logging
import json
from aiohttp import ClientSession
from PIL import Image
from bs4 import BeautifulSoup as b
from bs4.element import Tag
from datetime import datetime
from src.paths import FLAGS_PATH

LOG = logging.getLogger(__name__)

class Scrapper():

    def __init__(self,wikiurl : str,population_url : str,headers : dict):
        self.WIKIURL = wikiurl
        self.POPULATION_URL = population_url
        self.HEADERS = headers

    async def make_directory(path : str):
        if not os.path.exists(path):
            os.mkdir(path)

    async def _get_flag(self, name : str, args : dict, session : ClientSession):
        try:
            img_path = os.path.join(FLAGS_PATH,name + '.png')
            args.update({"img" : img_path, "used" : "False"})

            if not os.path.exists(img_path):  
                async with session.get(args["img_url"],headers=self.HEADERS) as r: 
                    fil = io.BytesIO(await r.read())
                    img = Image.open(fil)
                    img.save(img_path)
                    LOG.debug(f"Added flag for {name}")
        except Exception as e:
            raise e 

    async def _get_flags(self,session : ClientSession):
        await self.make_directory(FLAGS_PATH)

        for name, args in self.countries.items():
            try:
                await self._get_flag(name,args,session)
            except Exception as e:
                raise e

    async def _init_countries(self, session : ClientSession):
        async with session.get(self.POPULATION_URL) as req:
            popcontent = await req.text()
        
        soup = b(popcontent,"lxml")
        table : Tag = soup.find("table")
        self.countries = {}
        for pop_xml in table.find_all("tr"):
            namexml, popxml = pop_xml.find_all("td",limit=2)
            name = namexml.find("img")['alt']
            img = "http:%s" % (namexml.find("img")['src'])
            pop = popxml.text
            self.countries.update({name : {"img_url" : img, "pop" : pop}})

    async def get_flags(self):
        async with ClientSession() as session:
            await self._init_countries(session)
            await self._get_flags(session)
            return self.countries
