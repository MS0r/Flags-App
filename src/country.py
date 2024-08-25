from . import database
import unicodedata
import os
from . import json_data
from collections.abc import Set

cwd = os.getcwd()
dir_name = 'flags'

json_path = os.path.join(cwd,'used.json')

def remove_accents(input_str : str):
    output_str = input_str
    if not input_str.isascii():
        nfkd_form = unicodedata.normalize('NFKD',input_str)
        output_str = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return output_str

class Countries(database.Database):

    data_class = database.Country

    def __init__(self, filename : str):
        super().__init__(filename)
        self._load()

    def get_names(self):
        return [country for country in self.indices['name']]

    def fuzzy_search(self,search : str) -> Set[str]:
        srch = remove_accents(search).lower()
        if srch == "":
            return set(self.get_names())
        costs = {}
        ifstarts = set()
        for name in self.get_names():
            contry = remove_accents(name).lower()
            if contry.startswith(srch):
                ifstarts.add(name)
                continue

            m = len(srch)
            n = len(contry)
            zero = [0 for _ in range(m)]
            matrix = [[j for j in range(m)] if i == 0 else zero.copy() for i in range(n)]
            for i in range(n):
                matrix[i][0] = i

            for i in range(1,n):
                for j in range(1,m):
                    cost = 0 if contry[i] == srch[j] else 1
                    matrix[i][j] = min(
                        matrix[i-1][j] + 1, #deletion
                        matrix[i][j-1] + 1, #Insertion
                        matrix[i-1][j-1] + cost #Substitution
                    )

                    if i > 1 and j > 1 and contry[i] == srch[j-1] and contry[i-1] == srch[j]: #Transpositions
                        matrix[i][j] = min(matrix[i][j], matrix[i-2][j-2] + cost)

            distance = matrix[n-1][m-1]

            if distance not in costs:
                costs[distance] = [name]
            else:
                costs[distance].append(name)
                
        minimum = min(list(costs.keys()))
        return set(costs[minimum]).union(ifstarts)
    
    def put_to_used(self,name : str):
        data = json_data.load_json(self.filename)
        data[name]['used'] = "True"
        json_data.save_json(self.filename,data)
        self.get(name=name).used = "True"