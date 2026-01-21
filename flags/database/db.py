from typing import Dict, List
from flags.handlers import json
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

class Database:
    def __init__(self,filename : str):
        self.filename = filename

        if isinstance(self.data_class,str):
            self.factory = type(self.data_class,(Data,),{})
        else:
            self.factory = self.data_class

    def _clear(self):
        self.objects : List[Data] = []
        self.indices : Dict[str,Dict[str,Data]] = {}

    def _load(self):
        
        self._clear()
        tree = getattr(self,'tree')
        if tree is None:
            raise NotImplementedError("self.tree not initialized")

        for entry in tree:
            obj : Data = self.factory(**entry)
            dictionary = obj.fields()
            self.objects.append(obj)
            for key,value in dictionary.items():
                index = self.indices.setdefault(key, {})
                value = value
                if value in index:
                    LOG.warning(
                        "%s %r already taken in index %r and will be "
                        "ignored. This is an error in the databases."
                        % (self.factory.__name__, value, key)
                    )
                index[value] = obj
    
    def get(self, *, default = None, **kw) -> Data:
        if len(kw) != 1:
            raise TypeError("Only one criteria may be given")
        field, value = kw.popitem()
        if not isinstance(value, str):
            raise LookupError()
        
        value = value
        index = self.indices[field]
        try:
            return index[value]
        except KeyError:
            return default