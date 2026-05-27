from Project.Knowledge_Combiner.Ontologies.Ontology import Ontology

class Person_Ontology(Ontology):

    def __init__(self, terms, key_id, db, nx = None):
        self.required_properties = ['name']
        self.rdf_type = "schema:Person"
        self.property_map = {
            "given_name": "schema:name",
            "date_of_birth": "schema:birthDate",
            "place_of_birth": "schema:placeOfBirth",
            "educated_at": "schema:educatedAt",
            "position_held": "schema:positionHeld",
            "occupation": "schema:occupation",
            "country_of_citizenship": "schema:nationality",
            "sex_or_gender": "schema:sex"
        }
        if nx:
            super().__init__(terms, key_id, db, nx)
        else:
            super().__init__(terms, key_id, db)

