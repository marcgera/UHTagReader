var g_events = null;
var g_SelectedEvent = null;
var g_UserID = -1;
var g_Names = [];
var g_UserIDs;
var g_Members = [];
var g_CurrentUser = null;
var g_MemberID2Add = null;
var g_MemberID2Remove = null;

$(document).ready(function () {
  var searchInput = $("#last_name");

  function initTypeAhead() {
    searchInput.typeahead(
      {
        hint: true,
        highlight: true,
        minLength: 1,
      },
      {
        name: "lastnames",
        source: function (query, syncResults, asyncResults) {
          $.ajax({
            url: "/get_last_names", // Replace with your backend endpoint
            data: {
              name_start: query,
            },
            dataType: "json",
            success: function (data) {
              // Assuming data is an array of suggestions
              g_Names = data.names;
              g_UserIDs = data.IDs;
              asyncResults(g_Names);
            },
            error: function () {
              asyncResults([]);
            },
          });
        },
      }
    );

    $("#last_name").bind("typeahead:select", function (ev, suggestion) {
      let i = 0;

      while (i < g_Names.length) {
        if (g_Names[i] == suggestion) {
          g_MemberID2Add = g_UserIDs[i];
          AddMemberEnable(true);
        }
        i++;
      }
    });
  }

  initTypeAhead();
  loadEvents();

  $.get("getCurrentUser", function (data, status) {
    g_CurrentUser = data;
  });

  $("#Include_public").change(function () {
    loadGroups();
  });

  $("#eventList").change(function () {
    var selectedIndex = $("#eventList").prop("selectedIndex");
    if (selectedIndex >= 0) {
      g_SelectedEvent = g_events[selectedIndex];
      fillOutEvent(g_SelectedEvent);
    } else {
      g_SelectedEvent = null;
    }
  });

  $("#groupsMembers").change(function () {
    var selectedIndex = $("#groupsMembers").prop("selectedIndex");
    if (selectedIndex >= 0) {
      g_MemberID2Remove = g_Members[selectedIndex];
      removeMemberEnable(true);
    } else {
      g_MemberID2Remove = null;
      removeMemberEnable(fasle);
    }
  });

  AddMemberEnable(false);
  removeMemberEnable(false);
});

function loadEvents(ID2Select = -1) {
  const include_public_groups = $("#Include_public").prop("checked");
  if (include_public_groups) {
    params = "?include_public=true";
  } else {
    params = "?include_public=false";
  }

  $.get("events/getList" + params, function (data, status) {
    g_events = JSON.parse(data);
    updateEventList();
    if (ID2Select > -1) {
      g_events.forEach(function (item, index) {
        if (item.ID == ID2Select) {
          g_SelectedEvent = item;
          let eventList = document.getElementById("eventList");
          eventList.value = ID2Select;
          eventList.scrollIntoView({
            behavior: "smooth",
            block: "center",
          });
          fillOutEvent(g_SelectedEvent);
        }
      });
    }
  });
}

function updateEventList(selectLast = false, include_public = false) {
  eventList = $("#eventList");

  eventList.empty();
  g_events.forEach(function (item, index) {
    eventList.append(
      $("<option>", {
        value: item.ID,
        text:
          item.event_name +
          " - " +
          item.user_name +
          " " +
          item.user_surname +
          " (" +
          item.nrOfMembers +
          ")",
      })
    );
  });
  if (selectLast) {
    eventList.scrollTop(eventList[0].scrollHeight);
    eventList.selectedIndex = g_events.length - 1;
    g_SelectedEvent = g_events[g_events.length - 1];
    fillOutEvent(g_SelectedEvent);
  }
}

function fillOutEvent(currentEvent) {
  $("#publicly_visible").prop("checked", false);
  $("#publicly_editable").prop("checked", false);
  $("#publicly_visible").prop("disabled", true);
  $("#publicly_editable").prop("disabled", true);
  $("#saveGroup").prop("disabled", true);
  $("#removeGroup").prop("disabled", true);
  $("#saveGroup").addClass("disabled");
  $("#removeGroup").addClass("disabled");
  $("#event_name").prop("disabled", true);

  if (g_CurrentUser.ID == currentEvent.group_owner_id) {
    $("#group_name").prop("disabled", false);
    $("#publicly_visible").prop("disabled", false);
    $("#publicly_editable").prop("disabled", false);
    $("#saveGroup").prop("disabled", false);
    $("#removeGroup").prop("disabled", false);
    $("#saveGroup").removeClass("disabled");
    $("#removeGroup").removeClass("disabled");
  }

  $("#event_name").val(currentEvent.event_name);

  if (currentEvent.event_is_public == 1) {
    $("#publicly_visible").prop("checked", true);
  }
  if (currentEvent.event_is_editable == 1) {
    $("#publicly_editable").prop("checked", true);
    $("#event_name").prop("disabled", false);
    $("#publicly_editable").prop("disabled", false);
  }

  var param = "?event_ID=" + currentEvent.ID;
  $.get("/events/getMembers" + param, function (data, status) {
    g_Members = JSON.parse(data);
    fillMemberList();
  });
  updateGroupButtons();
}

