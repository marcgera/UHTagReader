//window.setInterval(doRepeatSearch, 5000);

var g_devices;
var g_logs;
var g_selectedLog;
var g_SelectedTagID;
var g_UserID;

$.get("/get_devices", function (data, status) {
    g_devices = data;
    updateDropDownDevices(g_devices);
});

function updateDropDownDevices(devices) {
    $('#devices').empty();
    devices.forEach(function (item, index) {
        $('#devices').append($('<option>', {
            value: item.ID,
            text: item.device_name
        }));
    });
}

function doRepeatSearch() {
    if (g_logs) {
        doSearch();
    }
}

function doSearch() {

    var params = '';
    start_date = document.getElementById("start_date").value;
    end_date = document.getElementById("end_date").value;

    if (start_date.length == 10) {
        params = params + 'start_time=' + convertDateToInt(start_date) + '000000' + '&'
    }

    if (end_date.length == 10) {
        params = params + 'end_time=' + convertDateToInt(end_date) + '235959' + '&'
    }

    si = document.getElementById("devices").selectedIndex;
    if (si > -1) {
        params = params + 'device_id=' + g_devices[si].ID;
    }

    $.get("/get_logs?" + params, function (data, status) {
        g_logs = data;
        updateLogs()
    });
}

function convertDateToInt(dateString) {
    datestr = dateString.substring(6, 10) + dateString.substring(3, 5) + dateString.substring(0, 2)
    return datestr;
}

function updateLogs() {

    $('#loglist').empty();
    rows = '';
    g_logs.forEach(function (item, index) {
        rows = rows + generateRow(index, item.tagID, item.datestr, item.timestr, item.user_name, item.user_surname, item.user_id);
    });

    logsElem = document.getElementById('loglist');
    logsElem.innerHTML = rows;

}

function generateRow(rownr, tagID, dateStr, timeStr, name, surname, userID) {

    styleStr = 'bg-white text-dark';
    if (rownr % 2 == 0) {
        styleStr = ' bg-light text-dark';
    }
    rowstr = '<div class="row">';
    rowstr = rowstr + '<div class="col-1 ' + styleStr + '">' + rownr.toString() + '</div>';
    rowstr = rowstr + '<div class="col-2 ' + styleStr + '">' + tagID.toString() + '</div>';
    rowstr = rowstr + '<div class="col-2 ' + styleStr + '">' + dateStr + '</div>';
    rowstr = rowstr + '<div class="col-1 ' + styleStr + '">' + timeStr + '</div>';
    rowstr = rowstr + '<div class="col-2 ' + styleStr + '">' + surname + '</div>';
    rowstr = rowstr + '<div class="col-1 ' + styleStr + '">' + name + '</div>';

    if (userID == null) {
        userID = -1;
    }

    g_UserID = userID;

    onclickStr = ' onclick = editUser(' + tagID.toString() + ',' + userID.toString() + ')';
    buttonStr = '<button type="button" class="btn btn-primary btn-sm"' + onclickStr + '>Edit</button>';

    rowstr = rowstr + '<div class="col-1 ' + styleStr + '">' + buttonStr + '</div>';
    rowstr = rowstr + '</div>'
    return rowstr;

}

function editUser(tagID, userID) {
    g_SelectedTagID = tagID;
    g_UserID = userID;

    g_logs.forEach(function (item, index) {
        if(item.tagID==tagID){
            g_selectedLog = item;
        }
    });

    if (userID>-1){
        $('#user_name').val(g_selectedLog.user_name);
        $('#user_surname').val(g_selectedLog.user_surname);
        $('#user_id').val(g_selectedLog.user_external_id);
        $('#user_email').val(g_selectedLog.user_email);
    }
    $('#userModal').modal('show');
}

function HideModal() {
    $('#userModal').modal('hide');
}

function updateUser() {
    user_name = $('#user_name').val();
    user_surname = $('#user_surname').val();
    user_external_id = $('#user_id').val();
    user_email = $('#user_email').val();

    params = '?user_id=' + g_UserID.toString();
    params = params + '&user_name=' + user_name;
    params = params + '&user_surname=' + user_surname;
    params = params + '&user_email=' + user_email;
    params = params + '&user_external_id=' + user_external_id;

    $.get("/update_user?" + params, function (data, status) {
        $('#userModal').modal('hide');
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

    if (g_UserID > -1) {
        params = params + '&user_id=' + g_UserID.toString();
        $.get("/update_user?" + params, function (data, status) {
            $('#userModal').modal('hide');
        });
    } else {

        params = params + '&tag_id=' + g_SelectedTagID.toString();
        $.get("/insert_user_and_link2tag?" + params, function (data, status) {
            $('#userModal').modal('hide');
        });
    }

}