var g_admins = null;
var g_SelectedAdmin = null;
var g_UserID = -1;
var g_Names = [];
var g_UserIDs;


$(document).ready(function () {

    var searchInput = $('#last_name');

    function initTypeAhead() {
        searchInput.typeahead({
            hint: true,
            highlight: true,
            minLength: 1
        },
            {
                name: 'lastnames',
                source: function (query, syncResults, asyncResults) {
                    $.ajax({
                        url: '/get_last_names', // Replace with your backend endpoint
                        data: {
                            name_start: query
                        },
                        dataType: 'json',
                        success: function (data) {
                            // Assuming data is an array of suggestions
                            g_Names = data.names;
                            g_UserIDs = data.IDs;
                            asyncResults(g_Names);
                        },
                        error: function () {
                            asyncResults([]);
                        }
                    });
                }
            });

        $('#last_name').bind('typeahead:select', function (ev, suggestion) {
            let i = 0;

            while (i < g_Names.length) {
                if (g_Names[i] == suggestion) {
                    g_UserID = g_UserIDs[i];
                }
                i++;
            }
        });

    }

    initTypeAhead();


    $.get("/get_admins", function (data, status) {
        g_admins = JSON.parse(data);
        updateAdminsList();
    });

    function updateAdminsList() {
        $('#adminList').empty();
        g_admins.forEach(function (item, index) {
            $('#adminList').append($('<option>', {
                value: item.ID,
                text: item.user_surname + ' ' + item.user_name
            }));
        });
    }

    $('#adminList').change(function () {
        var selectedIndex = $('#adminList').prop('selectedIndex');
        if (selectedIndex >= 0) {
            g_SelectedAdmin = g_admins[selectedIndex];
            fillOutAdmin();
        }
        else {
            g_SelectedAdmin = null;
        }
    });
});


function doSelectAdmin() {
    alert(g_UserID);
}

function convertDateToInt(dateString) {
    datestr = dateString.substring(6, 10) + dateString.substring(3, 5) + dateString.substring(0, 2)
    return datestr;
}

function DownLoadEnable(value) {
    var downloadButton = $('#download');

    if (value) {
        downloadButton.prop('disabled', false); // Enable the button
        downloadButton.addClass('btn-primary'); // Restore the primary color
        downloadButton.removeClass('btn-secondary'); // Remove the gray color
    }
    else {
        downloadButton.prop('disabled', true); // Disable the button
        downloadButton.addClass('btn-secondary'); // Change color to gray
        downloadButton.removeClass('btn-primary'); // Remove the primary color
    }
}




