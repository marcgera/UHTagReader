var user;
var tag_ID;

function loadUser(){


    //hideUserInfo();
    //hideNoRecent();

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

        document.getElementById("user_info").innerHTML = data;
      }
    }
    else {
      tag_ID = data.tag_id;

      if(!data.user_email){
        showUserInfo();
      }
      else if  (data.user_email == user_email){
            showUserInfo();
      }
      else{
            let user_info = document.getElementById("user_info");
            user_info.setAttribute("hidden", "hidden");
            document.getElementById("user_info").innerHTML = "Email addresses don't compare with you login data";
       }

      tag_timestamp = data.tag_timestamp;
    }
  });
}

function showUserInfo(){

    hideNoRecent();
    $("#user_info").css("display", "block");
    $("#user_info").css("visibility", "visible");
}
function showNoRecent(){
    hideUserInfo();
    $("#no_recent").css("display", "block");
    $("#user_info").css("visibility", "visible");
}

function hideUserInfo(){
    $("#user_info").css("display", "none");
    $("#user_info").css("visibility", "hidden");
}

function hideNoRecent(){
    $("#no_recent").css("display", "none");
    $("#user_info").css("visibility", "hidden");
}

function saveUser() {

    user_external_id = $('#user_id').val();

    params = 'user_name=' + user_name;
    params = params + '&user_surname=' + user_surname;
    params = params + '&user_email=' + user_email;
    params = params + '&user_external_id=' + user_external_id;
    params = params + '&tag_id=' + tag_ID;

    $.get("/insert_user_and_link2tag?" + params, function (data, status) {
        if (data.includes("http200OK")){
            $("#user_info").html("<h1>Insert succes</h1>");
        }else
        {
            $("#user_info").html("<h1>Insert Failed!</h1>");
        }
    });
}

function Logout(){
    $.get("/logout", function (data, status) {
            $("#user_info").html("You are logged out");
    });
}