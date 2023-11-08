setInterval(PollDeviceLogs, 1700);

function PollDeviceLogs() {

    const tableBody = document.getElementById("table-body");

    tableContent = "";

    $.get("/get_most_recent_logs?", function (data, status) {

        data = JSON.parse(data);

        for (const item of data) {

            tableRow = '<tr>';

            colCounter = 0;
            for (const key in item) {
                colCounter = colCounter + 1;
                if (colCounter != 7) {
                    tableRow = tableRow + '<td>' + item[key] + '</td>';
                }
                else {
                    link = "<a href = https://uhtagtools.lm.r.appspot.com/qrdevice?id=" + item[key] + ">";
                    link = link + item[key];
                    link = link + "</a>"
                    tableRow = tableRow + '<td>' + link + '</td>';
                }
            }
            if (item.userID) {
                buttonHTML = "<button onclick='Disconnect("  + item.tag_id.toString() + ");'>Disconnect</button>";
                tableRow = tableRow + "<td>" + buttonHTML + "</td>";
            }
            else{
                tableRow = tableRow + "<td></td>";
            }

            tableRow = tableRow + '</tr>';
            tableContent = tableContent + tableRow;
        }

        tableBody.innerHTML = tableContent;

    });
}

function Disconnect(tagID) {
    params = "tagID=" + tagID.toString();

    $.get("/disconnectTagFromUser?" + params, function (data, status) {
        
    });
}
