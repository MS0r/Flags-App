import types
import pytest

import flags.interface as interface_mod


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


class FakeTree:
	def __init__(self):
		self._rows = []
		self._next = 1
		self._selected = None

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

	def heading(self, *args, **kwargs):
		return None

	def move(self, *args, **kwargs):
		return None


def fake_image_open(path):
	class Ctx:
		def __enter__(self):
			return self

		def __exit__(self, exc_type, exc, tb):
			return False

		def resize(self, size):
			return "resized-image"

	return Ctx()


def test_put_all_items_populates_table_and_images(monkeypatch):
	# Replace Countries with a fake and use a fake Tree and image functions
	monkeypatch.setattr(interface_mod, 'Countries', FakeCountries)

	# Build a dummy instance (avoid Tkinter entirely)
	app = object.__new__(interface_mod.App)
	app.countries = FakeCountries()
	app.images = {}
	app.current_items = set()
	app.table = FakeTree()

	# Patch Image.open and ImageTk.PhotoImage used by put_all_items
	monkeypatch.setattr(interface_mod.Image, 'open', fake_image_open)
	monkeypatch.setattr(interface_mod.ImageTk, 'PhotoImage', lambda x: f"PHOTO-{x}")

	# Call the method
	interface_mod.App.put_all_items(app)

	# Assertions: images populated and table rows inserted
	assert len(app.images) == len(app.countries.get_names())
	assert len(app.table.get_children()) == len(app.countries.get_names())


def test_put_to_used_calls_countries_and_updates_table(monkeypatch):
	monkeypatch.setattr(interface_mod, 'Countries', FakeCountries)

	app = object.__new__(interface_mod.App)
	app.countries = FakeCountries()
	app.images = {}
	app.current_items = set()
	app.table = FakeTree()

	# Patch image handling
	monkeypatch.setattr(interface_mod.Image, 'open', fake_image_open)
	monkeypatch.setattr(interface_mod.ImageTk, 'PhotoImage', lambda x: f"PHOTO-{x}")

	# Populate the table (simulate put_all_items)
	interface_mod.App.put_all_items(app)

	children = app.table.get_children()
	assert children, "table should have rows"

	# Select first child and call put_to_used
	first = children[0]
	app.table.selection_set(first)

	# Replace search_function to avoid full GUI search behavior
	app.search_function = lambda *a, **k: None

	# Perform action
	interface_mod.App.put_to_used(app)

	# The fake Countries should have recorded the call
	assert app.countries.put_called, "put_to_used should have been called on Countries"
	# The selected row should have been removed
	assert first not in app.table.get_children()
