from DB_Access.DB_Controller import DB_Controller
from Project.Specific_Searcher.Search_Master import SearchMaster

class Deducer():

    def __init__(self):
        self.ROOT_CLASSES = {
            'Q5': 'person',
            'Q2095': 'food',
            'Q571': 'book',
            'Q11424': 'film',
            'Q4830453': 'business',
            'Q16521': 'taxon',  # Animales, plantas, etc.
            'Q11173': 'chemical compound',
            'Q4022': 'river',
            'Q515': 'city',
            'Q6256': 'country'
        }
        self.searcher = SearchMaster()
        self.db = DB_Controller()

    def deduce_object(self, term):
        self.searcher.search_by_category(term)

    def check_term(self, term):
        self.db.term_exists(term.term)
