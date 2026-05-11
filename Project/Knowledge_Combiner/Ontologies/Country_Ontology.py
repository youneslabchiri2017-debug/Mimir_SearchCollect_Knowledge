from Project.Knowledge_Combiner.Ontologies.Ontology import Ontology


class Country_Ontology(Ontology):

    def __init__(self, terms, key_id, nx=None):
        self.required_properties = ['name']
        self.rdf_type = "schema:Country"
        self.property_map = {
            "name": "schema:name",
            "address": "schema:address",
            "latitude": "schema:latitude",
            "longitude": "schema:longitude",
        }
        if nx:
            super().__init__(terms, key_id, nx)
        else:
            super().__init__(terms, key_id)