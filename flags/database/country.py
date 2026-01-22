import unicodedata
import asyncio

from typing import Set

from flags.scrapper import Scrapper
from flags.database.db import (Table, Data)
from flags.loggers import setup_logging
from flags.paths import FLAGS_PATH
from flags.req_conf import (WIKIURL, HEADERS, POPULATION_URL)

scrapper = Scrapper(WIKIURL,POPULATION_URL,FLAGS_PATH,HEADERS)

LOG = setup_logging(__name__)

def remove_accents(input_str : str):
    output_str = input_str
    if not input_str.isascii():
        nfkd_form = unicodedata.normalize('NFKD',input_str)
        output_str = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return output_str

class Country(Data):
    def __getattr__(self, key : str):
        if key in self._fields:
            return self ._fields[key]

        name = self._fields.get('name')
        if name is not None:
            warning_message = (f'Country {key} not found, Country name provided instead')
            LOG.warning(warning_message)
            return name
        raise AttributeError()

class Countries(Table):

    data_class = Country

    def __init__(self, filename : str):
        super().__init__(filename)
        self._load()

    def _load(self):
        tree = self.sql.select_all()
        if len(tree) == 0:
            self.tree = asyncio.run(scrapper.get_flags())
            super()._load()

    def get_names(self):
        return list(map(lambda x: x['name'],self.sql.select_columns(('name',))))

    def fuzzy_search(self,search : str) -> Set[str]:
        srch = remove_accents(search).lower()
        names = self.get_names()

        if srch == "":
            return set(names)
        
        costs = {}
        ifstarts = set()
        for name in names:
            country = remove_accents(name).lower()
            if country.startswith(srch):
                ifstarts.add(name)
                continue

            m = len(srch)
            n = len(country)
            zero = [0 for _ in range(m)]
            matrix = [[j for j in range(m)] if i == 0 else zero.copy() for i in range(n)]
            for i in range(n):
                matrix[i][0] = i

            for i in range(1,n):
                for j in range(1,m):
                    cost = 0 if country[i] == srch[j] else 1
                    matrix[i][j] = min(
                        matrix[i-1][j] + 1, #deletion
                        matrix[i][j-1] + 1, #Insertion
                        matrix[i-1][j-1] + cost #Substitution
                    )

                    if i > 1 and j > 1 and country[i] == srch[j-1] and country[i-1] == srch[j]: #Transpositions
                        matrix[i][j] = min(matrix[i][j], matrix[i-2][j-2] + cost)

            distance = matrix[n-1][m-1]

            if distance not in costs:
                costs[distance] = [name]
            else:
                costs[distance].append(name)
                
        minimum = min(list(costs.keys()))
        return set(costs[minimum]).union(ifstarts)
    
    def put_to_used(self,name : str):
        # update the underlying SQL row and the in-memory object
        # SQLiteTable.update_where_name expects keyword assignments directly;
        # pass the string value so the TEXT column is updated
        self.sql.update_where_name(name, used='True')
        self.get(name=name).used = "True"