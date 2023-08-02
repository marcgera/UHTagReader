var user;

function loadUser(){

    $.get("/get_user", function (data, status) {
        user = JSON.parse(data);

        $('#user_email').html(user.email);
        $('#user_name').html(user.name);
        $('#user_surname').html(user.surname);

    });
}