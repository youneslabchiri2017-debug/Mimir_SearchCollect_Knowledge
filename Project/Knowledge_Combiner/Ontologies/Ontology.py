import networkx as nx, re
import hashlib
import matplotlib.pyplot as plt
from rdflib import Graph, Literal, RDF, URIRef, Namespace, OWL, Dataset
from rdflib.namespace import RDF, RDFS, PROV
from DB_Access.DB_Controller import DB_Controller
from urllib.parse import quote


class Ontology:

    def __init__(self, terms, key_cat, db = DB_Controller(), nx = nx):
        if not hasattr(self, "required_properties"):
            self.required_properties = []
        if not hasattr(self, "property_map"):
            self.property_map = {}
        # Same as wikidata
        if not hasattr(self, "rdf_type"):
            self.rdf_type = None
        self.db = db
        self.term = terms.term
        self.nx = nx
        self.SCHEMA = Namespace("http://schema.org/rdf/")
        self.LOCAL = Namespace("http://mimir.org/resource/")
        self.EXTRA = Namespace("http://mimir.org/rdf-schema/")
        self.PREMIUM = Namespace("http://mimir.org/rdf-premium/")
        self.PREMIUM_S = Namespace("http://mimir.org/rdfs-premium/")
        self.url = "http://localhost:7200/repositories/KnowledgeDB"
        self.WikiData = Namespace("https://www.wikidata.org/wiki/")
        self.EX = Namespace("http://example.org/")
        self.WD = Namespace("http://www.wikidata.org/entity/")
        self.DBO = Namespace("http://dbpedia.org/ontology/")

        self.SOURCE_GRAPHS = {
            2: URIRef("http://mimir.org/graph/wikidata"),
            3: URIRef("http://mimir.org/graph/dbpedia"),
            0: URIRef("http://mimir.org/graph/traditional"),
            4: URIRef("http://mimir.org/graph/other"),
        }
        self.graph = self.build_graph(terms.filtered_data[key_cat], key_cat.split("-")[1])
        self.saved_in_db = False


    def clean_for_uri(self, text):
        texto_str = str(text).replace(" ", "_")
        return quote(texto_str, safe="_-")

    def clean_property_name(self, text, source = "Other"):
        text = text.replace("schema:", "").replace("properties/extra/", "")
        text = text.replace(" ", "_")
        # Deja solo letras, números, guiones y guiones bajos
        return re.sub(r'[^a-zA-Z0-9__-]', '', text)

    def add_triple(self, graph, trip, main_subject):
        # Algunos triples pueden contener información adicional,
        # por lo que utilizamos solo los tres primeros elementos.
        if len(trip) < 3:
            raise ValueError(f"Triple incompleto: {trip}")

        _, attr, value = trip[:3]
        clean_attr = self.clean_for_uri(attr)

        # Seleccionar el predicado
        if clean_attr in self.property_map:
            predicate = self.PREMIUM_S[clean_attr]
        else:
            predicate = self.EXTRA[clean_attr]

        graph.add((main_subject, predicate, Literal(value)))

    def build_graph(self, data, term):
        main_subject = self.LOCAL[self.clean_for_uri(term)]

        # Usamos Dataset() para soportar gráficos con nombre (Named Graphs)
        dataset = Dataset()

        # Tipo del sujeto (lo añadimos al grafo por defecto o general del dataset)
        if self.rdf_type:
            type_url = self.rdf_type.replace("schema:", str(self.SCHEMA))
            dataset.add((
                main_subject,
                RDF.type,
                URIRef(type_url)
            ))

        for source, triples in data.items():
            # Ignorar fuentes desconocidas o sin datos
            if source not in self.SOURCE_GRAPHS or not triples:
                continue

            # Obtenemos el grafo específico para esta fuente (ej. http://mimir.org/graph/wikidata)
            graph_id = self.SOURCE_GRAPHS[source]
            source_graph = dataset.graph(graph_id)

            # Bindings opcionales para legibilidad
            source_graph.bind("owl", OWL)
            source_graph.bind("rdfs", RDFS)
            source_graph.bind("dbo", self.DBO)

            # Identidad de Wikidata, cuando corresponde
            if (
                    source == 2
                    and isinstance(term, str)
                    and re.fullmatch(r"Q[0-9]+", term)
            ):
                source_graph.add((
                    main_subject,
                    OWL.sameAs,
                    URIRef(f"https://www.wikidata.org/entity/{term}")
                ))

            # Añadir los triples al grafo de su fuente respectiva
            for trip in triples:
                try:
                    self.add_triple(source_graph, trip, main_subject)
                except Exception as e:
                    print(f"Error procesando fuente {source}, triple {trip}: {e}")

        # Retornamos el Dataset completo (contiene los gráficos con nombre)
        return dataset
