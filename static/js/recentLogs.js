

function PollDeviceLogs() {


  $.get("/get_most_recent_logs?" , function (data, status) {

        jsonObject = JSON.parse(jsonString);

        tablstr =



        for (const item of jsonArray) {
            const row = document.createElement("tr");
            for (const key in item) {
                const cell = document.createElement("td");
                cell.textContent = item[key];
                row.appendChild(cell);
            }
            tableBody.appendChild(row);
        }


        document.getElementById("user_info").innerHTML = data;
  });
}

