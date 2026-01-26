from flags.handlers.sql import SQLiteTable
from typing import Dict, List
from flags.loggers import setup_logging

LOG = setup_logging(__name__)

class Data:
    def __init__(self,**fields):
        self._fields = fields

    def __getattr__(self,key : str):
        if key in self._fields:
            return self._fields[key]
        raise AttributeError()
    
    def __setattr__(self, key : str, value : object):
        if key != "_fields":
            self._fields[key] = value
        super().__setattr__(key, value)

    def __repr__(self):
        cls_name = self.__class__.__name__
        fields = ", ".join("%s=%r" % i for i in sorted(self._fields.items()))
        return f"{cls_name}({fields})"
    
    def __dir__(self):
        return dir(self.__class__) + list(self._fields)  
    
    def __iter__(self):
        # allow casting into a dict
        for field in self._fields:
            yield field, getattr(self, field)
        
    def fields(self):
        return self._fields

class Table:
    def __init__(self,filename : str):
        self.sql = SQLiteTable(filename,self.__class__.__name__)
        
        if isinstance(self.data_class,str):
            self.factory = type(self.data_class,(Data,),{})
        else:
            self.factory = self.data_class
        
    def _load(self):

        tree = getattr(self,'tree')
        if tree is None:
            raise NotImplementedError("self.tree not initialized")  
         
        keys = tree[0].keys()

        self.sql.create_table(keys)
        self.sql.insert_many(keys,tree)
    
    def get(self, *_, **kw) -> Data:
        if len(kw) != 1:
            raise TypeError("Only one criteria may be given")
        field, value = kw.popitem()
        if not isinstance(value, str):
            raise LookupError()
        
        res = self.sql.select_one_where(field,value)
        return self.factory(**res)