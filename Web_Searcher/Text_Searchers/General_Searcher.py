from Web_Searcher.Text_Searchers.Text_Searcher import TextSearcher
from Web_Searcher.Transformers.HTML_Transformer import HTML_Transformer

class General_Web_Searcher(TextSearcher):

    def __init__(self):
        super(TextSearcher, self).__init__()
        self.web_scrapper = HTML_Transformer()

    def __search_in_pages__(self, urls):
        t_txt = ""
        for url in self.urls:
            txt = self.web_scrapper.trasnform(url)
            if txt:
                t_txt += txt
        return self.transformer.trasnform(t_txt)

    def search(self, term):
        return []