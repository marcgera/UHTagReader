//window.setInterval(doRepeatSearch, 5000);

var g_devices;
var g_logs;
var g_SelectedTagID;

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

function doRepeatSearch(){
    if (g_logs){
        doSearch() ;
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
        rows = rows + generateRow(index, item.tagID, item.datestr, item.timestr, item.user_name, item.user_surname);
    });

    logsElem = document.getElementById('loglist');
    logsElem.innerHTML = rows;
    
}

function generateRow(rownr, tagID,  dateStr, timeStr, name, surname) {
    
    styleStr = 'bg-white text-dark';
    if(rownr % 2 == 0) {
        styleStr = ' bg-light text-dark';
    }
    rowstr = '<div class="row">';
    rowstr = rowstr + '<div class="col-1 ' + styleStr + '">' + rownr.toString() + '</div>';
    rowstr = rowstr + '<div class="col-2 ' + styleStr + '">' + tagID.toString() + '</div>';
    rowstr = rowstr + '<div class="col-2 ' + styleStr + '">' + dateStr + '</div>';
    rowstr = rowstr + '<div class="col-1 ' + styleStr + '">' + timeStr + '</div>';
    rowstr = rowstr + '<div class="col-2 ' + styleStr + '">' + surname + '</div>';
    rowstr = rowstr + '<div class="col-1 ' + styleStr + '">' + name + '</div>';

    onclickStr = ' onclick = editUser(' + tagID.toString() + ')';
    buttonStr = '<button type="button" class="btn btn-primary btn-sm"' + onclickStr +  '>Edit</button>';

    rowstr = rowstr + '<div class="col-1 ' + styleStr + '">' + buttonStr + '</div>';
    rowstr = rowstr + '</div>'
    return rowstr;

}

function editUser(tagID){
    g_SelectedTagID = tagID;
    $('#userModal').modal('show');

}

function saveUser(){
    user_name = $('#user_name').val();
    user_surname = $('#user_surname').val();
    user_id = $('#user_id').val();
}