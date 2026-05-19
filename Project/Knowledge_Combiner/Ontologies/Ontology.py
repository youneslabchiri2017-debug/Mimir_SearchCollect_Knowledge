import networkx as nx, re
import matplotlib.pyplot as plt
from rdflib import Graph, Literal, RDF, URIRef, Namespace
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
        self.SCHEMA = Namespace("http://schema.org/")
        self.LOCAL = Namespace("http://tu_proyecto.org/resource/")
        self.EXTRA = Namespace("http://tu_proyecto.org/properties/extra/")
        self.url = "http://localhost:7200/repositories/KnowledgeDB"
        self.graph = self.build_graph(terms.filtered_data[key_cat], key_cat.split("-")[1])

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
        main_subject = self.LOCAL[term.replace(" ", "_")]
        rdf_g = Graph()

        # Asignar tipo base del recurso
        type_url = self.rdf_type.replace("schema:", str(self.SCHEMA))
        rdf_g.add((main_subject, RDF.type, URIRef(type_url)))

        # --- 1. PROCESAR DATA[2] (El formato nuevo enriquecido de 5 elementos) ---
        if len(data) > 2 and data[2]:
            for u, attr, v, is_literal, qid in data[2]:
                clean_attr = self.clean_property_name(attr)
                pred_uri = self.SCHEMA[clean_attr]

                if is_literal == 'literal':
                    # ERROR ARREGLADO: Usamos paréntesis () y guardamos el texto 'v' original y limpio
                    rdf_g.add((main_subject, pred_uri, Literal(v)))
                else:
                    # Si es una entidad y tenemos su QID, lo ideal es usar el QID como URI local
                    rdf_g.add((main_subject, pred_uri, self.LOCAL[qid]))

        # --- 2. PROCESAR DATA[0] (Formato antiguo/tradicional de 3 elementos) ---
        if len(data) > 0 and data[0]:
            for u, attr, v in data[0]:
                clean_attr = self.clean_property_name(attr)
                pred_uri = self.SCHEMA[clean_attr]

                # CORRECCIÓN CRÍTICA: Paréntesis en lugar de corchetes.
                # Guardamos el valor real 'v' como texto en el Literal, NO la URI formateada.
                objeto = Literal(v)
                rdf_g.add((main_subject, pred_uri, objeto))

        # --- 3. PROCESAR DATA[1] (Formato antiguo/extra de 3 elementos) ---
        if len(data) > 1 and data[1]:
            for u, attr, v in data[1]:
                clean_attr = self.clean_property_name(attr)
                pred_uri = self.EXTRA[clean_attr]

                # CORRECCIÓN CRÍTICA: Paréntesis en lugar de corchetes y texto plano.
                objeto = Literal(v)
                rdf_g.add((main_subject, pred_uri, objeto))

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