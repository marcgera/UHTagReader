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
def home():
    return render_template('index.html')

@app.route('/log', methods=['GET'])
def log():
    tagMD5 = request.args.get('hsh')
    deviceMAC = request.args.get('mac')
    result = db.log_tag(tagMD5, deviceMAC)
    return result

@app.route('/logs', methods=['GET'])
def logs():
    return render_template('logs.html')

@app.route ('/isfile')
def test3():
    fname = os.getcwd() + os.path.sep + 'database' + os.path.sep + 'tagdb.db'
    return (str(os.path.isfile(fname)))

@app.route('/get_logs', methods=['GET'])
def get_logs():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    device_id = request.args.get('device_id')
    return db.getLogs(start_time, end_time, device_id)

@app.route('/get_devices', methods=['GET'])
def get_devices():
    return db.getDevices()

@app.route('/insert_user_and_link2tag', methods=['GET'])
def insert_user_and_link2tag():
    tag_id = request.args.get('tag_id')
    user_name = request.args.get('user_name')
    user_surname = request.args.get('user_surname')
    user_email = request.args.get('user_email')
    user_external_id = request.args.get('user_external_id')
    return db.insert_user_and_link2tag(tag_id, user_name, user_surname, user_external_id, user_email)

@app.route('/update_user', methods=['GET'])
def update_user():
    user_id = request.args.get('user_id')
    user_name = request.args.get('user_name')
    user_surname = request.args.get('user_surname')
    user_email = request.args.get('user_email')
    user_external_id = request.args.get('user_external_id')
    return db.update_user(user_id, user_name, user_surname, user_external_id, user_email)

@app.route('/get_user_from_tag_id', methods=['GET'])
def get_user_from_tag_id():
    tag_id = request.args.get('tag_id')
    return db.get_user_from_tag_id(tag_id)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host='127.0.0.1', port=81, debug=True)
# [END gae_flex_quickstart]