import os
import pytest

from flags.database import db as db_mod
from flags.database import country as country_mod
import flags.handlers.json as handlers_json


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
    # prepare fake JSON structure returned by init_json_flags
    sample = {
        'Testland': {'used': 'False', 'pop': '100'},
        'Examplestan': {'used': 'False', 'pop': '200'},
    }

    monkeypatch.setattr(handlers_json, 'init_json_flags', lambda fn: sample)

    # instantiate Countries which will call _load in its __init__
    fname = str(tmp_path / 'flags.json')
    C = country_mod.Countries(fname)
    
    # Should have indices for fields
    assert 'name' in C.indices
    # get by name returns an object
    obj = C.get(name='Testland')
    assert obj is not None
    assert obj.name.lower() == 'testland'

    # get with missing returns default
    assert C.get(name='Nope', default=None) is None

    # TypeError when passing more than one kw
    with pytest.raises(TypeError):
        C.get(name='a', population='b')

    # LookupError when non-string value
    with pytest.raises(LookupError):
        C.get(name=123)


def test_put_to_used_updates_and_saves(monkeypatch, tmp_path):
    # initial json data
    data = {'Testland': {'used': 'False', 'population': '100'}}

    loaded = {}

    def fake_load(path):
        return data

    saved = {}

    def fake_save(path, d):
        # record what was saved
        saved['payload'] = d

    monkeypatch.setattr(handlers_json, 'load_json', fake_load)
    monkeypatch.setattr(handlers_json, 'save_json', fake_save)
    # ensure init_json_flags returns the same structure for _load
    monkeypatch.setattr(handlers_json, 'init_json_flags', lambda fn: data)

    fname = str(tmp_path / 'flags.json')
    C = country_mod.Countries(fname)

    # ensure initial used value
    assert C.get(name='Testland').used == 'False'

    C.put_to_used('Testland')

    # ensure save_json was called with updated data
    assert saved['payload']['Testland']['used'] == 'True'
    # ensure in-memory object updated
    assert C.get(name='Testland').used == 'True'
