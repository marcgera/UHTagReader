var user;
var tag_ID;

function loadUser(){

    $("#user_info").hide();
    $("#no_recent").hide();

    $.get("/get_user", function (data, status) {
        user = JSON.parse(data);
        $('#user_email').html(user_email);
        $('#user_name').html(user_name);
        $('#user_surname').html(user_surname);
        $('#user_id').val(user.external_ID);
    });
    PollDeviceLogs();
}

function PollDeviceLogs() {

  var params = 'id=' + device_id;

  $.get("/get_most_recent_log?" + params, function (data, status) {

    if (typeof(data) == 'string') {
      if (data.includes("No recent")) {
        $("#no_recent").show();
      }
    }
    else {
      $("#user_info").show();
      tag_ID = data.tag_id;
      tag_timestamp = data.tag_timestamp;
    }
  });
}

function saveUser() {

    user_external_id = $('#user_id').val();

    params = 'user_name=' + user_name;
    params = params + '&user_surname=' + user_surname;
    params = params + '&user_email=' + user_email;
    params = params + '&user_external_id=' + user_external_id;
    params = params + '&tag_id=' + tag_ID;

    $.get("/insert_user_and_link2tag?" + params, function (data, status) {
        $("#no_recent").show();
        $("#user_info").hide();
        if (data.includes("http200OK")){

            $("#toast-message").html("<h1>Insert succes</h1>");
        }else
        {
            $("#toast-message").html("<h1>Insert Failed!</h1>");
        }
        $('.toast').toast('show');
    });
}