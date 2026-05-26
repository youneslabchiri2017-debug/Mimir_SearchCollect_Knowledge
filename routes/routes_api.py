import flask, json
from DB_Access.DB_Controller import DB_Controller
from Project.Master_Knowledge import Master_Knowledge
from Web_Searcher.Transformers.Ollama_Transformer import Ollama_Transformer

db = DB_Controller()
master = Master_Knowledge()
transformer = Ollama_Transformer()

routes_api = flask.Blueprint('routes_api', __name__, url_prefix='/api')

@routes_api.route('/terms/<term>', methods=['GET'])
def get_term_data(term):
    qids = db.get_id_of_term(term)
    if qids:
        data = {}
        for qid in qids:
            info = db.get_tuples_of_term(qid)
            if len(info) > 5:
                data[qid] = info
        mimir_knowledge = transformer.reverse_transform(data, term)
        return flask.jsonify(mimir_knowledge)
    else:
        flask.abort(404, "Term not found")


import json
from flask import Response, abort


@routes_api.route('/ask_mimir/<text>', methods=['GET'])
def ask_mimir(text):
    def generate():
        try:
            # 1. Estado Inicial
            yield f"data: {json.dumps({'status': '🧠 Mimir está procesando tu petición...'})}\n\n"

            extracted_data = transformer.extract_entity_data(text)
            if not extracted_data or not extracted_data['entities']:
                yield f"data: {json.dumps({'response': "Mimir: Mis ojos fallan, forastero. No comprendo sobre qué me preguntas."})}\n\n"
                return

            intencion = extracted_data.get("intent", "describe")
            entidades = extracted_data.get("entities", [])

            if intencion == "relate" and len(entidades) >= 2:
                entidad1, entidad2 = entidades[0], entidades[1]
                msg = f"Mimir: [Aún en desarrollo] Buscaré cómo se entrelazan los destinos de {entidad1} y {entidad2}."
                yield f"data: {json.dumps({'response': msg})}\n\n"
                return

            entidad_principal = entidades[0]

            yield f"data: {json.dumps({'status': f'🔍 Consultando el pozo del conocimiento por \"{entidad_principal}\"...'})}\n\n"
            qids = db.get_id_of_term(entidad_principal)
            data = {}
            for qid in qids:
                info = db.get_tuples_of_term(qid)
                if len(info) > 5:
                    data[qid] = info

            # 2. Si no existe info, buscamos en la Web
            if len(data) == 0:
                yield f"data: {json.dumps({'status': '🦅 Enviando los cuervos a buscar nuevo conocimiento (Scraping)...'})}\n\n"
                knowledge = master.seatch_new_knowledge(entidad_principal)

                if knowledge:
                    yield f"data: {json.dumps({'status': '💾 Grabando las nuevas runas en el grafo (Guardando)...'})}\n\n"
                    db.save_knowledge(knowledge.ontologyes)
                    qids = db.get_id_of_term(entidad_principal)
                    data = {}
                    for qid in qids:
                        info = db.get_tuples_of_term(qid)
                        if len(info) > 5:
                            data[qid] = info
                else:
                    yield f"data: {json.dumps({'error': 'No se encontró información sobre ese término en los Nueve Mundos.'})}\n\n"
                    return

            # 3. Respuesta Final
            yield f"data: {json.dumps({'status': '🗣️ Mimir está ordenando sus recuerdos...'})}\n\n"
            final_story = transformer.reverse_transform(data, entidad_principal, text)

            yield f"data: {json.dumps({'response': final_story})}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': f'Error interno: {str(e)}'})}\n\n"

    # Retornamos el generador con el mimetype correcto para streaming continuo
    return Response(generate(), mimetype='text/event-stream')


@routes_api.route('/terms/<name_term>', methods=['POST'])
def get_new_term(name_term):
    knowledge = master.seatch_new_knowledge(name_term)
    if knowledge and len(knowledge.ontologyes.values()) > 0:
        db.save_knowledge(knowledge.ontologyes)
        knoledge_saved = [id for id in knowledge.ontologyes if knowledge.ontologyes[id].saved_in_db]
        return flask.jsonify(knoledge_saved)
    else:
        flask.abort(422, "Term not found / Could not create knowledge")
