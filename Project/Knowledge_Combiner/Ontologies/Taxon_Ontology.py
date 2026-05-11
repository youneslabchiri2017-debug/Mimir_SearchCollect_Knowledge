from Project.Knowledge_Combiner.Ontologies.Ontology import Ontology


class Taxon_Ontology(Ontology):

    def __init__(self, terms, key_id, nx=None):
        self.required_properties = ['name']
        self.rdf_type = "schema:Taxon"
        self.property_map = {
            "name": "schema:name",
            "scientificName": "schema:scientificName",
            "taxonRank": "schema:taxonRank",
            "parentTaxon": "schema:parentTaxon",
            "status": "schema:conservationStatus"
        }
        if nx:
            super().__init__(terms, key_id, nx)
        else:
            super().__init__(terms, key_id)