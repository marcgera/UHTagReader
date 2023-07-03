
var g_users

function fieldChanged(field_name){

    if (field_name == 'user_name'){
        selection = document.getElementById("first_name").value;
    }
    else
    {
        selection = document.getElementById("last_name").value;
    }

    params =  'field_name=' + field_name;
    params = params + '&selection=' + selection + "%";

    $.get("/get_users?" + params, function (data, status) {
        g_users = data;
    });

}