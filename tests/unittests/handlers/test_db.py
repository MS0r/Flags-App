import sqlite3
from flags.handlers.sql import SQLiteTable

def test_sqlite_table_basic(tmp_path):
    db = str(tmp_path / "test.db")
    table = SQLiteTable(db, "mytable")
    # create table and insert rows
    table.create_table(("name", "value"))
    table.insert_many(("name", "value"), [{"name": "a", "value": "1"}, {"name": "b", "value": "2"}])
    all_rows = table.select_all()
    assert len(all_rows) == 2
    assert set(r["name"] for r in all_rows) == {"a", "b"}
    cols = table.select_columns(("name",))
    assert set(r["name"] for r in cols) == {"a", "b"}
    one = table.select_one_where("name", "a")
    assert one["value"] == "1"
    table.update_where_name("a", value="9")
    one2 = table.select_one_where("name", "a")
    assert one2["value"] == "9"