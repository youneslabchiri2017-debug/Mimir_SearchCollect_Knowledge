import requests, os, networkx as nx, matplotlib.pyplot as plt
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from urllib.parse import quote
from rdflib.parser import headers


class DB_Controller():

    def __init__(self):
        self.SCHEMA = Namespace("http://schema.org/")
        self.LOCAL = Namespace("http://tu_proyecto.org/resource/")
        self.EXTRA = Namespace("http://tu_proyecto.org/properties/extra/")
        self.url = "http://localhost:7200/repositories/KnowledgeDB"

    def clean_for_uri(self, text):
        """
        Convierte cualquier texto en una cadena 100% segura para ser usada como URI.
        Reemplaza espacios por guiones bajos y codifica símbolos raros.
        """
        # 1. Convertimos a string y cambiamos espacios por guiones bajos
        texto_str = str(text).replace(" ", "_")
        # 2. quote codifica las comillas, paréntesis, tildes, etc.
        # El parámetro safe="_-" asegura que no nos modifique los guiones
        return quote(texto_str, safe="_-")

    def save_knowledge(self, ontologys):
        # Crear carpeta de debug si no existe
        if not os.path.exists('debug_turtles'):
            os.makedirs('debug_turtles')

        for id in ontologys:
            try:
                # Usamos UTF-8 para evitar errores con tildes o caracteres especiales
                data_turtle = ontologys[id].graph.serialize(format='turtle')

                # 5. Envío a GraphDB
                headers = {'Content-Type': 'text/turtle'}
                response = requests.post(f"{self.url}/statements", data=data_turtle, headers=headers)

                print(f"Ontología {id} ({ontologys[id].term}) enviada. Status: {response.status_code}")

                if response.status_code == 400:
                    print(f"Respuesta del servidor (Error 400): {response.text}")

                # --- GUARDADO LOCAL PARA DEBUG ---
                file_path = f"debug_turtles/{id}.ttl"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(data_turtle)
                print(f"Archivo guardado localmente en: {file_path}")
                # ----------------------------------

            except Exception as e:
                print(f"Error procesando ontología {id}: {e}")


    def load_knowledge(self, term_name):
        # 1. Preparar la URI y la consulta
        clean_term = term_name.replace(" ", "_")
        # Asegúrate de que coincida con la URI que usaste para guardar
        uri_full = f"http://tu_proyecto.org/resource/{clean_term}"

        query = f"DESCRIBE <{uri_full}>"

        # 2. Configurar la petición al endpoint de SPARQL
        # Nota: El endpoint de consulta suele terminar en /repositories/TuRepo
        endpoint = self.url.replace("/statements", "")

        headers = {
            'Accept': 'text/turtle',  # Queremos que nos devuelva el grafo en Turtle
        }

        params = {
            'query': query
        }

        try:
            response = requests.get(endpoint, params=params, headers=headers)

            if response.status_code == 200:
                # 3. Cargar el resultado en rdflib
                retrieved_graph = Graph()
                retrieved_graph.parse(data=response.text, format="turtle")

                print(f"Grafo de {term_name} recuperado. Total de triples: {len(retrieved_graph)}")

                # Opcional: Mostrar los triples recuperados
                for s, p, o in retrieved_graph:
                    print(f"S: {s} | P: {p} | O: {o}")

                return retrieved_graph
            else:
                print(f"Error al consultar: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"Error en la conexión SPARQL: {e}")
            return None

    def delete_knowledge(self, term_name):
        # 1. Preparar la URI del sujeto
        clean_term = term_name.replace(" ", "_")
        uri_full = f"http://tu_proyecto.org/resource/{clean_term}"

        # 2. Definir la consulta SPARQL Update
        # Borra todos los triples donde Oscar Corcho sea el SUJETO
        query = f"""
        DELETE WHERE {{ 
            <{uri_full}> ?p ?o . 
        }}
        """

        # 3. Endpoint de GraphDB para actualizaciones
        # Es el mismo que usas para subir (el que termina en /statements)
        url = f"{self.url}/statements"

        # IMPORTANTE: Para borrar, el Content-Type debe ser application/sparql-update
        headers = {
            'Content-Type': 'application/sparql-update'
        }

        try:
            response = requests.post(url, data=query, headers=headers)

            if response.status_code in [200, 204]:
                print(f"Éxito: Se ha eliminado a '{term_name}' de la base de datos.")
            else:
                print(f"Error al eliminar: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"Error en la conexión al borrar: {e}")

    def replace_knowledge(self, term):
        pass


    def rdf_to_nx(self, rdf_graph):
        """Convierte un grafo de RDFLib a NetworkX para visualización."""
        nx_graph = nx.DiGraph()  # Usamos DiGraph para ver la dirección de las flechas

        for s, p, o in rdf_graph:
            # Extraemos el final de la URI (lo que hay después de la última / o #)
            s_label = str(s).split('/')[-1].split('#')[-1].replace("_", " ")
            p_label = str(p).split('/')[-1].split('#')[-1].replace("_", " ")
            o_label = str(o).split('/')[-1].split('#')[-1].replace("_", " ")

            # Añadimos la arista con el predicado como atributo
            nx_graph.add_edge(s_label, o_label, label=p_label)

        return nx_graph

    def term_exists(self, term_name):
        clean_term = term_name.replace(" ", "_")
        uri_full = f"http://tu_proyecto.org/resource/{clean_term}"

        query = f"ASK {{ <{uri_full}> ?p ?o . }}"

        endpoint = self.url.replace("/statements", "")

        headers = {
            'Accept': 'application/sparql-results+json'
        }

        params = {
            'query': query
        }

        try:
            response = requests.get(endpoint, params=params, headers=headers)

            if response.status_code == 200:
                data = response.json()
                # El resultado de un ASK está en la clave 'boolean'
                exists = data.get('boolean', False)
                return exists
            else:
                print(f"Error en la consulta: {response.status_code}")
                return False

        except Exception as e:
            print(f"Error de conexión: {e}")
            return False

    def draw_retrieved_graph(self, nx_graph, center_node_name):
        """Dibuja el grafo recuperado con Matplotlib."""
        plt.figure(figsize=(15, 10))

        # Layout para organizar los nodos
        pos = nx.spring_layout(nx_graph, k=0.8)

        # Colores: Nodo buscado en naranja, los demás en azul
        node_colors = [
            'orange' if node.lower() == center_node_name.lower() else 'skyblue'
            for node in nx_graph.nodes()
        ]

        # Dibujar Nodos
        nx.draw_networkx_nodes(nx_graph, pos, node_size=3000, node_color=node_colors, alpha=0.8)

        # Dibujar Etiquetas de Nodos
        nx.draw_networkx_labels(nx_graph, pos, font_size=9, font_weight='bold')

        # Dibujar Aristas
        nx.draw_networkx_edges(nx_graph, pos, edge_color='gray', arrows=True, arrowsize=20)

        # Dibujar Etiquetas de las Aristas (las propiedades)
        edge_labels = nx.get_edge_attributes(nx_graph, 'label')
        nx.draw_networkx_edge_labels(nx_graph, pos, edge_labels=edge_labels, font_color='red')

        plt.title(f"Visualización de conocimiento recuperado: {center_node_name}")
        plt.axis('off')
        plt.show()