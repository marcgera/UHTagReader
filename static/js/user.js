var user;
var tag_ID;

function loadUser(){

    //$("#user_info").hide();
    //$("#no_recent").hide();

    hideUserInfo();
    hideNoRecent();

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
      $("#message").html = "No recent scan detected... Please present your tag and reload this page or rescan the QR code.";
            hideUserInfo();
            showNoRecent();
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
            $("#message").html("Email addresses don't compare with you login data");
            showNoRecent();
       }

      tag_timestamp = data.tag_timestamp;
    }
  });
}

function showUserInfo(){
    hideNoRecent();
    let element = document.getElementById("user_info");
    element.removeAttribute("hidden")
}
function showNoRecent(){
    hideUserInfo();
    let element = document.getElementById("no_recent");
    element.removeAttribute("hidden")
}

function hideUserInfo(){
    let element = document.getElementById("user_info");
    element.setAttribute("hidden", "hidden");
}

function hideNoRecent(){
    let element = document.getElementById("no_recent");
    element.setAttribute("hidden", "hidden");
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

function Logout(){
    $.get("/logout", function (data, status) {
            $("#user_info").hide();
            $("#message").html("You are logged out");
            showNoRecent();
    });
}