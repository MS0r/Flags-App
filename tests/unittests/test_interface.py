import types
import pytest

import flags.interface as interface_mod


# Dummy tkinter classes for testing
class DummyTk:
    def __init__(self):
        self.tk = self  # Self-reference for tkinter compatibility
        self._w = 'dummy_tk'


class DummyFrame:
    def __init__(self, master=None, **kwargs):
        self.master = master
        self.kwargs = kwargs
        self.tk = getattr(master, 'tk', None) if master else None
        self._w = f'dummy_frame_{id(self)}'
    
    def pack(self, **kwargs):
        pass
    
    def place(self, **kwargs):
        pass
    
    def update(self):
        pass
    
    def winfo_width(self):
        return 800
    
    def winfo_height(self):
        return 600


class DummyStringVar:
    def __init__(self):
        self._value = ""
    
    def get(self):
        return self._value
    
    def set(self, value):
        self._value = value


class DummyLabel:
    def __init__(self, master=None, **kwargs):
        self.master = master
        self.kwargs = kwargs
    
    def grid(self, **kwargs):
        pass


class DummyEntry:
    def __init__(self, master=None, **kwargs):
        self.master = master
        self.kwargs = kwargs
        self.textvariable = kwargs.get('textvariable')
    
    def grid(self, **kwargs):
        pass


class DummyButton:
    def __init__(self, master=None, **kwargs):
        self.master = master
        self.kwargs = kwargs
        self.command = kwargs.get('command')
    
    def grid(self, **kwargs):
        pass


class DummyTreeview:
    def __init__(self, master=None, **kwargs):
        self.master = master
        self.kwargs = kwargs
        self._rows = []
        self._next = 1
        self._selected = None
    
    def column(self, *args, **kwargs):
        pass
    
    def heading(self, *args, **kwargs):
        pass
    
    def pack(self, **kwargs):
        pass
    
    def insert(self, parent, index=0, image=None, values=None):
        iid = f"iid{self._next}"
        self._next += 1
        self._rows.append((iid, image, values))
        return iid
    
    def get_children(self):
        return [r[0] for r in self._rows]
    
    def set(self, child, col):
        for iid, image, values in self._rows:
            if iid == child:
                if col == 'flags':
                    return values[0]
        return ""
    
    def item(self, iid):
        for r in self._rows:
            if r[0] == iid:
                return {'values': r[2]}
        return {'values': []}
    
    def delete(self, iid):
        self._rows = [r for r in self._rows if r[0] != iid]
    
    def selection(self):
        return [self._selected] if self._selected else []
    
    def selection_set(self, iid):
        self._selected = iid
    
    def move(self, *args, **kwargs):
        pass


class FakeCountry:
    def __init__(self, name):
        self.img_path = f"/tmp/{name}.png"
        self.used = "False"
        self.pop = "123"


class FakeCountries:
    def __init__(self, json_path=None):
        self._names = ["testland", "examplestan"]
        self.put_called = []

    def get_names(self):
        return list(self._names)

    def get(self, name=None):
        return FakeCountry(name)

    def fuzzy_search(self, search):
        if not search:
            return set(self._names)
        return {n for n in self._names if search.lower() in n}

    def put_to_used(self, name):
        self.put_called.append(name)


def fake_image_open(path):
    class Ctx:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def copy(self):
            return self

        def thumbnail(self, size):
            return None

    return Ctx()


