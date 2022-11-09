import flask
import argparse
import api

app = flask.Flask(__name__, static_folder='static', template_folder='templates')
app.register_blueprint(api.api, url_prefix='/api')

@app.route('/') 
def home():
    return flask.render_template('index.html')

@app.route('/users')
def users():
    return flask.render_template('mockup1.html')

@app.route('/problems')
def problems():
    return flask.render_template('mockup2.html')

@app.route('/contests')
def contests():
    return flask.render_template('mockup3.html')

@app.route('/tags')
def tags():
    return flask.render_template('mockup4.html')

@app.route('/tags_intersection')
def tags_intersection():
    return flask.render_template('mockup5.html')

if __name__ == '__main__':
    parser = argparse.ArgumentParser('A codeforces data application, including API & DB')
    parser.add_argument('host', help='the host to run on')
    parser.add_argument('port', type=int, help='the port to listen on')
    arguments = parser.parse_args()
    app.run(host=arguments.host, port=arguments.port, debug=True)
