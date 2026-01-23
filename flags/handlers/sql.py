import sqlite3
from sqlite3 import Cursor
from typing import List, Dict, Iterable, Set
from flags.loggers import setup_logging

LOG = setup_logging(__name__)

class SQLiteTable:
    def __init__(self,database, table_name):
        self._database = database
        self.table_name = table_name

    def get_cursor(fun):
        def wrapper(self,*args,**kwargs):
            db = self._database
            if db is not None:
                con = sqlite3.connect(db)
                con.row_factory = sqlite3.Row
                try:
                    with con:
                        return fun(self,cursor=con.cursor(),*args,**kwargs)
                finally:
                    con.close()
            else:
                raise AttributeError("filename Attr does not exists in the object")
        return wrapper

    @get_cursor
    def create_table(self,columns : Iterable,cursor : Cursor = None) -> None:
        try:
            cols = ",".join(f"{c} TEXT" for c in columns)
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name}({cols})")
        except Exception as e:
            LOG.error("Error on creating the new table: %s",e)

    @get_cursor
    def insert_many(self, columns : Iterable, values : List[Dict],cursor : Cursor = None) -> None:
        try:
            cols = ",".join(columns)
            params = ",".join(f":{c}" for c in columns)
            cursor.executemany(f"INSERT INTO {self.table_name}({cols}) VALUES({params})",values)
        except Exception as e:
            LOG.error("Error on inserting to the table: %s", e)

    @get_cursor
    def select_all(self, cursor: Cursor = None) -> List[Dict]:
        try:
            rows = cursor.execute(f"SELECT * FROM {self.table_name}").fetchall()
            return [dict(r) for r in rows]
        except Exception:
            LOG.warning("Table does not exists in the database")
            return []

    @get_cursor
    def select_columns(self,columns : Set[str] = ("*",), cursor : Cursor = None):
        try:
            rows = cursor.execute(f"SELECT {",".join(columns)} FROM {self.table_name}").fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            LOG.warning("Error retrieving the column %s from the table %s: %s",columns, self.table_name,e)
            return []

    @get_cursor
    def select_one_where(self, key : str, value : str, cursor : Cursor = None) -> Dict:
        try:
            row = cursor.execute(f"SELECT * FROM {self.table_name} WHERE {key}=?", (value,)).fetchone()
            return dict(row) if row is not None else None
        except Exception as e:
            LOG.error("Error retrieving an entry from the table %s: %s",self.table_name, e)
            return dict()
    
    @get_cursor
    def update_where_name(self,name : str, cursor : Cursor = None, **kw):
        parts = []
        for k, v in kw.items():
            if isinstance(v, str):
                parts.append(f"{k}='{v}'")
            else:
                parts.append(f"{k}={v}")
        st = ",".join(parts)
        try:
            cursor.execute(f"UPDATE {self.table_name} SET {st} WHERE name='{name}'")
        except Exception as e:
            LOG.error("Error updating the entry with name %s from the table %s: %s", name, self.table_name, e)
