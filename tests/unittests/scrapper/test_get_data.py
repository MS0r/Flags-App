
import asyncio
from unittest import mock

import pytest

from src.urls import POPULATION_URL, WIKIURL, HEADERS
from src.scrapper import get_data

M_PATH = "src.scrapper.get_data"

class TestScrapper:
    @pytest.fixture
    def scrapper():
        return get_data.Scrapper()
        pass
    
    def test_get_flags(scrapper):
        pass