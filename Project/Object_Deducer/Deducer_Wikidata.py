import json
import os
import time

import requests
from Project.Object_Deducer.Deducer import Deducer

class Deducer_Wikidata(Deducer):

    def __init__(self):
        super().__init__()
        self.sparql_url = "https://query.wikidata.org/sparql"
        self.search_url = "https://www.wikidata.org/w/api.php"

        # Archivo para guardar lo que vamos aprendiendo
        self.cache_file = "wikidata_cache.json"
        self.cache = self.__load_cache__()

        # Identificarse correctamente evita bloqueos
        self.headers = {
            'User-Agent': 'MiBotEducativo/1.0 (contacto: y.lacbhiri@alumnos.upm.es)',
            'Accept': 'application/sparql-results+json'
        }

    def __load_cache__(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}

    def __save_cache__(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)

    def __search_entities__(self, term):
        params = {
            "action": "wbsearchentities",
            "language": "en",
            "format": "json",
            "search": term
        }
        try:
            response = requests.get(self.search_url, headers=self.headers, params=params)
            if response.status_code == 200:
                return [item['id'] for item in response.json().get('search', [])]
        except Exception as e:
            print(e)

        return []

    def __get_root_category__(self, qid):
        """Usa SPARQL para encontrar a qué ROOT_CLASS pertenece el QID."""
        # 1. Mirar en caché primero
        if qid in self.cache:
            return self.cache[qid]

        # 2. Si no está en caché, preguntar a Wikidata
        # Esta consulta busca si el objeto es instancia/subclase de nuestras raíces
        root_ids = " ".join([f"wd:{key}" for key in self.ROOT_CLASSES.keys()])

        query = f"""
        SELECT ?root WHERE {{
          VALUES ?root {{ {root_ids} }}
           wd:{qid} (wdt:P31|wdt:P279)* ?root .
        }}
        """

        try:
            response = requests.get(self.sparql_url, params={'query': query, "format": "json"}, headers=self.headers)

            '''
            if response.status_code == 429:  # Too many requests
                print("Esperando 5 segundos por límite de velocidad...")
                time.sleep(5)
                return self.__get_root_category__(qid)
            '''

            if response.status_code != 200:
                print(f"Error HTTP {response.status_code}: {response.text}")
                return None

            data = response.json()
            results = data.get('results', {}).get('bindings', [])

            if results:
                data = []
                for result in results:
                    root_qid = result['root']['value'].split('/')[-1]
                    data.append(f"{root_qid}-{qid}")
                self.cache[qid] = data
                return data

        except Exception as e:
            print(f"Error deduciendo {qid}: {e}")

        return None

    def deduce_object(self, term_obj):
        qids = self.__search_entities__(term_obj.term)
        found_categories = []
        for qid in qids:
            categorias = self.__get_root_category__(qid)
            if categorias:
                found_categories += categorias
        term_obj.set_categories(found_categories)
        self.__save_cache__()
        super().deduce_object(term_obj)