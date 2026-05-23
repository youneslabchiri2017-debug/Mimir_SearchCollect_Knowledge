import flask
from DB_Access.DB_Controller import DB_Controller
from Web_Searcher.Transformers.Ollama_Transformer import Ollama_Transformer

db = DB_Controller()
routes_api = flask.Blueprint('routes_api', __name__, url_prefix='/api')


# Get the id of the term, and return data of this term
@routes_api.route('/terms/<term>', methods=['GET'])
def get_term_data(term):
    qids = db.get_id_of_term(term)
    if qids:
        data = {}
        for qid in qids:
            info = db.get_tuples_of_term(qid)
            if len(info) > 5:
                data[qid] = info
        mimir_knowledge = Ollama_Transformer().reverse_transform(data, term)
        return flask.jsonify(mimir_knowledge)
    else:
        flask.abort(404, "Term not found")

