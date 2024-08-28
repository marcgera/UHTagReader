var g_groups = null;
var g_SelectedGroup = null;
var g_UserID = -1;
var g_Names = [];
var g_UserIDs;
var g_Members = [];
var g_CurrentUser = null;


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
                    AddMemberEnable(true);
                }
                i++;
            }
        });

    }

    initTypeAhead();


    $.get("getCurrentUser", function (data, status) {
        g_CurrentUser = data;
    });

    $.get("groups/getList", function (data, status) {
        g_groups = JSON.parse(data);
        updateGroupsList();
    });



    $('#groupsList').change(function () {
        var selectedIndex = $('#groupsList').prop('selectedIndex');
        if (selectedIndex >= 0) {
            g_SelectedGroup = g_groups[selectedIndex];
            fillOutGroup(g_SelectedGroup);
        }
        else {
            g_SelectedGroup = null;
        }
    });
});

function updateGroupsList() {
    $('#groupsList').empty();
    g_groups.forEach(function (item, index) {
        $('#groupsList').append($('<option>', {
            value: item.ID,
            text: item.group_name + ' - ' + item.user_name + ' ' + item.user_surname
        }));
    });
}

function fillOutGroup(currentGroup){
    $("#publicly_visible").prop('checked', false);
    $("#publicly_editable").prop('checked', false);
    $("#publicly_visible").prop('disabled', true);
    $("#publicly_editable").prop('disabled', true);
    $("#saveGroup").prop('disabled', true);
    $("#removeGroup").prop('disabled', true);
    $("#saveGroup").addClass('disabled'); 
    $("#removeGroup").addClass('disabled'); 
    $('#group_name').prop('disabled', true);


    if(g_CurrentUser.ID == currentGroup.group_owner_id){
        $('#group_name').prop('disabled', false);
        $("#publicly_visible").prop('disabled', false);
        $("#publicly_editable").prop('disabled', false);
        $("#saveGroup").prop('disabled', false);
        $("#removeGroup").prop('disabled', false);
        $("#saveGroup").removeClass('disabled'); 
        $("#removeGroup").removeClass('disabled'); 
    }

    $("#group_name").val(currentGroup.group_name);

    if (currentGroup.group_is_public == 1){
        $("#publicly_visible").prop('checked', true);
    }
    if (currentGroup.group_is_editable == 1){
        $("#publicly_editable").prop('checked', true);
        $('#group_name').prop('disabled', false);
        $("#publicly_editable").prop('disabled', false);
    }

    var param = "?group_ID=" + currentGroup.ID;
    $.get("/groups/getMembers" + param, function (data, status) {
        g_members = JSON.parse(data);
        fillMemberList();
    });


}


function addMember(){
    AddMemberEnable(false);
    $("#last_name").val("");
}

function AddMemberEnable(value){
    element = $("#addMember");

    if (value){
        element.prop('disabled', false);
        element.removeClass('disabled'); 
    }
    else{
        element.prop('disabled', true);
        element.addClass('disabled'); 
    }
}

function fillMemberList(){
    $('#groupsMembers').empty();
    g_members.forEach(function (item, index) {
        $('#groupsMembers').append($('<option>', {
            value: item.ID,
            text: item.user_name + ' ' + item.user_surname
        }));
    });

}

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




