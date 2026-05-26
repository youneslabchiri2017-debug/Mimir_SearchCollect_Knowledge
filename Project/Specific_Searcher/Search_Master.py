from Project.Filters.Knowledge_Filter import Knowledge_Filter
from Project.Knowledge_Combiner.Ontology_Master import Ontology_Master
from Project.Specific_Searcher.Category_Searchers.Taxon_Searcher import Taxon_Searcher
from Project.Specific_Searcher.Category_Searchers.Person_Searcher import Person_Searcher
from Project.Specific_Searcher.Category_Searchers.Country_Searcher import Country_Searcher


class SearchMaster():

    def __init__(self):
        # Searchers
        self.person_searcher = Person_Searcher()
        self.country_Searcher = Country_Searcher()
        self.taxon_searcher = Taxon_Searcher()
        # Filters
        self.filter = Knowledge_Filter()
        self.knowledge_m = Ontology_Master()

    def search_by_category(self, term):
        if len(term.term_categories) > 0:
            for category in term.term_categories:
                try:
                    if 'Q5-' in category:
                        self.person_searcher.search(term)
                    elif 'Q515-' in category or 'Q6256-' in category:
                        self.country_Searcher.search(term)
                    elif 'Q16521-' in category:
                        self.taxon_searcher.search(term)
                except Exception as e:
                    print(e)
            '''
            self.filter.filter(term)
            old_graph = self.knowledge_m.load_knowledge(term)
            # El termino ya existe
            print("Search Finished")
            if old_graph:
                new_graph = self.knowledge_m.create_graph(term)
                self.knowledge_m.combine_knowledge(new_graph, old_graph)
                self.knowledge_m.save_knowledge(new_graph)
            # El termino no existe
            else:
                self.knowledge_m.create_and_save_oltologys(term)
            '''
