from Project.Knowledge_Combiner.Ontologies.Ontology import Ontology


class Country_Ontology(Ontology):

    def __init__(self, terms, key_id, db, nx=None):
        self.required_properties = ['name']
        self.rdf_type = "schema:Country"
        self.property_map = {
            "short_name": "schema:name",
            "official_language": "schema:language",
            "continent": "schema:continent",
            "capital": "schema:capital",
            "located_in_time zone": "schema:timezone",
            "coordinate_location": "schema:coordinate",
            "basic_form_of_government": "schema:government",
            #"office held by head of state": "schema:government",
            "head_of_state": "schema:ruler",
            "member_of": "schema:member of",
            "pupulation": "schema:pupulation",
            "currency": "schema:currency",
            "Human_Development_Index": "schema:human index",
            "shares_border_with": "schema:border with",
            "top-level_Internet_domain": "schema:domain"
        }
        if nx:
            super().__init__(terms, key_id, db, nx)
        else:
            super().__init__(terms, key_id, db)