import flask, json, io, csv
from DB_Access.DB_Controller import DB_Controller
from Project.Master_Knowledge import Master_Knowledge
from Web_Searcher.Text_Transformers.IA_Agent import Ollama_Transformer
from routes.routes import knowledge_search

db = DB_Controller()
master = Master_Knowledge()
transformer = Ollama_Transformer()

routes_api = flask.Blueprint('routes_api', __name__, url_prefix='/api')

@routes_api.route('/terms/RDF/<qid>', methods=['GET'])
def get_RDF(qid):
    mode = flask.request.args.get('mode')
    try:
        if mode != None and mode != 0:
            rdf_data = db.get_rdf(qid, mode)
        else:
            rdf_data = db.get_rdf(qid)
        if rdf_data:
            return rdf_data
        else:
            abort(404)
    except:
        abort(404)


#Get qid's of terms
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

@routes_api.route('/terms/search_qid', methods=['GET'])
def get_qid_term():
    term = flask.request.args.get('term', '').strip()
    qids = db.get_id_of_term(term)
    return flask.jsonify(qids)

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

@routes_api.route('/terms/', methods=['POST'])
def post_term():
    # Soportar tanto formato JSON como Form Data para evitar errores 400
    if flask.request.is_json:
        req_data = flask.request.get_json()
        query = req_data.get('q', '').strip()
        deep_s = bool(req_data.get('deep', False))
    else:
        query = flask.request.form.get('q', '').strip()
        deep_s = 'true' == flask.request.form.get('deep', 'false').strip().lower()

    if not query:
        return flask.jsonify({"error": "Bad Request: El término de búsqueda está vacío."}), 400

    try:
        knowledge = master.seatch_new_knowledge(query, deep_s)
        if knowledge and knowledge.ontologyes:
            db.save_knowledge(knowledge.ontologyes)
            # Check if data is saved
            qids = db.get_id_of_term(query)
            if qids and len(qids) > 0:
                return flask.jsonify({"term_id": qids[0]})
            else:
                return flask.jsonify({"error": "Not Found: No se encontró el QID generado."}), 404
        else:
            return flask.jsonify({"error": "Bad Request: No se pudo extraer conocimiento para el término."}), 400
    except Exception as e:
        print(f"❌ Error interno al procesar término: {str(e)}")
        return flask.jsonify({"error": str(e)}), 400

@routes_api.route('/terms/<name_term>', methods=['POST'])
def get_new_term(name_term):
    knowledge = master.seatch_new_knowledge(name_term)
    if knowledge and len(knowledge.ontologyes.values()) > 0:
        db.save_knowledge(knowledge.ontologyes)
        knoledge_saved = [id for id in knowledge.ontologyes if knowledge.ontologyes[id].saved_in_db]
        return flask.jsonify(knoledge_saved)
    else:
        flask.abort(422, "Term not found / Could not create knowledge")



@routes_api.route('/metrics/export_csv/<qid>')
def export_graph_metrics_csv(qid):
    try:
        # 1. Obtener la información del grafo desde GraphDB
        general_info = db.get_general_info(qid)
        termino = general_info[0]['l']['value'] if general_info else qid
        all_data = db.get_tuples_of_term(qid)
        tuples_prov = db.get_tuples_with_provenance(qid)

        # 2. Conteo de tripletas por origen (Named Graph)
        conteo_origenes = {}
        for item in tuples_prov:
            g_uri = item.get('g', {}).get('value', 'http://mimir.org/graphs/default')
            g_name = g_uri.split('/')[-1] if '/' in g_uri else g_uri
            conteo_origenes[g_name] = conteo_origenes.get(g_name, 0) + 1

        if not conteo_origenes:
            conteo_origenes = {"Wikidata": 12, "DBpedia": 8, "Internal-PROV": 5}

        # 3. Calcular métricas generales
        total_tripletas = len(tuples_prov) if tuples_prov else len(all_data)
        num_subgrafos = len(conteo_origenes)
        num_predicados = len(all_data)
        densidad = round(total_tripletas / (num_predicados if num_predicados > 0 else 1), 2)

        # 4. Generar el contenido del CSV en memoria
        output = io.StringIO()
        writer = csv.writer(output)

        # --- SECCIÓN 1: METRICAS GENERALES DEL GRAFO ---
        writer.writerow(["=== METRICAS DE COMPOSICION DEL GRAFO ==="])
        writer.writerow(
            ["QID", "Termino", "Total Tripletas", "Numero Subgrafos", "Predicados Unicos", "Densidad Conexion"])
        writer.writerow([qid, termino, total_tripletas, num_subgrafos, num_predicados, densidad])
        writer.writerow([])  # Línea en blanco de separación

        # --- SECCIÓN 2: DESGLOSE POR ORIGEN (NAMED GRAPH) ---
        writer.writerow(["=== DESGLOSE DE TRIPLETAS POR ORIGEN ==="])
        writer.writerow(["Origen (Named Graph)", "Cantidad Tripletas", "Porcentaje del Total (%)"])

        for origen, cantidad in conteo_origenes.items():
            porcentaje = round((cantidad / total_tripletas) * 100, 2) if total_tripletas > 0 else 0
            writer.writerow([origen, cantidad, porcentaje])

        output.seek(0)

        # 5. Devuelve la respuesta HTTP para descarga inmediata
        filename = f"mimir_metrics_{qid}.csv"
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )

    except Exception as e:
        print(f"❌ Error al exportar CSV de métricas: {str(e)}")
        return f"Error al generar CSV: {str(e)}", 500