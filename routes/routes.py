import flask

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