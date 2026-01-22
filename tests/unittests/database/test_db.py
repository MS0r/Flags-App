import os
import pytest

from flags.database import db as db_mod
from flags.database import country as country_mod
import asyncio


def test_data_basic_behavior():
    d = db_mod.Data(name='Test', a=1, b=2)
    assert d.name == 'Test'
    assert d.a == 1
    # repr contains class and fields
    r = repr(d)
    assert 'Data' in r and 'a=1' in r
    # dir contains field names
    assert 'a' in dir(d)
    # iteration yields pairs
    items = dict(iter(d))
    assert items['name'] == 'Test' and items['b'] == 2


def test_country_missing_attr_returns_name_and_logs(caplog):
    c = country_mod.Country(name='Narnia')
    caplog.clear()
    # access a missing attribute -> should return the name and log a warning
    val = c.some_missing_attribute
    assert val == 'Narnia'
    assert any('not found' in rec.message for rec in caplog.records)


def test_database_load_and_get(monkeypatch, tmp_path):
    async def fake_get_flags():
        return [
            {'name': 'Testland', 'used': 'False', 'pop': '100'},
            {'name': 'Examplestan', 'used': 'False', 'pop': '200'},
        ]

    monkeypatch.setattr(country_mod.scrapper, 'get_flags', fake_get_flags)

    # instantiate Countries which will call _load in its __init__
    fname = str(tmp_path / 'flags.db')
    C = country_mod.Countries(fname)
    
    # get by name returns an object
    obj = C.get(name='Testland')
    assert obj is not None
    assert obj.name.lower() == 'testland'

    # get with missing should raise when not found (no default support)
    with pytest.raises(TypeError):
        C.get(name='Nope')

    # TypeError when passing more than one kw
    with pytest.raises(TypeError):
        C.get(name='a', population='b')

    # LookupError when non-string value
    with pytest.raises(LookupError):
        C.get(name=123)


def test_put_to_used_updates_and_saves(monkeypatch, tmp_path):
    # start with a single country inserted by scrapper.get_flags
    async def fake_get_flags():
        return [{'name': 'Testland', 'used': 'False', 'population': '100'}]

    monkeypatch.setattr(country_mod.scrapper, 'get_flags', fake_get_flags)

    fname = str(tmp_path / 'flags.db')
    C = country_mod.Countries(fname)

    # ensure initial used value
    assert C.get(name='Testland').used == 'False'

    C.put_to_used('Testland')

    # ensure DB was updated
    row = C.sql.select_one_where('name', 'Testland')
    assert row['used'] == 'True'
    # ensure in-memory object updated
    assert C.get(name='Testland').used == 'True'
