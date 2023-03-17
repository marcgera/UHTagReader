from flask import Flask, render_template, request, Blueprint
import tagdb
import os

print('')
print(' **********************************************************')
print(' *                                                        *')
print(' * Tagdb server - Marc Geraerts - March 2023 - V1.0       *')
print(' *   Institute of Rehabilitation Science - UHasselt       *')
print(' *                                                        *')
print(' **********************************************************')
print('')

app = Flask(__name__)
app.secret_key = "!g$FRrWwkqtCZfrsptyYWwBb*"

db = tagdb.tagdb()
db.create_db()

@app.route('/')
def hello():
    return 'tagDB server'

@app.route('/log', methods=['GET'])
def log():
    tagMD5 = request.args.get('hsh')
    deviceMAC = request.args.get('mac')
    result = db.log_tag(tagMD5, deviceMAC)
    return result


@app.route ('/isfile/')
def test3():
    fname = os.getcwd() + os.path.sep + 'database' + os.path.sep + 'tagdb.db'
    return (str(os.path.isfile(fname)))


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host='127.0.0.1', port=81, debug=True)
# [END gae_flex_quickstart]