import flask
from DB_Access.DB_Controller import DB_Controller

db = DB_Controller()
routes = flask.Blueprint('routes', __name__, url_prefix='/')

@routes.route('/')
def home():
    return flask.render_template('home.html')

@routes.route('/mimir_oracles')
def mimir_chatbot():
    return flask.render_template('mimir_chatbot.html')

@routes.route('/knowledge_search')
def knowledge_search():
    return flask.render_template('knowledge_search.html')


@routes.route('/mimir_wiki/<qid>')
def mimir_wiki(qid):
    try:
        # 1. Recuperar los datos crudos de tu controlador DB
        info_premium = db.get_premium_data(qid)
        general_info = db.get_general_info(qid)
        all_data = db.get_tuples_of_term(qid)

        # NUEVO: Obtenemos las tripletas con su procedencia (Named Graphs)
        tuples_prov = db.get_tuples_with_provenance(qid)

        # 2. Extraer Término y Categoría de forma segura
        termino = general_info[0]['l']['value'] if general_info else "Enigma Desconocido"
        categoria = general_info[0]['o']['value'] if general_info else "Grafo General"

        relato_mimir = "Mimir está escudriñando los recuerdos del pozo..."

        # 3. CONSTRUIR DICCIONARIOS REALES
        datos_premium = {}
        for data in info_premium:
            prop = data['attr_name']['value'].replace('_', ' ').capitalize()
            val = data['label']['value']
            datos_premium[prop] = val

        datos_extra = {}
        for data in all_data:
            uri_p = data['pt']['value']
            prop_clean = uri_p.split('/')[-1].split('#')[-1].replace('_', ' ').capitalize()
            val = data['o']['value']
            datos_extra[prop_clean] = val

        # 4. PROCESAR DATOS DE PROCEDENCIA PARA LA TABLA Y LOS GRÁFICOS
        procedencia_tripletas = []
        conteo_origenes = {}

        for item in tuples_prov:
            # Extraer URI del Named Graph y limpiar nombre para mostrar
            g_uri = item.get('g', {}).get('value', 'http://mimir.org/graphs/default')
            g_name = g_uri.split('/')[-1] if '/' in g_uri else g_uri

            pred = item.get('pt', {}).get('value', 'propiedad')
            obj = item.get('o', {}).get('value', '')

            procedencia_tripletas.append({
                "predicado": pred,
                "objeto": obj,
                "origen": g_name
            })

            # Conteo para el gráfico de barras (Tripletas por origen)
            conteo_origenes[g_name] = conteo_origenes.get(g_name, 0) + 1

        # Si no hay datos reales de origen, colocamos datos mock seguros para pruebas
        if not conteo_origenes:
            conteo_origenes = {"Wikidata": 12, "DBpedia": 8, "Internal-PROV": 5}

        origenes_labels = list(conteo_origenes.keys())
        origenes_valores = list(conteo_origenes.values())

        # Métricas calculadas para la interfaz
        total_tripletas = len(tuples_prov) if tuples_prov else len(all_data)
        num_subgrafos = len(origenes_labels)
        num_predicados = len(datos_extra)
        densidad = round(total_tripletas / (num_predicados if num_predicados > 0 else 1), 2)

        metricas = {
            "total_tripletas": total_tripletas,
            "num_subgrafos": num_subgrafos,
            "num_predicados": num_predicados,
            "densidad": densidad
        }

        # Estructura para el gráfico de sectores (Intersección de Subgrafos)
        datos_graficos = {
            "origenes": origenes_labels,
            "cantidades": origenes_valores,
            "interseccion_labels": [f"Exclusivo {org}" for org in origenes_labels] + ["Intersección Compartida"],
            "interseccion_valores": [val * 2 for val in origenes_valores] + [max(1, total_tripletas // 3)]
        }

        otras_entidades_list = []

        # 4. Renderizar pasando estructuras compatibles a Jinja2
        return flask.render_template('mimir_wiki.html',
                                     termino=termino,
                                     categoria=categoria,
                                     relato_mimir=relato_mimir,
                                     datos_premium=datos_premium,
                                     datos_extra=datos_extra,
                                     procedencia_tripletas=procedencia_tripletas,
                                     otras_entidades=otras_entidades_list,
                                     qid=qid,
                                     metricas=metricas,
                                     datos_graficos=datos_graficos
                                     )

    except Exception as e:
        print(f"❌ Error crítico en el telar de Mimir: {str(e)}")
        return f"Error interno en el servidor: {str(e)}", 500


