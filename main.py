import pickle

from flask import Flask, render_template, request, Blueprint, flash, Response
import tagdbmysql
import os
import json
from google_auth_oauthlib.flow import Flow
# Third-party libraries
from flask import Flask, redirect, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from oauthlib.oauth2 import WebApplicationClient
import pathlib
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime
from flask_mail import Mail, Message
from email.message import EmailMessage
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from Google import Create_Service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import os.path

import google.auth
from googleapiclient.errors import HttpError

import requests
from User import User

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
print(' * Tagdb server - Marc Geraerts - Sept 2023 - V1.0        *')
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

client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://mail.google.com/",
            "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


client = WebApplicationClient(GOOGLE_CLIENT_ID)

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
app.secret_key = "!g$FRrWwkqtCZfrsptyYWwBb*"

app.config['MAIL_SERVER'] = 'smtp.sendgrid.net'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'apikey'
app.config['MAIL_PASSWORD'] = os.environ.get("SENDGRID_API_KEY", None)
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('SENDGRID_DEFAULT_FROM')
mail = Mail(app)


def gmail_create_draft():
  """Create and insert a draft email.
   Print the returned draft's message and id.
   Returns: Draft object, including draft id and message meta data.

  Load pre-authorized user credentials from the environment.

  for guides on implementing OAuth2 for the application.
  """
  creds, _ = google.auth.default()

  try:
    # create gmail api client
    service = build("gmail", "v1", credentials=creds)

    message = EmailMessage()

    message.set_content("This is automated draft mail")

    message["To"] = "gduser1@workspacesamples.dev"
    message["From"] = "gduser2@workspacesamples.dev"
    message["Subject"] = "Automated draft"

    # encoded message
    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_message = {"message": {"raw": encoded_message}}
    # pylint: disable=E1101
    draft = (
        service.users()
        .drafts()
        .create(userId="me", body=create_message)
        .execute()
    )

    print(f'Draft id: {draft["id"]}\nDraft message: {draft["message"]}')

  except HttpError as error:
    print(f"An error occurred: {error}")
    draft = None

  return draft

db = tagdbmysql.tagdbmysql()
user_id = -1
service = None
device_id = -1
recentLoggedTagID = -1
tagLinkedtoUserEmail = ""

@login_manager.user_loader
def load_user(users_ID):
    usr = User(users_ID)
    return usr

def gmail_authenticate():
    creds = None
    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow1 = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow1.run_local_server(port=0)
        # save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

# get the Gmail API service

def get_formatted_datetime():
    # Get the current date and time
    now = datetime.now()
    # Format the date and time
    formatted_datetime = now.strftime('%d-%b-%Y %H:%M:%S')
    return formatted_datetime


@app.route('/')
def home():
    if current_user:
        if current_user.is_authenticated:
            return (
                "<p>Hello, {}! You're logged in! Email: {}</p>"
                '<a class="button" href="/logout">Logout</a>'.format(
                    current_user.name, current_user.email
                )
            )

    return render_template('login.html')
    return '<a class="button" href="/login">Google Login</a>'

@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/index')
def index():

    if current_user:

        if not current_user.is_authenticated:
            return app.login_manager.unauthorized()

        if current_user.is_admin:
            return render_template('index.html')
        else:
            return render_template_user()
    else:
        return render_template('login.html')


    # if current_user.is_authenticated:
    #     return (
    #         "<p>Hello, {}! You're logged in! Email: {}</p>"
    #         '<a class="button" href="/logout">Logout</a>'.format(
    #             current_user.name, current_user.email
    #         )
    #     )
    # else:
    #     return '<a class="button" href="/login">Google Login</a>'


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

@app.route('/get_users',  methods=['GET'])
def getUsers():
    field_name = request.args.get('field_name')
    selection = request.args.get('selection')
    return db.getUsers(field_name, selection)

@app.route('/reader_stat', methods=['get'])
def readerStat():
    json_payload = request.args.get('json_payload')
    dict_payload = json.loads(json_payload)
    result = db.log_reader_stat(dict_payload)
    return result

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
        user_picture_url = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
        users_surname = userinfo_response.json()["family_name"]

        current_user = User(users_email, users_name, users_surname, user_picture_url)
        login_user(current_user,  remember=False)

    else:
        return "User email not available or not verified by Google.", 400
    # Create a user in your db with the information provided
    # by Google

    global user_id
    user_id = current_user.ID


    # Send user back to homepage
    redirect_url = url_for("index")

    return redirect(redirect_url)

def ensureHTTPS(url):
        return  url.replace("http:", "https:")

@app.route("/user")
@login_required
def user():
    render_template_user()


def render_template_user():
    global device_id
    template = render_template('user.html',
                    user_name=current_user.name,
                    user_surname=current_user.surname,
                    user_email=current_user.email,
                    tag_id = recentLoggedTagID,
                    tag_Linked_to_User_Email =tagLinkedtoUserEmail,
                    device_id=device_id)
    return template

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return "http200OK"
    #return redirect(url_for("index"))

