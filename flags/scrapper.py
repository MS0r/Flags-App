import os
import io
import logging
from aiohttp import ClientSession
from PIL import Image
from bs4 import BeautifulSoup as b
from bs4.element import Tag
from flags.paths import FLAGS_PATH
from flags.loggers import setup_logging

LOG = setup_logging(__name__)

class Scrapper:

    def __init__(self,wikiurl : str,population_url : str,headers : dict):
        self.WIKIURL = wikiurl
        self.POPULATION_URL = population_url
        self.HEADERS = headers
        self.countries = {}

    def make_directory(self, path : str):
        if not os.path.exists(path):
            os.mkdir(path)

    async def _get_flag(self, name : str, args : dict, session : ClientSession):
        img_path = os.path.join(FLAGS_PATH,name + '.png')
        args.update({"img" : img_path, "used" : "False"})

        if not os.path.exists(img_path):  
            async with session.get(args["img_url"],headers=self.HEADERS) as r: 
                fil = io.BytesIO(await r.read())
                img = Image.open(fil)
                img.save(img_path)
                LOG.debug(f"Added flag for {name}")

    async def _get_flags(self,session : ClientSession):
        self.make_directory(FLAGS_PATH)
        
        for name, args in self.countries.items():
            await self._get_flag(name,args,session)

    async def _init_countries(self, session : ClientSession):
        if len(self.countries) == 0:
            async with session.get(self.POPULATION_URL, headers=self.HEADERS) as req:
                popcontent = await req.text()
            
            soup = b(popcontent,"lxml-xml")
            table : Tag = soup.find("table").find('tbody')
            for country_tag in table.find_all("tr"):
                namexml, popxml = country_tag.find_all("td",limit=2)
                if namexml.find("img") is None: continue
                name = namexml.find("a")['title']
                img = "http:%s" % (namexml.find("img")['src'])
                pop = popxml.text
                self.countries.update({name : {"img_url" : img, "pop" : pop}})

    async def get_flags(self):
        async with ClientSession() as session:
            await self._init_countries(session)
            await self._get_flags(session)
            return self.countries
