
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


def fake_open(fil):
    class FakeImage:
        def save(self, path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'wb') as f:
                f.write(b'FAKEPNG')

    return FakeImage()


def test_get_flags_creates_entries_and_saves(tmp_path, monkeypatch):
    population_url = "https://example.com/pop"

    # Patch ClientSession, Image.open, and FLAGS_PATH used by the scrapper
    monkeypatch.setattr(scrapper_mod, "ClientSession", lambda: DummyClientSession(population_url))
    monkeypatch.setattr(scrapper_mod.Image, "open", fake_open)
    flags_path = tmp_path / "flags_dir"
    monkeypatch.setattr(scrapper_mod, "FLAGS_PATH", str(flags_path))

    s = Scrapper(wikiurl="http://unused", population_url=population_url, headers={})
    data = asyncio.run(s.get_flags())

    assert all([c in data for c in SAMPLE_COUNTRIES])
    td = data[SAMPLE_COUNTRIES[0]]
    assert td["img"].endswith(".png")
    assert td["img_url"].endswith(".svg.png")
    assert td["used"] == "False"
    # Fake save wrote the file
    assert os.path.exists(td["img"]) is True