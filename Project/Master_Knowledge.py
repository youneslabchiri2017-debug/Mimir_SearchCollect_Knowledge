from DB_Access.Term import Term
from Project.Filters.Knowledge_Filter import Knowledge_Filter
from Project.Knowledge_Combiner.Ontology_Master import Ontology_Master
from Project.Object_Deducer.Deducer_Wikidata import Deducer_Wikidata
from Project.Specific_Searcher.Search_Master import SearchMaster


class Master_Knowledge():

    def __init__(self):
        self.deducer = Deducer_Wikidata()
        self.search = SearchMaster()
        self.k_combiner = Ontology_Master()
        self.filter = Knowledge_Filter()

    def seatch_new_knowledge(self, term):
        try:
            new_term = Term(term)
            self.deducer.deduce_object(new_term)
            self.search.search_by_category(new_term)
            self.filter.filter(new_term)
            self.k_combiner.create_and_save_oltologys(new_term, save_g=False)
            return new_term
        except Exception as e:
            return None
