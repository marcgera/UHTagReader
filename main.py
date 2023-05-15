from flask import Flask, render_template, request, Blueprint
import tagdb
import Admin
import os
import json

# Third-party libraries
from flask import Flask, redirect, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient
import requests

from Admin import Admin

# try:
#     import googleclouddebugger
#     googleclouddebugger.enable(
#     breakpoint_enable_canary=True
#   )
# except ImportError:
#   pass

print('')
print(' **********************************************************')
print(' *                                                        *')
print(' * Tagdb server - Marc Geraerts - March 2023 - V1.0       *')
print(' *   Institute of Rehabilitation Science - UHasselt       *')
print(' *                                                        *')
print(' **********************************************************')
print('')

# Configuration
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID_UH_TAG", None)
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET_UH_TAG", None)
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)

client = WebApplicationClient(GOOGLE_CLIENT_ID)

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = "!g$FRrWwkqtCZfrsptyYWwBb*"

db = tagdb.tagdb()
db.create_db()
user_id = -1

@login_manager.user_loader
def load_user(usr_id):
    admin = Admin()
    admin = admin.get_user_by_ID(usr_id)
    return admin


@app.route('/')
def home():
    if current_user.is_authenticated:
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email
            )
        )
    else:
        return '<a class="button" href="/login">Google Login</a>'


@app.route('/index')
def index():
    if current_user.is_authenticated:
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email
            )
        )
    else:
        return '<a class="button" href="/login">Google Login</a>'


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route('/tkns')
def tkns():
    return os.environ.get("GOOGLE_CLIENT_ID_UH_TAG", None) + \
        " - " + os.environ.get("GOOGLE_CLIENT_SECRET_UH_TAG", None)

@app.route('/registerUser', methods=['GET'])
def registerUser():
    user_name = request.args.get('user_name')
    user_surname = request.args.get('user_surname')
    user_email = request.args.get('user_email')
    event_id = request.args.get('event_id')
    return db.registerUser(user_name, user_surname, user_email, event_id)


@app.route("/login")
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google


    request_uri = client.prepare_request_uri(
            authorization_endpoint,
            redirect_uri=ensureHTTPS(request.base_url + "/callback"),
            scope=["openid", "email", "profile"],
        )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=ensureHTTPS(request.url),
        redirect_url=ensureHTTPS(request.base_url),
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))
    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400
    # Create a user in your db with the information provided
    # by Google

    admin = Admin()
    admin = admin.get_admin(users_email)
    global user_id
    user_id = admin.ID

    # Begin user session by logging the user in
    login_user(admin)

    # Send user back to homepage
    return redirect(url_for("index"))


def ensureHTTPS(url):
    if "https" in url:
        return url
    else:
        return url.replace("http","https")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("You need to login first")
            return redirect(url_for('login_page'))

    return wrap

@app.route('/log', methods=['GET'])
def log():
    tagMD5 = request.args.get('hsh')
    deviceMAC = request.args.get('mac')
    result = db.log_tag(tagMD5, deviceMAC)
    return json.dumps(result)


@app.route('/logs', methods=['GET'])
def logs():
    return render_template('logs.html')

@app.route('/qrdevice', methods=['GET'])
def qrdevice():
    device_id = request.args.get('id')
    return render_template('QRDevice.html', device_id=device_id)

@app.route('/get_most_recent_log', methods=['GET'])
def get_most_recent_log():
    device_id = request.args.get('id')
    return db.getMostRecentLogEntry(device_id)

@app.route('/frd4VIWD')
def iterdump():
    return db.dump()

@app.route('/select', methods=['GET'])
def select():
    select_string = request.args.get('sql')
    return json.dumps(db.select(select_string))

@app.route('/isfile')
def test3():
    fname = os.getcwd() + os.path.sep + 'database' + os.path.sep + 'tagdb.db'
    return (str(os.path.isfile(fname)))


@app.route('/get_logs', methods=['GET'])
def get_logs():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    device_id = request.args.get('device_id')
    return json.dumps(db.getLogs(start_time, end_time, device_id))

@app.route('/get_devices', methods=['GET'])
def get_devices():
    return json.dumps(db.getDevices())


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
    only_name = request.args.get('only_name')
    return db.get_user_from_tag_id(tag_id, only_name)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host='127.0.0.1', port=5000, debug=True, ssl_context='adhoc')
# [END gae_flex_quickstart]
