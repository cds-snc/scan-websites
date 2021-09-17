// Add data to <table>
function dataAdd() {
  // First check if a <tbody> tag exists, add one if not
  if ($("#dataTable tbody").length == 0) {
    $("#dataTable").append("<tbody></tbody>");
  }

  var newId = Number($("#dataTable tbody").length, 10) + Number(1);

  // Append data to the table
  $("#dataTable tbody").append("<tr data-id='" + newId + "'>" +
    "<td class='border px-4 py-2'><input type='text' name='key'/></td>" +
    "<td class='border px-4 py-2'><input type='text' name='value'/></td>" +
    "</tr>");
}

function scanAdd() {
  var container = document.getElementById("container");
  var selectedOption = document.getElementById("scanType");
  var input = document.createElement("input");
  input.className = "bg-gray-200 appearance-none border-2 border-gray-200 rounded w-full py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white focus:border-purple-500";
  var unique_id = "scanType-" + selectedOption.options[selectedOption.selectedIndex].value;

  var elementExists = document.getElementById(unique_id);

  if (typeof (elementExists) == 'undefined' || elementExists == null) {
    input.type = "text";
    input.id = unique_id
    input.name = "scanType"
    input.value = selectedOption.options[selectedOption.selectedIndex].id;
    container.appendChild(input);
    container.appendChild(document.createElement("br"));
  }
}

$(document).ready(function () {
  $("form").submit(function (event) {
    event.preventDefault();
    var form = $(document.templateScan);
    var dat = JSON.stringify(form.serializeArray());

    $.post(
      form.attr("action"),
      dat,
      function (res) {
        window.location = res.redirect;
        location.reload();  
      }
    );

  });
});
