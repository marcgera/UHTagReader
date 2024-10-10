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

  $("#start_date").datepicker({
    format: "dd/mm/yyyy",
  });
  $("#end_date").datepicker({
    format: "dd/mm/yyyy",
  });

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
  $("#saveEvent").prop("disabled", true);
  $("#removeEvent").prop("disabled", true);
  $("#saveEvent").addClass("disabled");
  $("#removeEvent").addClass("disabled");
  $("#event_name").prop("disabled", true);
  $("#start_date").prop("disabled", true);
  $("#end_date").prop("disabled", true);
  $("#start_time").prop("disabled", true);
  $("#end_time").prop("disabled", true);

  if (g_CurrentUser.ID == currentEvent.event_owner_id) {
    $("#event_name").prop("disabled", false);
    $("#publicly_visible").prop("disabled", false);
    $("#publicly_editable").prop("disabled", false);
    $("#saveEvent").prop("disabled", false);
    $("#removeEvent").prop("disabled", false);
    $("#saveEvent").removeClass("disabled");
    $("#removeEvent").removeClass("disabled");
    $("#start_date").prop("disabled", false);
    $("#end_date").prop("disabled", false);
    $("#start_time").prop("disabled", false);
    $("#end_time").prop("disabled", false);
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

  $("#start_date").val(convertDate(currentEvent.event_start_datetime));
  $("#end_date").val(convertDate(currentEvent.event_end_datetime));
  $("#start_time").val(convertTime(currentEvent.event_start_datetime));
  $("#end_time").val(convertTime(currentEvent.event_end_datetime));

  var param = "?event_ID=" + currentEvent.ID;
  $.get("/events/getMembers" + param, function (data, status) {
    g_Members = JSON.parse(data);
    fillMemberList();
  });
  updateGroupButtons();
}

function addMember() {
  var param = "?event_ID=" + g_SelectedEvent.ID + "&user_ID=" + g_MemberID2Add;
  $.get("/events/addMember" + param, function (data, status) {
    g_Members = JSON.parse(data);
    fillMemberList();
    AddMemberEnable(false);
    removeMemberEnable(false);
    $("#last_name").val("");
    g_MemberID2Add = null;
    g_MemberID2Remove = null;
    elem = $("#eventMembers");
    elem.scrollTop(elem[0].scrollHeight);
  });
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

function saveEvent() {
  const publicly_visible = $("#publicly_visible").prop("checked");
  const publicly_editable = $("#publicly_editable").prop("checked");

  var dateStrStart = $("#start_date").val();
  var dateStrEnd = $("#end_date").val();
  var timeStrStart = $("#start_time").val();
  var timeStrEnd = $("#end_time").val();

  var startTS = convertToInt(dateStrStart, timeStrStart);
  var endTS = convertToInt(dateStrEnd, timeStrEnd);

  var param = "?event_ID=" + g_SelectedEvent.ID;
  param = param + "&name=" + $("#event_name").val();

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

  param = param + "&event_start_datetime=" + startTS;
  param = param + "&event_end_datetime=" + endTS;

  $.get("/events/edit" + param, function (data, status) {
    loadEvents(g_SelectedEvent.ID);
  });
}

function convertToInt(dateStr, timeStr) {
  dateParts = dateStr.split("/");
  timeParts = timeStr.split(":");
  if (dateParts.length != 3) {
    alert("Date needs to be in DD/MM/YYYY format");
    return false;
  }

  if (timeParts.length != 2) {
    alert("Time needs to be in HH:mm format");
    return false;
  }

  const day = parseInt(dateParts[0], 10);
  const month = parseInt(dateParts[1], 10);
  const year = parseInt(dateParts[2], 10);
  const hour = parseInt(timeParts[0], 10);
  const minute = parseInt(timeParts[1], 10);

  // Check if the year is valid
  if (year < 1000 || year > 9999) {
    alert("Invalid year. Year must be a 4-digit number.");
    return false;
  }

  // Check if the month is valid
  if (month < 1 || month > 12) {
    alert("Invalid month. Month must be between 1 and 12.");
    return false;
  }

  const paddedDay = String(day).padStart(2, "0"); // Ensure day is two digits
  const paddedMonth = String(month).padStart(2, "0"); // Ensure month is two digits
  const paddedHour = String(hour).padStart(2, "0");
  const paddedMinute = String(minute).padStart(2, "0");
  dateStr = `${year}${paddedMonth}${paddedDay}`;
  timeStr = `${paddedHour}${paddedMinute}00`;
  return dateStr + timeStr;
}

function updateGroupButtons() {
  if (g_SelectedEvent) {
    if (g_SelectedEvent.eventowner_ID != g_CurrentUser.ID) {
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
  $("#eventMembers").empty();
  index = 1;
  g_Members.forEach(function (item, index) {
    $("#eventMembers").append(
      $("<option>", {
        value: item.ID,
        text: index.toString() + " " + item.user_name + " " + item.user_surname,
      })
    );
    index++;
  });
  Participants_str = "Participants (" + g_Members.length.toString() + ")";
  elem = $("#participants");
  elem.html(Participants_str);
}

function doSelectAdmin() {
  alert(g_UserID);
}

function convertDate(intDate) {
  // Convert the integer to a string
  const dateString = intDate.toString();

  // Extract year, month, and day
  const year = dateString.substring(0, 4);
  const month = dateString.substring(4, 6);
  const day = dateString.substring(6, 8);

  // Format the date as dd/mm/yyyy
  return `${day}/${month}/${year}`;
}

function convertTime(intDate) {
  // Convert the integer to a string
  const dateString = intDate.toString();

  // Extract year, month, and day
  const HH = dateString.substring(8, 10);
  const mm = dateString.substring(10, 12);

  // Format the date as dd/mm/yyyy
  return `${HH}:${mm}`;
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