@app.route("/protected")
@login_required
def protected():
    return "Protected area"

@app.route('/log', methods=['GET'])
def log():
    tagMD5 = request.args.get('hsh')
    deviceMAC = request.args.get('mac')
    result = db.log_tag(tagMD5, deviceMAC)
    return result

@app.route('/logs', methods=['GET'])
def logs():
    return render_template('logs.html')

@app.route('/users', methods=['GET'])
def users():
    return render_template('users.html')

@app.route('/report')
@login_required
def report():
    return render_template('report.html')

@app.route('/admins')
@login_required
def admins():
    return render_template('admins.html')

@app.route('/getCurrentUser')
@login_required
def get_current_user():
    return current_user.get_JSON()

@app.route('/groups')
@login_required
def groups():
    return render_template('groups.html')

@app.route('/events')
@login_required
def events():
    return render_template('events.html')

@app.route('/register')
@login_required
def register():
    return render_template('register.html')

@app.route('/recentLogs')
def recentLogs():
    return render_template('recentLogs.html')

@app.route('/myaccount')
def myaccount():
    return render_template('myaccount.html',
        user_name = current_user.name,
        user_surname = current_user.surname,
        user_email = current_user.email,
        tag_id = recentLoggedTagID,
        tag_Linked_to_User_Email = tagLinkedtoUserEmail,
        device_id = device_id)

@app.route('/qrdevice', methods=['GET'])
def qrdevice():
    global device_id
    global recentLoggedTagID
    global tagLinkedtoUserEmail

    device_id = request.args.get('id')
    recentLoggedTagID = db.getMostRecentLogEntry(device_id)

    if isinstance(recentLoggedTagID, dict):
        tagLinkedtoUserEmail = recentLoggedTagID.get("user_email")
        recentLoggedTagID = recentLoggedTagID.get("tag_id")
    else:
        tagLinkedtoUserEmail = ""



    redirect_url = url_for("index")
    return redirect(redirect_url)

@app.route('/get_most_recent_log', methods=['GET'])
def get_most_recent_log():
    device_id = request.args.get('id')
    return db.getMostRecentLogEntry(device_id)

@app.route('/get_device_id', methods=['GET'])
def get_device_id():
    device_mac = request.args.get('mac')
    return db.get_device_id(device_mac)

@app.route('/frd4VIWD')
@login_required
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
    return json.dumps(db.get_logs(start_time, end_time, device_id))

@app.route('/get_last_names', methods=['GET'])
def get_last_names():
    name_start = request.args.get('name_start')
    return json.dumps(db.get_last_names(name_start))

@app.route('/get_admins')
@login_required
def get_admins():
    return json.dumps(db.get_admins())


#GROUPS*************************************************

@app.route('/groups/add', methods=['GET'])
@login_required
def groups_add():
    name = request.args.get('name')
    is_public = request.args.get('is_public')
    owner_ID = current_user.get_id()
    result = db.insert_group(name, owner_ID, is_public)
    if result == 'http200OK':
        return json.dumps(db.get_groups(current_user.get_id()))
    else:
        return 'Error inserting group'

@app.route('/groups/remove', methods=['GET'])
@login_required
def groups_remove():
    group_ID = request.args.get('group_ID')
    result = db.remove_group(group_ID, current_user.get_id())
    if result == 'http200OK':
        return json.dumps(db.get_groups(current_user.get_id()))
    else:
        return 'Error removing group'

@app.route('/groups/edit', methods=['GET'])
@login_required
def groups_edit():
    group_ID = request.args.get('group_ID')
    name = request.args.get('name')
    is_public = request.args.get('is_public')
    is_editable = request.args.get('is_editable')
    result = db.edit_group(group_ID, name, is_public, is_editable)
    if result == 'http200OK':
        return json.dumps(db.get_groups(current_user.get_id()))
    else:
        return 'Error removing group'


@app.route('/groups/addMember', methods=['GET'])
@login_required
def groups_add_member():
    group_ID = request.args.get('group_ID')
    user_ID = request.args.get('user_ID')
    return json.dumps(db.add_group_member(group_ID, user_ID))

@app.route('/groups/removeMember', methods=['GET'])
@login_required
def groups_remove_member():
    group_member_ID = request.args.get('group_member_ID')
    return json.dumps(db.remove_group_member(group_member_ID))

@app.route('/groups/getMembers', methods=['GET'])
@login_required
def groups_get_members():
    group_ID = request.args.get('group_ID')
    return json.dumps((db.get_group_members(group_ID)))

@app.route('/groups/getList', methods=['GET'])
@login_required
def groups_get_list():
    include_public = request.args.get('include_public')
    return json.dumps(db.get_groups(current_user.get_id(), include_public))

@app.route('/groups/getGroup', methods=['GET'])
@login_required
def groups_get_group():
    group_ID = request.args.get('group_ID')
    return json.dumps(db.get_group(group_ID))

#EVENTS*************************************************

