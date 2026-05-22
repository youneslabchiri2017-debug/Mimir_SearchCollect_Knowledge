import requests
from Project.Specific_Searcher.Category_Searchers.Category_Searcher import Category_Searcher

class Country_Searcher(Category_Searcher):

    def __init__(self):
        Category_Searcher.__init__(self)
        self.attributes_to_search[''] = ""
        self.id_cat = 'Q6256'
        self.base_url = "https://restcountries.com/v3.1/name/"

    def search(self, term):
        super().search(term)

    def __search_place__(self):
        pass

    def special_search(self, term):
        country_name = term.term
        triples = []
        try:
            # Pedimos la info (usamos fullText=true para evitar confusiones)
            response = requests.get(f"{self.base_url}{country_name}?fullText=true")
            if response.status_code != 200:
                return []

            data = response.json()[0]
            name = data['name']['common']

            # 1. Datos Geográficos y Políticos
            triples.append([name, "has_official_name", data['name']['official']])
            triples.append([name, "is_in_region", data.get('region')])
            triples.append([name, "is_in_subregion", data.get('subregion')])

            for cap in data.get('capital', []):
                triples.append([name, "has_capital", cap])

            for cont in data.get('continents', []):
                triples.append([name, "is_located_in", cont])

            # 2. Datos Demográficos y Físicos
            triples.append([name, "has_population", data.get('population')])
            triples.append([name, "has_area_km2", data.get('area')])
            triples.append([name, "drives_on_side", data.get('car', {}).get('side')])

            # 3. Idiomas y Monedas (Dinámico)
            for lang in data.get('languages', {}).values():
                triples.append([name, "has_language", lang])

            for curr in data.get('currencies', {}).values():
                triples.append([name, "uses_currency", f"{curr.get('name')} ({curr.get('symbol')})"])

            # 4. Fronteras (Borders)
            for border in data.get('borders', []):
                triples.append([name, "borders_with", border])

            # 5. Extras (Internet y Telefonía)
            for tld in data.get('tld', []):
                triples.append([name, "has_internet_tld", tld])

            triples.append([name, "has_calling_code", data.get('idd', {}).get('root', '') +
                            "".join(data.get('idd', {}).get('suffixes', []))])

            return triples
        except Exception as e:
            print(f"Error: {e}")
            return []