function addMember() {
  var param = "?group_ID=" + g_SelectedGroup.ID + "&user_ID=" + g_MemberID2Add;
  $.get("/groups/addMember" + param, function (data, status) {});
}

function containsNumeric(value) {
  return !isNaN(parseFloat(value)) && isFinite(value);
}

function removeMember() {
  var param = "?group_member_ID=" + g_MemberID2Remove.ID;
  $.get("/groups/removeMember" + param, function (data, status) {
    g_Members = JSON.parse(data);
    fillMemberList();
    AddMemberEnable(false);
    removeMemberEnable(false);
    $("#last_name").val("");
    g_MemberID2Add = null;
    g_MemberID2Remove = null;
    elem.scrollTop(elem[0].scrollHeight);
  });
}

function AddMemberEnable(value) {
  element = $("#addMember");

  if (value) {
    element.prop("disabled", false);
    element.removeClass("disabled");
  } else {
    element.prop("disabled", true);
    element.addClass("disabled");
  }
}

function removeMemberEnable(value) {
  element = $("#removeMember");

  if (value) {
    element.prop("disabled", false);
    element.removeClass("disabled");
  } else {
    element.prop("disabled", true);
    element.addClass("disabled");
  }
}

function RemoveGroupEnable(value) {
  element = $("#removeGroup");

  if (value) {
    element.prop("disabled", false);
    element.removeClass("disabled");
  } else {
    element.prop("disabled", true);
    element.addClass("disabled");
  }
}

function SaveGroupEnable(value) {
  element = $("#saveGroup");

  if (value) {
    element.prop("disabled", false);
    element.removeClass("disabled");
  } else {
    element.prop("disabled", true);
    element.addClass("disabled");
  }
}

function addEvent() {
  var param = "?name=newEvent&is_public=0&owner_ID=" + g_CurrentUser.toString();
  $.get("/events/add" + param, function (data, status) {
    if (containsNumeric(data)) {
      loadEvents(parseInt(data));
    }
  });
}

function removeEvent() {
  var param = "?event_ID=" + g_SelectedEvent.ID;
  $.get("/events/remove" + param, function (data, status) {
    if (data == "http200OK") {
      loadEvents(-1);
    }
  });
}

function saveGroup() {
  const publicly_visible = $("#publicly_visible").prop("checked");
  const publicly_editable = $("#publicly_editable").prop("checked");

  var param = "?group_ID=" + g_SelectedGroup.ID;
  param = param + "&name=" + $("#group_name").val();

  if (publicly_visible) {
    param = param + "&is_public=1";
  } else {
    param = param + "&is_public=0";
  }

  if (publicly_editable) {
    param = param + "&is_editable=1";
  } else {
    param = param + "&is_editable=0";
  }

  $.get("/events/edit" + param, function (data, status) {
    g_groups = JSON.parse(data);
    updateEventList(false);
  });
}

function updateGroupButtons() {
  if (g_SelectedGroup) {
    if (g_SelectedGroup.group_owner_id != g_CurrentUser.ID) {
      SaveGroupEnable(false);
      RemoveGroupEnable(false);
    } else {
      SaveGroupEnable(true);
      RemoveGroupEnable(true);
    }
  } else {
    SaveGroupEnable(false);
    RemoveGroupEnable(false);
  }
}

function fillMemberList() {
  $("#groupsMembers").empty();
  index = 1;
  g_Members.forEach(function (item, index) {
    $("#groupsMembers").append(
      $("<option>", {
        value: item.ID,
        text: index.toString() + " " + item.user_name + " " + item.user_surname,
      })
    );
    index++;
  });
}

function doSelectAdmin() {
  alert(g_UserID);
}

function convertDateToInt(dateString) {
  datestr =
    dateString.substring(6, 10) +
    dateString.substring(3, 5) +
    dateString.substring(0, 2);
  return datestr;
}

function DownLoadEnable(value) {
  var downloadButton = $("#download");

  if (value) {
    downloadButton.prop("disabled", false); // Enable the button
    downloadButton.addClass("btn-primary"); // Restore the primary color
    downloadButton.removeClass("btn-secondary"); // Remove the gray color
  } else {
    downloadButton.prop("disabled", true); // Disable the button
    downloadButton.addClass("btn-secondary"); // Change color to gray
    downloadButton.removeClass("btn-primary"); // Remove the primary color
  }
}
