from Web_Searcher.Text_Searchers.Text_Searcher import TextSearcher
from Web_Searcher.Text_Transformers.HTML_Transformer import HTML_Transformer
from ddgs import DDGS
# Importamos las herramientas de concurrencia nativas de Python
from concurrent.futures import ThreadPoolExecutor, TimeoutError


class General_Web_Searcher(TextSearcher):

    def __init__(self):
        TextSearcher.__init__(self)
        self.web_scrapper = HTML_Transformer()

    def __search_in_pages__(self, urls, term, lim = 1):
        tuples = []
        texts = []

        # Creamos un pool de hilos para consultar las URLs en paralelo
        max_workers = len(urls) if urls else 1
        with ThreadPoolExecutor(max_workers=max_workers) as executor:

            # Lanzamos la ejecución de .trasnform(url) para todas las URLs simultáneamente
            futuros_mapeados = {
                executor.submit(self.web_scrapper.trasnform, url): url
                for url in urls
            }

            # Evaluamos los resultados aplicando el límite de tiempo
            for futuro in futuros_mapeados:
                url = futuros_mapeados[futuro]
                try:
                    # MÁXIMO 5 SEGUNDOS DE ESPERA POR PÁGINA
                    txt = futuro.result(timeout=5)
                    if txt:
                        texts.append(txt)
                except TimeoutError:
                     # Si la web no responde en 5s, saltamos aquí y la ignoramos
                    print(f"⏳ [Timeout] La página tardó más de 5s y fue omitida: {url}")
                    continue
                except Exception as e:
                    print(f"❌ Error al raspar la web {url}: {str(e)}")
                    continue

        # Una vez recolectados los textos que respondieron a tiempo, los procesa Ollama
        if len(texts) > 0:
            for text in texts:
                try:
                    if lim >= 1:
                        tuples += self.ollama_transformer.transform(text, term)
                        lim -= 1
                    else:
                        break
                except Exception as e:
                    print(f"❌ Error en Ollama_Transformer: {str(e)}")

        return tuples

    def seach_pages(self, term, max_res=5):
        excluded_sites = [
            "wikipedia.org",
            "facebook.com",
            "youtube.com",
            "twitter.com",
            "instagram.com"
        ]
        query_excluded = " ".join([f"-site:{site}" for site in excluded_sites])
        search_query = f"{term} {query_excluded}"
        with DDGS() as ddgs:
            results = ddgs.text(search_query, max_results=max_res)
        return list(map(lambda x: x['href'], results))

    def search(self, term, num_results=5):
        pages = self.seach_pages(term, num_results)
        tuples = self.__search_in_pages__(pages, term)
        return tuples