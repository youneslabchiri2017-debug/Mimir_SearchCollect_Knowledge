from ddgs import DDGS
from Project.Specific_Searcher.Utils.DBpedia_Searcher import DBpedia_Searcher
from Project.Specific_Searcher.Utils.WikiData_Searcher import WikiData_Searcher
from Project.Specific_Searcher.Utils.WikiPedia_Searcher import Wikipedia_Searcher
from Web_Searcher.Text_Searchers.General_Web_Searcher import General_Web_Searcher


class Category_Searcher():

    def __init__(self):
        self.wiki_searcher = WikiData_Searcher()
        self.dbpedia_searcher = DBpedia_Searcher()
        self.wikipedia_searcher = Wikipedia_Searcher()
        self.general_web_searcher = General_Web_Searcher()
        self.attributes_to_search = {}
        self.id_cat = None

    def __search_pages__(self, term, max_res=5):
        with DDGS() as ddgs:
            results = ddgs.text(term, max_results=max_res)
        return list(map(lambda x: x['href'], results))

    def search(self, term):
        for key in term.data:
            if self.id_cat == key.split('-')[0]:
                try:
                    term.data[key]['wikidata'] = self.wiki_searcher.search(term.term)
                except Exception as e:
                    print(e)
                try:
                    term.data[key]['dbpedia'] = self.dbpedia_searcher.search(term.term)
                except Exception as e:
                    print(e)
                try:
                    term.data[key]['wikipedia'] = self.wikipedia_searcher.search(term.term)
                except Exception as e:
                    print(e)
                try:
                    term.data[key]['web_search'] = self.general_web_searcher.search(term.term)
                except Exception as e:
                    print(e)

