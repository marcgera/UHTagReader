from flask import Flask, render_template, request, Blueprint
import tagdb

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
    return 'Hello, World!'

@app.route('/log', methods=['GET'])
def log():
    tagIDMD5 = request.args.get('hsh')
    result = db.log_tag(tagIDMD5)
    return result


app.run(host='0.0.0.0', port=81)
