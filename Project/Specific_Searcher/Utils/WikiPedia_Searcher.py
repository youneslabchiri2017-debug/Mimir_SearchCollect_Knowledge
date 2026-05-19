import requests
from Web_Searcher.Text_Searchers.Text_Searcher import TextSearcher

class Wikipedia_Searcher(TextSearcher):

    def __init__(self):
        super().__init__()
        self.wikipedia_url = "https://query.wikidata.org/sparql"

    def __search_wikipedia_text_by_qid__(self, termino, qid, lang="en"):
        # Configurar un User-Agent es obligatorio por políticas de la API de Wikimedia
        headers = {
            'User-Agent': 'MiBotEducativo/1.0 (contacto@ejemplo.com)'
        }

        # PASO 1: Obtener el título de Wikipedia desde Wikidata
        wikidata_url = "https://www.wikidata.org/w/api.php"
        wd_params = {
            "action": "wbgetentities",
            "ids": qid,
            "props": "sitelinks/urls",
            "sitefilter": f"{lang}wiki",
            "format": "json"
        }

        wd_res = requests.get(wikidata_url, params=wd_params, headers=headers).json()

        try:
            # Extraer el título exacto de la página
            title = wd_res["entities"][qid]["sitelinks"][f"{lang}wiki"]["title"]
        except KeyError:
            return ""

        # PASO 2: Obtener el contenido de la Wikipedia
        wp_url = f"https://{lang}.wikipedia.org/w/api.php"
        wp_params = {
            "action": "query",
            "prop": "extracts",
            "titles": title,
            "explaintext": True,  # Devuelve texto plano en lugar de HTML
            "exintro": False,  # False para traer todo el texto, True para solo la intro
            "format": "json"
        }

        wp_res = requests.get(wp_url, params=wp_params, headers=headers).json()

        # La respuesta viene indexada por Page ID, así que tomamos el primer resultado
        pages = wp_res["query"]["pages"]
        page_id = next(iter(pages))

        return pages[page_id].get("extract", "No se pudo extraer el contenido.")

    def search(self, term, qid):
        return self.transformer.transform(self.__search_wikipedia_text_by_qid__(term, qid), term)

