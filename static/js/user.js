var user;

function loadUser(){

    $.get("/get_user", function (data, status) {
        user = JSON.parse(data);

        $('#user_email').html(user_email);
        $('#user_name').html(user_name);
        $('#user_surname').html(user_surname);

        if (user.user_picture_url == "")
        {
            $('#profile_picture').attr('src','/static/images/Generic-Profile-Image.png');
        } else
        {
            $('#profile_picture').attr('src', user.user_picture_url);
        }

        $('#card_title').html(user.name + ' ' + user.surname);
        $('#card_text').html(user.email + '<br>' + user.external_ID);

    });
}