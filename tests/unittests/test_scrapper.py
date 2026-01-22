
import asyncio
import os

import pytest

from flags.scrapper import Scrapper
import flags.scrapper as scrapper_mod
from tests.data.sample_page import SAMPLE_COUNTRIES

PATH = '/home/mickael/changes/Flags-App/tests/data/sample_page.html'

with open(PATH, "r", encoding="utf-8") as f:
    SAMPLE_HTML = f.read()


class DummyResponse:
    def __init__(self, text=None, data=None):
        self._text = text
        self._data = data or b''

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def raise_for_status(self):
        return None

    async def text(self):
        return self._text

    async def read(self):
        return self._data


class DummyClientSession:
    def __init__(self, population_url, img_bytes=b'PNGDATA'):
        self.population_url = population_url
        self.img_bytes = img_bytes

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    def get(self, url, headers=None):
        if url == self.population_url:
            return DummyResponse(text=SAMPLE_HTML)
        return DummyResponse(data=self.img_bytes)

def write_fake_bytes(self):
    os.makedirs(self, exist_ok=True)
    with self.open(mode='wb') as f:
        f.write(b'FAKEPNG')

def get_fake_running_loop():
    class FakeLoop:
        def __init__(self):
            pass

        async def run_in_executor(self,executor,func,*args):
            func(*args)

    return FakeLoop()


def test_get_flags_creates_entries_and_saves(tmp_path, monkeypatch):
    population_url = "https://example.com/pop"

    # Patch ClientSession, Image.open, and FLAGS_PATH used by the scrapper
    monkeypatch.setattr(scrapper_mod, "ClientSession", lambda: DummyClientSession(population_url))
    monkeypatch.setattr(scrapper_mod.asyncio, "get_running_loop", get_fake_running_loop)
    monkeypatch.setattr(scrapper_mod.Path,"write_bytes",write_fake_bytes) 
    flags_path = tmp_path / "flags_dir"

    s = Scrapper(wikiurl="http://unused", population_url=population_url,flags_path=str(flags_path),headers={})
    data = asyncio.run(s.get_flags())

    names = list(map(lambda x: x['name'],data))
    assert all([c in names for c in SAMPLE_COUNTRIES])
    sample0 = data[0]
    assert sample0["img_path"].endswith(".png")
    assert sample0["origin_url"].endswith(".svg.png")
    assert sample0["used"] == "False"
    # Fake save wrote the file
    assert os.path.exists(sample0["img_path"])