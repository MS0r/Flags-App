import asyncio
from aiohttp import ClientSession
from bs4 import BeautifulSoup as b
from flags.loggers import setup_logging
from pathlib import Path

LOG = setup_logging(__name__)

class Scrapper:

    def __init__(self,wikiurl : str,population_url : str,flags_path : str,headers : dict):
        self.WIKIURL = wikiurl
        self.POPULATION_URL = population_url
        self.HEADERS = headers
        self.FLAGS_PATH = flags_path
        self.countries = []
        self._sem_limit = 10

    def make_directory(self, path: str):
        Path(path).mkdir(parents=True, exist_ok=True)

    async def _get_flag(self, name: str, origin_url: str, img_path: str, session: ClientSession, sem=None):
        try:
            async with (sem or asyncio.Semaphore(self._sem_limit)):
                async with session.get(origin_url, headers=self.HEADERS) as r:
                    r.raise_for_status()
                    data = await r.read()
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, Path(img_path).write_bytes, data)
            LOG.debug("Added flag for %s", name)
        except Exception as e:
            LOG.exception("Failed to get flag %s from %s: %s", name, origin_url, e)

    async def _init_countries(self, session: ClientSession):
        if self.countries:
            return
        try:
            async with session.get(self.POPULATION_URL, headers=self.HEADERS) as req:
                req_content = await req.text()
        except Exception as e:
            LOG.exception("Failed to fetch population page: %s", e)
            return

        soup = b(req_content, "lxml")
        tbody = soup.find("tbody")
        if not tbody:
            LOG.error("No tbody found on population page")
            return

        trs = tbody.find_all("tr")
        self.make_directory(self.FLAGS_PATH)

        tasks = []
        sem = asyncio.Semaphore(self._sem_limit)
        for country_tag in trs:
            tds = country_tag.find_all("td", limit=2)
            if len(tds) < 2:
                continue
            td1, td2 = tds
            img = td1.find("img")
            if img is None:
                continue
            a_tag = td1.find("a")
            name = a_tag["title"] if a_tag and a_tag.has_attr("title") else td1.get_text(strip=True)
            pop = td2.get_text(strip=True)
            img_path = str(Path(self.FLAGS_PATH) / f"{name}.png")
            origin_url = img.get("src")
            if origin_url and origin_url.startswith("//"):
                origin_url = f"http:{origin_url}"
            elif origin_url and origin_url.startswith("/"):
                origin_url = f"{self.WIKIURL.rstrip('/')}{origin_url}"
            country = {"name": name, "origin_url": origin_url, "pop": pop, "img_path": img_path, "used": "False"}
            self.countries.append(country)
            if origin_url and not Path(img_path).exists():
                tasks.append(self._get_flag(name, origin_url, img_path, session, sem))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def get_flags(self):
        async with ClientSession() as session:
            await self._init_countries(session)
        return self.countries
