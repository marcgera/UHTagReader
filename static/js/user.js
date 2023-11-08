var user;


function loadUser() {


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

    if (isNaN(tag_id)) {
        if (tag_id.includes("No recent")) {
            document.getElementById("user_info").innerHTML = data;
        }else{
            tag_id=tag_id.toString();
        }
    }
    else {

        if (!tag_Linked_to_User_Email || tag_Linked_to_User_Email == "None") {
            showUserInfo();
        }
        else if (tag_Linked_to_User_Email == user_email) {
            showUserInfo();
        }
        else {
            let user_info = document.getElementById("user_info");
            document.getElementById("user_info").innerHTML = "Email addresses don't compare with you login data. ("
                + user_email + " <> " + tag_Linked_to_User_Email + ")";
        }


    }

}

function showUserInfo() {

    hideNoRecent();
    $("#user_info").css("display", "block");
    $("#user_info").css("visibility", "visible");
}
function showNoRecent() {
    hideUserInfo();
    $("#no_recent").css("display", "block");
    $("#user_info").css("visibility", "visible");
}

function hideUserInfo() {
    $("#user_info").css("display", "none");
    $("#user_info").css("visibility", "hidden");
}

function hideNoRecent() {
    $("#no_recent").css("display", "none");
    $("#user_info").css("visibility", "hidden");
}

function saveUser() {

    user_external_id = $('#user_id').val();

    params = 'user_name=' + user_name;
    params = params + '&user_surname=' + user_surname;
    params = params + '&user_email=' + user_email;
    params = params + '&user_external_id=' + user_external_id;
    params = params + '&tag_id=' + tag_id;

    $.get("/insert_user_and_link2tag?" + params, function (data, status) {
        if (data.includes("http200OK")) {
            $("#user_info").html("<h1>Insert succes</h1>");
        } else {
            $("#user_info").html("<h1>Insert Failed!</h1>");
        }
    });
}

function Logout() {
    $.get("/logout", function (data, status) {
        $("#user_info").html("You are logged out");
    });
}