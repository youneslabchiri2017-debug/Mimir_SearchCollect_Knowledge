import networkx as nx, re
import matplotlib.pyplot as plt
from rdflib import Graph, Literal, RDF, URIRef, Namespace, OWL
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
        self.graph = self.build_graph(terms.filtered_data[key_cat], key_cat.split("-")[1])
        self.saved_in_db = False

    def clean_for_uri(self, text):
        """Convierte texto en una cadena segura para URIs de recursos (IDs)."""
        texto_str = str(text).replace(" ", "_")
        return quote(texto_str, safe="_-")

    def clean_property_name(self, text):
        """
        Limpia estrictamente los nombres de las propiedades para evitar que
        caracteres extraños (comas, comillas, etc.) rompan el parser de GraphDB.
        """
        text = text.replace("schema:", "").replace("properties/extra/", "")
        text = text.replace(" ", "_")
        # Deja solo letras, números, guiones y guiones bajos
        return re.sub(r'[^a-zA-Z0-9__-]', '', text)

    def build_graph(self, data, term):
        main_subject = self.LOCAL[self.clean_for_uri(term)]
        rdf_g = Graph()

        rdf_g.bind("prov", PROV)
        rdf_g.bind("rdf", RDF)
        rdf_g.bind("owl", OWL)

        # Identificador único dentro de esta construcción del grafo.
        claim_counter = 0

        def source_uri_for(value, fallback):
            """Devuelve una URI de fuente cuando el valor permite identificarla."""
            if isinstance(value, str) and value.startswith(("http://", "https://")):
                return URIRef(value)
            if isinstance(value, str) and re.fullmatch(r"Q[0-9]+", value):
                return URIRef(f"https://www.wikidata.org/entity/{value}")
            return URIRef(f"https://mimir.example/source/{fallback}")

        def add_triple_with_provenance(subject, predicate, obj, source_uri):
            """
            Añade la tripleta original y una descripción reificada de la
            afirmación con su procedencia PROV-O.
            """
            nonlocal claim_counter
            rdf_g.add((subject, predicate, obj))

            claim_counter += 1
            claim = URIRef(f"https://mimir.example/claim/{claim_counter}")

            rdf_g.add((claim, RDF.type, RDF.Statement))
            rdf_g.add((claim, RDF.subject, subject))
            rdf_g.add((claim, RDF.predicate, predicate))
            rdf_g.add((claim, RDF.object, obj))
            rdf_g.add((claim, RDF.type, PROV.Entity))
            rdf_g.add((claim, PROV.wasDerivedFrom, source_uri))

        # --- Recurso principal ---
        if self.rdf_type:
            type_url = self.rdf_type.replace("schema:", str(self.SCHEMA))
            rdf_g.add((main_subject, RDF.type, URIRef(type_url)))

        # No se presupone que 'term' sea un QID. El enlace a Wikidata se añade
        # únicamente si el término es realmente un identificador Wikidata.
        if isinstance(term, str) and re.fullmatch(r"Q[0-9]+", term):
            rdf_g.add((
                main_subject,
                OWL.sameAs,
                URIRef(f"https://www.wikidata.org/entity/{term}")
            ))

        # --- 1. DATA[2]: Wikidata ---
        if 2 in data:
            for u, attr, v, is_literal, qid in data[2]:
                try:
                    clean_attr = self.clean_property_name(attr)
                    is_premium = clean_attr in self.property_map

                    if is_premium:
                        pred_uri = self.PREMIUM[clean_attr]
                        pred_uri_rdfs = self.PREMIUM_S[clean_attr]
                    else:
                        pred_uri = self.SCHEMA[clean_attr]
                        pred_uri_rdfs = self.EXTRA[clean_attr]

                    source_uri = source_uri_for(
                        u,
                        f"wikidata/{term}"
                    )

                    # Se conserva la tripleta textual auxiliar original.
                    add_triple_with_provenance(
                        main_subject, pred_uri_rdfs, Literal(v), source_uri
                    )

                    if is_literal == "entity" and qid:
                        local_object = self.LOCAL[self.clean_for_uri(qid)]

                        add_triple_with_provenance(
                            main_subject, pred_uri, local_object, source_uri
                        )

                        wikidata_uri = URIRef(
                            f"https://www.wikidata.org/entity/{qid}"
                        )
                        rdf_g.add((local_object, OWL.sameAs, wikidata_uri))

                        # Etiquetas derivadas de la misma afirmación de Wikidata.
                        add_triple_with_provenance(
                            local_object, self.EXTRA["Label"],
                            Literal(v), source_uri
                        )
                        add_triple_with_provenance(
                            local_object, self.PREMIUM_S["Label"],
                            Literal(v), source_uri
                        )

                except Exception as e:
                    print(f"Error procesando Wikidata ({attr}): {e}")

            names = [
                item for item in data[2]
                if item[1] in {"short name", "taxon name", "given name"}
            ]
            for name in names:
                source_uri = source_uri_for(name[0], f"wikidata/{term}")
                add_triple_with_provenance(
                    main_subject,
                    self.EXTRA["Label"],
                    Literal(name[2]),
                    source_uri
                )

        # --- 2. DATA[3]: DBpedia ---
        if 3 in data:
            for u, attr, v in data[3]:
                try:
                    source_uri = source_uri_for(
                        u,
                        f"dbpedia/{self.clean_for_uri(term)}"
                    )

                    if attr != "Link from a Wikipage to an external page":
                        clean_attr = self.clean_property_name(attr)
                        pred_uri = self.EXTRA[clean_attr]
                        obj = Literal(v)
                    else:
                        pred_uri = OWL.sameAs
                        obj = URIRef(v)

                    add_triple_with_provenance(
                        main_subject, pred_uri, obj, source_uri
                    )

                except Exception as e:
                    print(f"Error procesando DBpedia ({attr}): {e}")

        # --- 3. DATA[0]: formato tradicional ---
        if 0 in data:
            for u, attr, v in data[0]:
                try:
                    clean_attr = self.clean_property_name(attr)
                    pred_uri = self.SCHEMA[clean_attr]
                    source_uri = source_uri_for(u, "traditional")

                    add_triple_with_provenance(
                        main_subject, pred_uri, Literal(v), source_uri
                    )

                except Exception as e:
                    print(f"Error procesando data[0] ({attr}): {e}")

        # --- 4. DATA[1]: formato extra ---
        if 1 in data:
            for u, attr, v in data[1]:
                try:
                    clean_attr = self.clean_property_name(attr)
                    pred_uri = self.EXTRA[clean_attr]
                    source_uri = source_uri_for(u, "extra")

                    add_triple_with_provenance(
                        main_subject, pred_uri, Literal(v), source_uri
                    )

                except Exception as e:
                    print(f"Error procesando data[1] ({attr}): {e}")

        return rdf_g



    def validate(self, data):
        return all(prop in data for prop in self.required_properties)

    def draw_graph(self):
        G = self.graph
        pos = nx.spring_layout(G)

        # 4. Dibujar el grafo
        plt.figure(figsize=(8, 6))
        nx.draw(
            G, pos,
            with_labels=True,  # Mostrar los nombres de los nodos
            node_color='skyblue',  # Color del nodo
            node_size=2000,  # Tamaño del nodo
            edge_color='gray',  # Color de las líneas
            font_size=12,  # Tamaño de la letra
            font_weight='bold'  # Negrita para las etiquetas
        )

        # 5. Mostrar con Matplotlib
        plt.title("Visualización de Grafo con NetworkX")
        plt.show()

    def draw_limited_graph(self, center, N=20):
        # Obtener vecinos directos del nodo central
        neighbors = list(self.graph.neighbors(center))

        # Limitar a los primeros N vecinos
        limited_neighbors = neighbors[:N]

        # Crear lista de nodos a incluir (centro + vecinos)
        nodes_to_include = [center] + limited_neighbors

        # Crear subgrafo
        subgraph = self.graph.subgraph(nodes_to_include)

        # Layout
        pos = nx.spring_layout(subgraph, seed=42)

        # Colores de aristas según in_pm
        edge_colors = [
            "red" if d.get("in_pm") else "gray"
            for _, _, d in subgraph.edges(data=True)
        ]

        # Dibujar nodos
        nx.draw_networkx_nodes(subgraph, pos, node_color="lightblue", node_size=800)

        # Dibujar etiquetas
        nx.draw_networkx_labels(subgraph, pos, font_size=8)

        # Dibujar aristas
        nx.draw_networkx_edges(subgraph, pos, edge_color=edge_colors, width=2)

        # Etiquetas de aristas
        edge_labels = nx.get_edge_attributes(subgraph, "prop")
        nx.draw_networkx_edge_labels(subgraph, pos, edge_labels=edge_labels, font_size=6)

        plt.axis("off")
        plt.show()