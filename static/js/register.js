var g_devices = [];
var g_device = null;
var g_IsDirty = false;
var g_PreviousLog = null;
var g_UserIDs;
var g_Names;
var g_UserID;
var g_TagID = -1;
var g_User = null;

setInterval(PollDeviceLogs, 1700);

$(document).ready(function () {
  var searchInput = $("#lastName");

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

  $("#lastName").bind("typeahead:select", function (ev, suggestion) {
    let i = 0;

    while (i < g_Names.length) {
      if (g_Names[i] == suggestion) {
        g_UserID = g_UserIDs[i];
        fillOutUser();
      }
      i++;
    }
  });

  $.get("/get_devices", function (data, status) {
    g_devices = JSON.parse(data);
    updateDropDownDevices();
  });

  $("#name").on("input", function () {
    g_IsDirty = true;
  });

  $("#lastName").on("input", function () {
    g_IsDirty = true;
  });

  $("#email").on("input", function () {
    g_IsDirty = true;
  });

  $("#devices").on("change", function () {
    si = $("#devices").prop("selectedIndex");
    if (si > -1) {
      g_device = g_devices[si];
    } else {
      g_device = null;
    }
  });
});

//**************************************************************************** */
//*********************  End onLoad           ******************************** */
//**************************************************************************** */

function PollDeviceLogs() {
  if (!g_device) {
    return;
  }

  var param = "?id=" + g_device.ID;
  $.get("/get_most_recent_log" + param, function (data, status) {
    if (g_PreviousLog) {
      if (typeof data == "object") {
        if (g_PreviousLog.ID != data.ID) {
          g_IsDirty = false;
        }
      }
    }

    g_PreviousLog = data;

    if (!g_IsDirty) {
      if (typeof data == "object") {
        g_User = data;
        $("#name").val(data.user_name);
        $("#lastName").val(data.user_surname);
        $("#email").val(data.user_email);
        $("#externalID").val(data.user_external_ID);
        $("#lastScan").html(
          convertDate(data.tag_timestamp) +
            " " +
            convertTime(data.tag_timestamp)
        );
        $("#tagID").html(data.tag_id);
        g_TagID = data.tag_id;
        g_IsDirty = false;
      } else {
        $("#lastScan").html("No recent scan (<2 minutes)");
        $("#name").val("");
        $("#lastName").val("");
        $("#email").val("");
        $("#tagID").html("");
        g_TagID = -1;
        g_User = null;
      }
    }
  });
}

function fillOutUser() {
  param = "?field_name=ID&selection=" + g_UserID;
  $.get("/get_users" + param, function (data, status) {
    data = data[0];
    $("#name").val(data.user_name);
    $("#lastName").val(data.user_surname);
    $("#email").val(data.user_email);
    $("#externalID").val(data.user_external_ID);
  });
}

function Connect() {
  if (g_TagID >= 0) {
    param = "?tag_id=" + g_TagID;
    param = param + "&user_name=" + $("#name").val();
    param = param + "&user_surname=" + $("#lastName").val();
    param = param + "&user_external_id=" + $("#externalID").val();
    param = param + "&user_email=" + $("#email").val();
    $.get("/insert_user_and_link2tag" + param, function (data, status) {
      $("#name").val("");
      $("#lastName").val("");
      $("#email").val("");
      $("#tagID").html("");
      g_IsDirty = false;
      g_TagID = -1;
    });
  }
}

function Disconnect() {
  if (g_TagID >= 0) {
    param = "?tagID=" + g_TagID;
    $.get("/disconnectTagFromUser" + param, function (data, status) {
      $("#name").val("");
      $("#lastName").val("");
      $("#email").val("");
      $("#tagID").html("");
      g_IsDirty = false;
      g_TagID = -1;
    });
  }
}

function updateDropDownDevices() {
  $("#devices").empty();
  g_devices.forEach(function (item, index) {
    if (!item.device_name) {
      device_name = item.ID.toString();
    } else {
      device_name = item.device_name;
    }
    $("#devices").append(
      $("<option>", {
        value: item.ID,
        text: device_name,
      })
    );
  });
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
