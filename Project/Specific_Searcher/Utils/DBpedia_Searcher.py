import requests


class DBpedia_Searcher():

    def __get_knowledge_from_dbpedia__(self, term, qid):
        url = "https://dbpedia.org/sparql"

        # Modificamos la query añadiendo filtros estratégicos
        query = f"""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX wd: <http://www.wikidata.org/entity/>

        SELECT ?item ?property ?value ?propertyLabel ?valueLabel WHERE {{

          ?item owl:sameAs wd:{qid} .
          FILTER(CONTAINS(STR(?item), "dbpedia.org/resource"))

          ?item ?property ?value .

          # =========================================================================
          # FILTROS CRÍTICOS:
          # 1. Filtramos las propiedades para quedarnos SOLO con la ontología limpia (dbo:)
          #    Esto evita las propiedades brutas de las cajas infobox que vienen muy sucias.
          # 2. Excluimos explícitamente los enlaces estructurales de Wikipedia (wikiPageWikiLink)
          # =========================================================================
          FILTER(STRSTARTS(STR(?property), "http://dbpedia.org/ontology/"))
          FILTER(?property != <http://dbpedia.org/ontology/wikiPageWikiLink>)

          OPTIONAL {{
            ?property rdfs:label ?propertyLabel .
            FILTER(LANG(?propertyLabel) = "en")
          }}

          OPTIONAL {{
            ?value rdfs:label ?valueLabel .
            FILTER(LANG(?valueLabel) = "en")
          }}
        }}
        LIMIT 200
        """

        headers = {
            "Accept": "application/sparql-results+json",
            "User-Agent": "MySearchBot_1.0"
        }

        response = requests.get(url, params={"query": query}, headers=headers)

        if response.status_code != 200:
            return None

        json_data = response.json()

        if "results" not in json_data:
            return None

        data = []
        for line in json_data["results"]["bindings"]:
            # Si tiene label amigable en inglés la usamos, si no, limpiamos la URI
            if "propertyLabel" in line:
                prop = line["propertyLabel"]["value"]
            else:
                prop = line["property"]["value"].split("/")[-1]

            val = line.get("valueLabel", {}).get("value") or line["value"]["value"]
            data.append((term, prop, val))

        return data

    def search(self, term, qid):
        return self.__get_knowledge_from_dbpedia__(term, qid)