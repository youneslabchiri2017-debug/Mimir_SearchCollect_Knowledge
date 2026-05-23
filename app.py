import flask
from routes.routes import routes
from routes.routes_api import routes_api

app = flask.Flask(__name__)

# Conect routes to server
app.register_blueprint(routes)
app.register_blueprint(routes_api)

if __name__ == '__main__':
    app.run(debug=True)