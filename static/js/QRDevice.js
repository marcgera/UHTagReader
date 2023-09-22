var g_log;
var QRC;
var serverURL;
var tag_ID;

function initialize() {
  document.getElementById("qrContent").style.display = "none";
  document.getElementById("user_info").style.display = "none";

  //setInterval("PollDeviceLogs(device_id);", 2500);
  PollDeviceLogs(device_id);

  serverURL = "https://uhtagtools.lm.r.appspot.com/";
  //serverURL = "https://127.0.0.1:5000/";

  PollDeviceLogs(device_id);
  QRC = new QRCode(document.getElementById("qrcode"), { text: serverURL, width: 400, height: 400 });
}

function openInsertUserForm() {
  window.open(serverURL + "insertUser?tag_id=" + tag_ID, "_self");
}

function PollDeviceLogs(device_id) {

  var params = 'id=' + device_id;

  $.get("/get_most_recent_log?" + params, function (data, status) {

    if (typeof(data) == 'string') {
      if (data.includes("No recent")) {
        document.getElementById("name").innerHTML = "No tag is logged in the last 2 minutes";
        document.getElementById("email").innerHTML = "";
        document.getElementById("timelogged").innerHTML = ""
        document.getElementById("qrContent").style.display = "none";
        document.getElementById("user_info").style.display = "block";
      }
    }
    else {
      user_name = data.user_name;
      user_surname = data.user_surname;
      user_email = data.user_email;
      tag_ID = data.tag_id;
      tag_timestamp = data.tag_timestamp;

      if (user_email == null) {
        QRC.clear();
        document.getElementById("qrcode").innerHTML = "";
        new_url = serverURL + "insertUser?tag_id=" + tag_ID;
        QRCr = new QRCode(document.getElementById("qrcode"), { text: new_url, width: 300, height: 300 });
        document.getElementById("qrContent").style.display = "block";
        document.getElementById("user_info").style.display = "none";
        openInsertUserForm();
      }
      else {
        document.getElementById("qrContent").style.display = "none";
        document.getElementById("user_info").style.display = "block";
        document.getElementById("name").innerHTML = user_name + " " + user_surname;
        document.getElementById("email").innerHTML = user_email;
        document.getElementById("timelogged").innerHTML = "Tag ID" + tag_ID + " logged on " + ParseTimeStamp(tag_timestamp);
        
      }
      
    }
  });
}

function ParseTimeStamp(ts) {

  ts = ts.toString();

  if (ts.length == 14) {
    const monthNames = ["January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December"];

    year = ts.substring(0, 4);
    month = parseInt(ts.substring(4, 6));
    day = ts.substring(6, 8);
    hour = ts.substring(8, 10);
    minute = ts.substring(10, 12);
    second = ts.substring(12, 14);
    dateStr = day + " " + monthNames[month] + " " + year + " at " + hour + ":" + minute + ":" + second;

  } else {
    dateStr = "Invalid timestamp: " + ts;
  }
  return dateStr;
}
