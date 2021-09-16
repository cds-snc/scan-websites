    // Add data to <table>
function dataAdd() {
    // First check if a <tbody> tag exists, add one if not
    if ($("#dataTable tbody").length == 0) {
        $("#dataTable").append("<tbody></tbody>");
    }

    var newId = Number($("#dataTable tbody").length,10) + Number(1);
    
    // Append data to the table
    $("#dataTable tbody").append("<tr data-id='" + newId + "'>" +
        "<td class='border px-4 py-2' contenteditable='true' data-field='key'></td>" +
        "<td class='border px-4 py-2' contenteditable='true' data-field='value'></td>" +
        "</tr>");
}
