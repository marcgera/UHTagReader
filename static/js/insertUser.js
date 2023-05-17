

function saveUser() {

    user_name = $('#user_name').val();
    user_surname = $('#user_surname').val();
    user_external_id = $('#user_id').val();
    user_email = $('#user_email').val();

    params = 'user_name=' + user_name;
    params = params + '&user_surname=' + user_surname;
    params = params + '&user_email=' + user_email;
    params = params + '&user_external_id=' + user_external_id;
    params = params + '&tag_id=' + tag_id;

    $.get("/insert_user_and_link2tag?" + params, function (data, status) {
        $('#userModal').modal('hide');
    });
    }
}