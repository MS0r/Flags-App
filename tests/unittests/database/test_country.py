import pytest

import flags.database.country as country_mod


def test_remove_accents_basic():
    assert country_mod.remove_accents('ascii') == 'ascii'
    assert country_mod.remove_accents('café') == 'cafe'
    assert country_mod.remove_accents('Áccénted') == 'Accented'


def make_sample():
    return [
        {'name': 'Testland', 'used': 'False', 'population': '100'},
        {'name': 'Examplestan', 'used': 'False', 'population': '200'},
        {'name': 'Áccénted', 'used': 'False', 'population': '50'},
    ]


def test_get_names_and_empty_fuzzy(monkeypatch, tmp_path):
    sample = make_sample()
    async def fake_get_flags():
        return sample

    monkeypatch.setattr(country_mod.scrapper, 'get_flags', fake_get_flags)
    fname = str(tmp_path / 'flags.db')
    C = country_mod.Countries(fname)

    names = C.get_names()
    assert set(names) == set(map(lambda x: x['name'],sample))

    # empty search returns all names
    res = C.fuzzy_search('')
    assert res == set(names)


def test_fuzzy_search_startswith_and_case_insensitive(monkeypatch, tmp_path):
    sample = make_sample()
    async def fake_get_flags():
        return sample

    monkeypatch.setattr(country_mod.scrapper, 'get_flags', fake_get_flags)

    C = country_mod.Countries(str(tmp_path / 'flags.db'))

    # startswith should match ignoring case
    assert 'Testland' in C.fuzzy_search('tes')
    assert 'Examplestan' in C.fuzzy_search('exam')


def test_fuzzy_search_handles_accents_and_transposition(monkeypatch, tmp_path):
    sample = make_sample()
    async def fake_get_flags():
        return sample

    monkeypatch.setattr(country_mod.scrapper, 'get_flags', fake_get_flags)

    C = country_mod.Countries(str(tmp_path / 'flags.db'))

    # Searching without accents should match accented name
    assert 'Áccénted' in C.fuzzy_search('accented')

    # transposition: tsetland vs testland should still find Testland
    assert 'Testland' in C.fuzzy_search('tsetland')
