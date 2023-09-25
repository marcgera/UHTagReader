var g_log;
var tag_ID;

function initialize() {
    $("#user_info").hide();
    $("#no_recent").hide();
  PollDeviceLogs(device_id);
}


function PollDeviceLogs(device_id) {

  var params = 'id=' + device_id;

  $.get("/get_most_recent_log?" + params, function (data, status) {

    if (typeof(data) == 'string') {
      if (data.includes("No recent")) {
        $("#no_recent").show();
      }
    }
    else {
      $("#user_info").show();
      user_name = data.user_name;
      user_surname = data.user_surname;
      user_email = data.user_email;
      tag_ID = data.tag_id;
      tag_timestamp = data.tag_timestamp;

      if (user_email != null) {
        document.getElementById("user_name").style.display = user_name;
        document.getElementById("user_surname").style.display = user_surname;
        document.getElementById("user_email").style.display = user_email;
        document.getElementById("user_id").style.display = user_external_ID;
      }
    }
  });
}


function saveUser() {

    user_name = $('#user_name').val();
    user_surname = $('#user_surname').val();
    user_external_id = $('#user_id').val();
    user_email = $('#user_email').val();

    params = 'user_name=' + user_name;
    params = params + '&user_surname=' + user_surname;
    params = params + '&user_email=' + user_email;
    params = params + '&user_external_id=' + user_external_id;
    params = params + '&tag_id=' + tag_ID;

    $.get("/insert_user_and_link2tag?" + params, function (data, status) {
        $("#no_recent").show();
        $("#user_info").hide();
        if (data.includes("http200OK")){

            $("#message").html("<h1>Insert succes</h1>");
        }else
        {
            $("#message").html("<h1>Insert Failed!</h1>");
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
