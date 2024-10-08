var g_devices = [];
var g_device = null;
var g_groups = [];
var g_group = null;
var g_Names = [];
var g_UserIDs;
var g_UserID = -1;

$(document).ready(function () {
  var searchInput = $("#last_name");

  DownLoadEnable(false);

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
        g_UserID = g_UserIDs[i];
      }
      i++;
    }
  });

  $.get("/get_devices", function (data, status) {
    g_devices = JSON.parse(data);
    updateDropDownDevices(g_devices);
  });

  $.get("groups/getList", function (data, status) {
    g_groups = JSON.parse(data);
    updateGroupsList();
  });

  function updateDropDownDevices(devices) {
    $("#devices").empty();
    devices.forEach(function (item, index) {
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

  $("#deviceCheckbox").change(function () {
    if ($(this).is(":checked")) {
      $("#devices").prop("disabled", true);
      $("#devices").prop("selectedIndex", -1);
    } else {
      $("#devices").prop("disabled", false);
    }
  });

  $("#userCheckbox").change(function () {
    if ($(this).is(":checked")) {
      $("#last_name").prop("disabled", true);
      $("#last_name").val("");
      g_UserID = -1;
    } else {
      $("#last_name").prop("disabled", false);
    }
  });

  $("#groupCheckbox").change(function () {
    if ($(this).is(":checked")) {
      $("#groupsList").prop("disabled", true);
      $("#groupsList").selectedIndex = -1;
      g_group = null;
    } else {
      $("#groupsList").prop("disabled", false);
    }
  });

  $("#groupsList").on("change", function () {
    si = $("#groupsList").prop("selectedIndex");
    if (si > -1) {
      g_group = g_groups[si];
    } else {
      g_group = null;
    }
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

function updateGroupsList(selectLast = false) {
  groupsList = $("#groupsList");
  groupsList.empty();
  g_groups.forEach(function (item, index) {
    groupsList.append(
      $("<option>", {
        value: item.ID,
        text:
          item.group_name + " - " + item.user_name + " " + item.user_surname,
      })
    );
  });
  if (selectLast) {
    groupsList.scrollTop(groupsList[0].scrollHeight);
    groupsList.selectedIndex = g_groups.length - 1;
    g_SelectedGroup = g_groups[g_groups.length - 1];
    fillOutGroup(g_SelectedGroup);
  }
}

function convertDateToInt(dateString) {
  datestr =
    dateString.substring(6, 10) +
    dateString.substring(3, 5) +
    dateString.substring(0, 2);
  return datestr;
}

function doSearch() {
  DownLoadEnable(false);

  var params = "";

  start_date = document.getElementById("start_date").value;
  end_date = document.getElementById("end_date").value;

  if (start_date.length == 10) {
    params =
      params +
      "start_time_stamp=" +
      convertDateToInt(start_date) +
      "000000" +
      "&";
  }

  if (end_date.length == 10) {
    params =
      params + "stop_time_stamp=" + convertDateToInt(end_date) + "235959" + "&";
  }

  if (g_device) {
    params = params + "device_id=" + g_device.ID.toString();
  } else {
    params = params + "device_id=-1";
  }

  if (g_group) {
    params = params + "&group_id=" + g_group.ID.toString();
    call = "/generateReportStyle2?";
  } else {
    params = params + "&user_id=" + g_UserID.toString();
    call = "/generateReportStyle1?";
  }

  $.get(call + params, function (data, status) {
    if (data.includes(".xlsx")) {
      $("#download").attr("href", data);
      $("#myToast").toast("show");
      DownLoadEnable(true);
    } else if (data.includes("Query contains no data")) {
      $("#myToast").toast(data);
    } else {
      g_logs = JSON.parse(data);
      //updateLogs()
    }
  });
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

function doFillInStopStart(kind) {
  const currentDate = new Date();
  // Use the getFullYear() method to get the four-digit year
  currentYear = currentDate.getFullYear();

  if (kind == 1) {
    dateStringStart = "15/09/" + String(currentYear - 1);
    dateStringStop = "31/06/" + String(currentYear);
  } else if (kind == 2) {
    dateStringStart = "01/01/" + String(currentYear);
    dateStringStop = "31/12/" + String(currentYear);
  }

  $("#start_date").val(dateStringStart);
  $("#end_date").val(dateStringStop);
}
