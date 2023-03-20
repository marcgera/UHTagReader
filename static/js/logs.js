    var g_devices;
    var g_logs;

    $.get("/get_devices", function (data, status) {
        g_devices = data;
        updateDropDownDevices(g_devices);
    });

    function updateDropDownDevices(devices){
    $('#devices').empty();
    devices.forEach(function (item, index) {
        $('#devices').append($('<option>', {
            value: item.ID,
            text: item.device_name
        }));
      });
    }

    function doSearch(){

        var params = '';
        start_date = document.getElementById("start_date").value;
        end_date = document.getElementById("end_date").value;

        if (start_date.length == 10){
            params = params + 'start_time=' + convertDateToInt(start_date) + '000000' + '&'
        }

        if (end_date.length == 10){
            params = params + 'end_time=' + convertDateToInt(end_date) +  '235959' + '&'
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

    function convertDateToInt(dateString){
          datestr = dateString.substring(6,10) + dateString.substring(3,5) + dateString.substring(0,2)
            return datestr;
    }