@pytest.fixture
def app(monkeypatch):
    # Patch tkinter classes with dummy implementations
    import tkinter as tk
    from tkinter import ttk
    
    monkeypatch.setattr(tk, 'Frame', DummyFrame)
    monkeypatch.setattr(tk, 'StringVar', DummyStringVar)
    monkeypatch.setattr(tk, 'Label', DummyLabel)
    monkeypatch.setattr(tk, 'Entry', DummyEntry)
    monkeypatch.setattr(tk, 'Button', DummyButton)
    monkeypatch.setattr(ttk, 'Treeview', DummyTreeview)
    
    # Use fake Countries and patch image handling
    monkeypatch.setattr(interface_mod, 'Countries', FakeCountries)
    monkeypatch.setattr(interface_mod.Image, 'open', fake_image_open)
    monkeypatch.setattr(interface_mod.ImageTk, 'PhotoImage', lambda x: f"PHOTO-{x}")

    # Create app instance with dummy tkinter classes
    app = object.__new__(interface_mod.App)
    app.countries = FakeCountries()
    app.images = {}
    app.current_items = set()
    app.table = DummyTreeview()
    # simple search var with get()
    app.search = DummyStringVar()

    return app


def test_init_sets_up_basic_attributes(monkeypatch):
    # Patch tkinter at module level before App uses it
    import tkinter as tk
    from tkinter import ttk
    import sys
    
    # Create a mock ttk module first
    mock_ttk = type(sys)('mock_ttk')
    mock_ttk.Treeview = DummyTreeview
    
    # Create a mock tk module
    mock_tk = type(sys)('mock_tk')
    mock_tk.Frame = DummyFrame
    mock_tk.StringVar = DummyStringVar
    mock_tk.Label = DummyLabel
    mock_tk.Entry = DummyEntry
    mock_tk.Button = DummyButton
    mock_tk.END = 'end'
    mock_tk.BOTH = 'both'
    mock_tk.Tk = DummyTk
    mock_tk.ttk = mock_ttk  # Add ttk as an attribute
    
    # Reload the module with mocked tkinter
    monkeypatch.setitem(sys.modules, 'tkinter', mock_tk)
    monkeypatch.setitem(sys.modules, 'tkinter.ttk', mock_ttk)
    
    # Reimport interface_mod to pick up the mocked tkinter
    import importlib
    importlib.reload(interface_mod)
    
    # Use fake Countries and patch image handling
    monkeypatch.setattr(interface_mod, 'Countries', FakeCountries)
    monkeypatch.setattr(interface_mod.Image, 'open', fake_image_open)
    monkeypatch.setattr(interface_mod.ImageTk, 'PhotoImage', lambda x: f"PHOTO-{x}")

    a = interface_mod.App(master=DummyTk(), heig=100, wid=100, flags_db=None)

    assert isinstance(a.countries, FakeCountries)
    assert isinstance(a.images, dict)
    assert isinstance(a.current_items, set)
    assert isinstance(a.search, DummyStringVar)


def test_put_all_items_populates_table_and_images(app):
    # Populate using the module method
    interface_mod.App.put_all_items(app)

    # images should be created and rows inserted for each country name
    assert len(app.images) == len(app.countries.get_names())
    assert len(app.table.get_children()) == len(app.countries.get_names())


def test_put_to_used_calls_countries_and_updates_table(app):
    # Populate table first
    interface_mod.App.put_all_items(app)

    children = app.table.get_children()
    assert children, "table should have rows"

    # Select first child and call put_to_used
    first = children[0]
    app.table.selection_set(first)

    # Avoid full GUI search behaviour by stubbing search_function
    app.search_function = lambda *a, **k: None

    interface_mod.App.put_to_used(app)

    # Countries should have recorded the call
    assert app.countries.put_called, "put_to_used should have been called on Countries"
    # Selected row should have been removed
    assert first not in app.table.get_children()


def test_search_function_filters_table(app):
    # Populate table
    interface_mod.App.put_all_items(app)

    # Ensure full set present initially
    children_before = app.table.get_children()
    assert len(children_before) == len(app.countries.get_names())

    # Search for substring that matches only one country
    app.search = types.SimpleNamespace(get=lambda: "exampl")
    interface_mod.App.search_function(app)

    children_after = app.table.get_children()
    assert len(children_after) == 1
    remaining = app.table.item(children_after[0])['values'][0]
    assert 'Examplestan' == remaining
