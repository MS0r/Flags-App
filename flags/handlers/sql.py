import sqlite3
from sqlite3 import Cursor
from typing import List, Dict, Iterable, Set

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
    def table_exists(self, cursor : Cursor = None):
        res = cursor.execute("")

    @get_cursor
    def create_table(self,columns : Iterable,cursor : Cursor = None) -> None:
        """"Create a table with the name and the named columns in a iterable"""
        cols = ",".join(f"{c} TEXT" for c in columns)
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name}({cols})")

    @get_cursor
    def insert_many(self, columns : Iterable, values : List[Dict],cursor : Cursor = None) -> None:
        cols = ",".join(columns)
        params = ",".join(f":{c}" for c in columns)
        cursor.executemany(f"INSERT INTO {self.table_name}({cols}) VALUES({params})",values)

    @get_cursor
    def select_all(self, cursor: Cursor = None) -> List[Dict]:
        try:
            rows = cursor.execute(f"SELECT * FROM {self.table_name}").fetchall()
            return [dict(r) for r in rows]
        except:
            return []

    @get_cursor
    def select_columns(self,columns : Set[str] = ("*",), cursor : Cursor = None):
        rows = cursor.execute(f"SELECT {",".join(columns)} FROM {self.table_name}").fetchall()
        return [dict(r) for r in rows]

    @get_cursor
    def select_one_where(self, key : str, value : str, cursor : Cursor = None) -> Dict:
        row = cursor.execute(f"SELECT * FROM {self.table_name} WHERE {key}=?", (value,)).fetchone()
        return dict(row) if row is not None else None
    
    @get_cursor
    def update_where_name(self,name : str, cursor : Cursor = None, **kw):
        # quote string values so TEXT columns are updated correctly
        parts = []
        for k, v in kw.items():
            if isinstance(v, str):
                parts.append(f"{k}='{v}'")
            else:
                parts.append(f"{k}={v}")
        st = ",".join(parts)
        cursor.execute(f"UPDATE {self.table_name} SET {st} WHERE name='{name}'")
