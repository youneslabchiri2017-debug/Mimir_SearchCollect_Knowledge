from Project.Specific_Searcher.Category_Searchers.Category_Searcher import Category_Searcher

class Taxon_Searcher(Category_Searcher):

    def __init__(self):
        Category_Searcher.__init__(self)
        self.attributes_to_search[''] = ""
        self.id_cat = 'Q16521'

    def search(self, term):
        super().search(term)

    def __search_taxon__(self):
        pass