from Project.Knowledge_Combiner.Ontologies.Ontology import Ontology


class Taxon_Ontology(Ontology):

    def __init__(self, terms, key_id, db, nx=None):
        self.required_properties = ['name']
        self.rdf_type = "schema:Taxon"
        self.property_map = {
            "taxon_name": "schema:taxon name",
            "parent_taxon_name": "schema:parent taxon",
            "taxon_rank": "schema: taxon rank",
            "taxon_common_name": "schema:name",
            "taxon_type": "schema:taxon type",
            "start_time": "schema:start time",
            "endemic_to": "schema:endemic to",
            "life_expectancy": "schema:life expectancy",
            "means_of_locomotion": "schema:means of locomotion",
            "diel_cycle": "schema:diel cycle",
            "has_fruit_type": "has fruit type"
        }
        if nx:
            super().__init__(terms, key_id, db, nx)
        else:
            super().__init__(terms, key_id, db)