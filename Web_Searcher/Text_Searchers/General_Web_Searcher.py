from Web_Searcher.Text_Searchers.Text_Searcher import TextSearcher
from Web_Searcher.Transformers.HTML_Transformer import HTML_Transformer
from ddgs import DDGS

class General_Web_Searcher(TextSearcher):

    def __init__(self):
        TextSearcher.__init__(self)
        self.web_scrapper = HTML_Transformer()

    def __search_in_pages__(self, urls, term):
        tuples = []
        for url in urls:
            txt = self.web_scrapper.trasnform(url)
            if txt:
                tuples += self.ollama_transformer.transform(txt, term)
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