@app.route('/events/add', methods=['GET'])
@login_required
def events_add():
    name = request.args.get('name')
    is_public = request.args.get('is_public')
    owner_ID = current_user.get_id()
    result = db.insert_event(name, owner_ID, is_public)
    if result == 'http200OK':
        return db.getLastAddedIDFromTable('events')
    else:
        return 'Error inserting group'

@app.route('/events/remove', methods=['GET'])
@login_required
def events_remove():
    event_ID = request.args.get('event_ID')
    result = db.remove_event(event_ID, current_user.get_id())
    if result == 'http200OK':
        return result
    else:
        return 'Error inserting group'

@app.route('/events/edit', methods=['GET'])
@login_required
def events_edit():
    event_ID = request.args.get('event_ID')
    name = request.args.get('name')
    is_public = request.args.get('is_public')
    is_editable = request.args.get('is_editable')
    event_start_datetime = request.args.get('event_start_datetime')
    event_end_datetime = request.args.get('event_end_datetime')
    result = db.edit_event(event_ID, name, is_public, is_editable)
    if result == 'http200OK':
        return db.getLastAddedIDFromTable('events')
    else:
        return 'Error removing event'

@app.route('/events/addMember', methods=['GET'])
@login_required
def events_add_member():
    event_ID = request.args.get('event_ID')
    user_ID = request.args.get('user_ID')
    return json.dumps(db.add_event_member(event_ID, user_ID))

@app.route('/events/removeMember', methods=['GET'])
@login_required
def events_remove_member():
    event_member_ID = request.args.get('event_member_ID')
    return json.dumps(db.remove_event_member(event_member_ID))

@app.route('/events/getMembers', methods=['GET'])
@login_required
def events_get_members():
    event_ID = request.args.get('event_ID')
    return json.dumps((db.get_event_members(event_ID)))

@app.route('/events/getList', methods=['GET'])
@login_required
def events_get_list():
    include_public = request.args.get('include_public')
    return json.dumps(db.get_events(current_user.get_id(), include_public))

@app.route('/events/getGroup', methods=['GET'])
@login_required
def events_get_group():
    event_ID = request.args.get('event_ID')
    return json.dumps(db.get_event(event_ID))

@app.route('/get_individual_logs', methods=['GET'])
def get_individual_logs():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    device_id = request.args.get('device_id')
    user_id = request.args.get('user_id')
    data = db.get_individual_logs(user_id, start_date, end_date, device_id)
    return json.dumps(data)

@app.route('/get_devices', methods=['GET'])
def get_devices():
    return json.dumps(db.getDevices())

@app.route("/download_logs_excel")
def download_logs_excel():
    with open("outputs/Adjacency.csv") as fp:
        csv = fp.read()
    return Response(
        csv,
        mimetype="application/vnd.ms-excel",
        headers={"Content-disposition":
                 "attachment; filename=static/downloads/logs.xlsx"})

@app.route('/insert_user_and_link2tag', methods=['GET'])
def insert_user_and_link2tag():
    tag_id = request.args.get('tag_id')
    user_name = request.args.get('user_name')
    user_surname = request.args.get('user_surname')
    user_email = request.args.get('user_email')
    user_external_id = request.args.get('user_external_id')
    return db.insert_user_and_link2tag(tag_id, user_name, user_surname, user_external_id, user_email)

@app.route('/insertUser', methods=['GET'])
def insert_user():
    tag_id = request.args.get('tag_id')
    return render_template('insertUser.html', tag_id=tag_id)

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
    response = db.get_user_from_tag_id(tag_id, only_name)
    return response

@app.route('/get_user')
@login_required
def get_user():
    user_dict = current_user.get_JSON()
    return json.dumps(user_dict)

@app.route('/get_most_recent_logs')
def get_most_recent_logs():
    data = db.getMostRecentLogEntries()
    return json.dumps(data)

@app.route('/disconnectTagFromUser', methods=['GET'])
def disconnectTagFromUser():
    tagID = request.args.get('tagID')
    data = db.disconnectTagFromUser(tagID)
    return data

@app.route('/generateReportStyle1', methods=['GET'])
def generateReportStyle1():
    user_id = request.args.get('user_id')
    start_time_stamp = request.args.get('start_time_stamp')
    stop_time_stamp = request.args.get('stop_time_stamp')
    device_id = request.args.get('device_id')
    out = db.generateReportStyle1(user_id, start_time_stamp, stop_time_stamp, device_id)
    return out

@app.route('/generateReportStyle2', methods=['GET'])
def generateReportStyle2():
    group_id = request.args.get('group_id')
    start_time_stamp = request.args.get('start_time_stamp')
    stop_time_stamp = request.args.get('stop_time_stamp')
    device_id = request.args.get('device_id')
    out = db.generateReportStyle2(user_id, start_time_stamp, stop_time_stamp, device_id)
    return out

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app.
    app.run(host='127.0.0.1', port=5000, debug=True, ssl_context='adhoc')
# [END gae_flex_quickstart]
