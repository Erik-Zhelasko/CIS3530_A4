
let page = 0;
let max_per_page = 10.0;
let total_pages;
let database;
let inAddMode = false;
let rowsize
const headers = [
  "First Name",
  "Middle Initial",
  "Last Name",
  "SSN",
  "Address",
  "Sex",
  "Salary",
  "Supervisor SSN",
  "Department Number",
  "Date of Birth",
  "Employment Date"
];


loadTable("/API/employee")
function tableScript() {

  total_pages = Math.ceil(database.length / max_per_page)

  const element = document.getElementById("tab");
  for (let t = page * max_per_page; t < Math.min(max_per_page * (page + 1),database.length); t++) {
    const newTr = document.createElement("tr")
    const editButton = document.createElement("button");
    const deleteButton = document.createElement("button");
    for (let i = 0; i < database[t].length; i++) {
      const newtd1 = document.createElement("td")
      newtd1.appendChild(document.createTextNode(database[t][i]))
      newTr.appendChild(newtd1)
      element.appendChild(newTr)
    }
    rowsize = database[0].length
    const newtd1 = document.createElement("td")
    editButton.setAttribute("id","eButton")
    editButton.setAttribute("onclick","editEntry("+ t + ")")

    deleteButton.setAttribute("id","dButton")
    deleteButton.setAttribute("onclick","deleteEntry("+ t + ")")

    newtd1.appendChild(editButton)
    newtd1.appendChild(deleteButton)
    newTr.appendChild(newtd1)
    element.appendChild(newTr)
  }
  generateInputRow(element)
  generateTableButtons(element)


}

function createEmployee() {
  inAddMode = true
  reloadTable()
}

function saveNewEmployee() {
  fetchPOST().then(closeAddMode)
}

function closeAddMode() {
  inAddMode = false
  reloadTable()
}

function generateTableButtons(element) {
  if (inAddMode){
    const tr = document.createElement("tr");
    const saveButton = document.createElement("button");
    const cancelButton = document.createElement("button");
    saveButton.setAttribute("id","sButton");
    saveButton.setAttribute("onclick","saveNewEmployee();")
    saveButton.textContent = "Save";

    cancelButton.setAttribute("id","cButton");
    cancelButton.setAttribute("onclick","closeAddMode();")
    cancelButton.textContent = "Cancel";
    const td = document.createElement("td");
    td.appendChild(cancelButton);
    td.appendChild(saveButton);
    tr.appendChild(td);
    element.appendChild(tr);


  }
  else {
    const tr = document.createElement("tr");
    const nextButton = document.createElement("button");
    const prevButton = document.createElement("button");
    const addButton = document.createElement("button");
    
    addButton.setAttribute("id","aButton");
    addButton.setAttribute("onclick","createEmployee();");
    addButton.textContent = "Add Employee";

    nextButton.setAttribute("id","eButton");
    nextButton.setAttribute("onclick","nextPage()");
    nextButton.textContent = "Next";

    prevButton.setAttribute("id","dButton");
    prevButton.setAttribute("onclick","prevPage()");
    prevButton.textContent = "Previous";

    const td = document.createElement("td");
    td.appendChild(addButton);
    td.appendChild(document.createTextNode("Page " + (page + 1) + " of " + total_pages));
    td.appendChild(nextButton);
    td.appendChild(prevButton);
    tr.appendChild(td);
    element.appendChild(tr);

  }
}
function generateInputRow(element){
  const numonly = ["ssn","salary","supervisor ssn","department number"];
  if (!inAddMode) {
    return;
  }
  const tr = document.createElement("tr");
  for (let i = 0; i < rowsize; i++) {
    const td = document.createElement("td");
    const input = document.createElement("input");
    console.log(headers[i].toLowerCase())
    console.log(numonly.includes(headers[i].toLowerCase()))
    if (headers[i].toLowerCase().includes("date")) {
      input.setAttribute("Type","date")
    }
    else if (numonly.includes(headers[i].toLowerCase())) {
      input.setAttribute("Type","number");
      input.setAttribute("placeholder",headers[i])
    }
    else {
      input.setAttribute("placeholder",headers[i])

    }
    input.setAttribute("id","addField"+i)
    td.appendChild(input)
    tr.appendChild(td)
  }
  element.appendChild(tr)
}


function showModal(id,type) {
  console.log(type)
  const dialog = document.getElementById(type)
  setEditorDefaults(id)
  dialog.showModal();
}
function hideModal(type) {
  const dialog = document.getElementById(type)
  dialog.close();
}

function setEditorDefaults(id){
    const SSNheader = document.getElementById("ssnHeader")
    const addressField = document.getElementById("addressField")
    const salaryField = document.getElementById("salaryField")
    const departmentField = document.getElementById("departmentField")
    SSNheader.textContent = (database[id][3])
    addressField.value = database[id][4];
    salaryField.value = database[id][6];
    departmentField.value = database[id][8];

}

async function loadTable(endpoint) {
    const table = await fetch(endpoint);
    database = await table.json();
    tableScript();
}
function editEntry (t) {
  // alert("Mattress Can Catch Fire if they don't meet federal standards! ID: " + t) 
  showModal(t,"ePopup") 
}
function deleteEntry(t) {
  showModal(t,"dPopup")

}
function nextPage() {
  if (page + 1 != total_pages) {
    page++;
    reloadTable();
  }
}
function prevPage() {
  if (page > 0) {
    page--;
    reloadTable();
    
  }

}
function reloadTable() {
  clearTable()
  loadTable("/API/employee")
  // tableScript()
}

function clearTable() {
  const element = document.getElementById("tab");
  while (element.children.length > 1) {
    element.removeChild(element.lastChild);
  }
}

async function fetchPatch() {
    const SSNheader = document.getElementById("ssnHeader").textContent
    const addressField = document.getElementById("addressField").value
    const salaryField = document.getElementById("salaryField").value
    const departmentField = document.getElementById("departmentField").value
    await fetch("/API/employee", {
      method:'PATCH',
      headers: {
      'Content-Type': 'application/json'
      },
      body: JSON.stringify({ssn: SSNheader, address: addressField, salary: salaryField, dno: departmentField })
    }).then(async response => {
      console.log(response.status)
      alert(await response.text())
    })
}
// INSERT
async function fetchPOST() {
  const data = {};
    for (i = 0; i < rowsize; i++) {
      data[headers[i]] = document.getElementById("addField"+i).value;
    }
  console.log(data)
  await fetch("/API/employee", {
    method:'POST',
    headers: {
    'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
}).then(async response => {
      console.log(response.status)
      alert(await response.text())
    })
}


async function fetchDelete() {
    const SSNheader = document.getElementById("ssnHeader").textContent
    await fetch("/API/employee", {
      method:'DELETE',
      headers: {
      'Content-Type': 'application/json'
      },
      body: JSON.stringify({ssn: SSNheader})
}).then(async response => {
      
      if (await response.text() == "RestrictViolation") {
        alert("Cannot delete employee: They are still assigned to projects, have dependents listed, or are a manager/supervisor.")
      }
      else{
        alert(await response.text())
      }
    })
}