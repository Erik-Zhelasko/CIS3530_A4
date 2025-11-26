let database;
let url = "/API/manager_overview";
function loadMOverview() {
    const element = document.getElementById("tab");
    for (let t = 0; t< database.length; t++) {
        let newTr = document.createElement("tr")
        let newtd1 = document.createElement("td")
        if (database[t][2] == null){
            database[t][2] = "N/A";
            database[t][3] = "";
            database[t][4] = "";
        }
        database[t][5] = (database[t][5] == null) ? 0 : database[t][5];
        database[t][6] = (database[t][6] == null) ? 0 : database[t][6];

        newtd1.appendChild(document.createTextNode(database[t][0]))
        newTr.appendChild(newtd1)
        element.appendChild(newTr)

        newtd1 = document.createElement("td")
        newtd1.appendChild(document.createTextNode(database[t][1]))
        newTr.appendChild(newtd1)
        element.appendChild(newTr)

        newtd1 = document.createElement("td")
        newtd1.appendChild(document.createTextNode(database[t][2]+ " " + database[t][3]+" "+ database[t][4]))
        newTr.appendChild(newtd1)
        element.appendChild(newTr)


        newtd1 = document.createElement("td")
        newtd1.appendChild(document.createTextNode(database[t][5]))
        newTr.appendChild(newtd1)
        element.appendChild(newTr)

        newtd1 = document.createElement("td")
        newtd1.appendChild(document.createTextNode(database[t][6]))
        newTr.appendChild(newtd1)
        element.appendChild(newTr)
    }
}
async function loadTable(endpoint) {
    const table = await fetch(endpoint);
    database = await table.json();
    loadMOverview();
}

loadTable(url);
