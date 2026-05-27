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

        # 2. Extraer Término y Categoría de forma segura (evitando errores si viene vacío)
        termino = general_info[0]['l']['value'] if general_info else "Enigma Desconocido"
        categoria = general_info[0]['o']['value'] if general_info else "Grafo General"

        # Aquí llamarías a tu transformer para generar la historia
        relato_mimir = "Mimir está escudriñando los recuerdos del pozo..."

        # 3. CONSTRUIR DICCIONARIOS REALES (Obligatorio para el .items() del HTML)

        # Mapeo para el Infobox Premium
        datos_premium = {}
        for data in info_premium:
            prop = data['attr_name']['value'].replace('_', ' ').capitalize()
            val = data['label']['value']
            datos_premium[prop] = val

        # Mapeo para la Tabla de Datos Adicionales (Long Tail)
        datos_extra = {}
        for data in all_data:
            # Limpiamos la URI del predicado sobre la marcha si no usaste BIND en SPARQL
            uri_p = data['pt']['value']
            prop_clean = uri_p.split('/')[-1].split('#')[-1].replace('_', ' ').capitalize()
            val = data['o']['value']
            datos_extra[prop_clean] = val

        # Opcional: Lógica de desambiguación si existen múltiples QIDs
        otras_entidades_list = []

        # 4. Renderizar pasando estructuras compatibles ({})
        return flask.render_template('mimir_wiki.html',
                                     termino=termino,
                                     categoria=categoria,
                                     relato_mimir=relato_mimir,
                                     datos_premium=datos_premium,  # Ahora es un {}
                                     datos_extra=datos_extra,      # Ahora es un {}
                                     otras_entidades=otras_entidades_list
                                     )

    except Exception as e:
        # Si algo falla por detrás, esto evitará que la pantalla se quede en blanco sin dar pistas
        print(f"❌ Error crítico en el telar de Mimir: {str(e)}")
        return f"Error interno en el servidor: {str(e)}", 500



