import requests


class WikiData_Searcher():

    def __get_knowledge_from_wikidata__(self, term, qid):
        url = "https://query.wikidata.org/sparql"

        # Nueva Query SPARQL optimizada
        query = f"""
        SELECT ?propiedadNombre ?objeto ?objetoNombre ?objetoQID WHERE {{
          BIND(wd:{qid} AS ?item)

          ?item ?p ?objeto .

          # Obtener el nombre de la propiedad en inglés
          ?propiedad wikibase:directClaim ?p .
          ?propiedad rdfs:label ?propiedadNombre .
          FILTER(LANG(?propiedadNombre) = "en")

          # OPTIONAL: Intentamos buscar una etiqueta si el objeto es una entidad.
          OPTIONAL {{
            ?objeto rdfs:label ?objetoNombre .
            FILTER(LANG(?objetoNombre) = "en")
          }}

          # NUEVA LÓGICA: Extraer el QID directamente desde SPARQL
          # Si es una URI y empieza por la URL de entidades de Wikidata, corta el texto y extrae el QID.
          # Si es un texto puro (Literal) o una fecha, devolverá un texto vacío "".
          BIND(
            IF(
              isURI(?objeto) && STRSTARTS(STR(?objeto), "http://www.wikidata.org/entity/"), 
              STRAFTER(STR(?objeto), "http://www.wikidata.org/entity/"), 
              ""
            ) AS ?objetoQID
          )
        }}
        """

        headers = {
            "Accept": "application/sparql-results+json",
            "User-Agent": "MySearchBot_1.0"
        }
        response = requests.get(url, params={'query': query}, headers=headers)

        if response.status_code != 200:
            return []

        data = []
        for line in response.json()["results"]["bindings"]:
            prop_name = line["propiedadNombre"]["value"]

            # 1. Obtener el valor crudo del objeto (puede ser una URL de Wikidata o un texto)
            raw_objeto = line["objeto"]["value"]
            objeto_type = line["objeto"]["type"]  # "uri" o "literal"

            # 2. Analizar si es Entidad (URI) o Texto Puro (Literal)
            if objeto_type == "uri" and "www.wikidata.org/entity/" in raw_objeto:
                # Es una entidad de Wikidata. Extraemos su QID de la URL
                objeto_qid = raw_objeto.split("/")[-1]

                # Si tiene un nombre amigable (label), usamos su nombre, si no, el QID
                nombre_visible = line["objetoNombre"]["value"] if "objetoNombre" in line else objeto_qid

                # Guardamos una tupla identificable: (Sujeto, Propiedad, Valor, Tipo, QID_Asociado)
                data.append((term, prop_name, nombre_visible, "entity", objeto_qid))
            else:
                # Es un texto puro, una fecha, un número, etc.
                # Si por alguna razón tiene label usamos ese texto, si no el valor crudo
                texto_puro = line["objetoNombre"]["value"] if "objetoNombre" in line else raw_objeto

                data.append((qid, prop_name, texto_puro, "literal", None))

        return data

    def search(self, term, qid):
        return self.__get_knowledge_from_wikidata__(term, qid)