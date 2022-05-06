// Add data to <table>
function addExclusion() {
  let expression = document.getElementById("regex").value;
  // First check if a <tbody> tag exists, add one if not
  var newId = Number($("#dataTable tbody").length, 10) + Number(1);

  // Append data to the table
  $("#dataTable tbody").append(
    "<tr class='border-t' id='" +
      newId +
      "'>" +
      "<td class='flex justify-between items-center px-4 py-1'>" +
      "<span>" + expression + "</span>" +
      "<input type='hidden' name='exclude' value='"+expression+"'>" +
      "<button class='text-sm uppercase text-red-500 px-2 py-1 rounded hover:bg-red-100' onclick='deleteRow(this)'>x</button>" +
      "</td></tr>"
  );
}

function deleteRow(button) {
  var $row = $(button).closest("tr");
  $row.remove();
}

// Convert form data into JSON string
function getFormData($form){
  var unindexed_array = $form.serializeArray();
  var indexed_array = {};

  $.map(unindexed_array, function(n, i){
      console.log(n['name']);
      if(Array.isArray(indexed_array[n['name']])){
        indexed_array[n['name']].push(n['value']);
      }else{
        if (indexed_array[n['name']]){
          save_value = indexed_array[n['name']];
          indexed_array[n['name']] = new Array();
          indexed_array[n['name']].push(save_value);
          indexed_array[n['name']].push(n['value']);
        }else{
          indexed_array[n['name']] = n['value'];
        }
      }
      
  });

  return JSON.stringify(indexed_array);
}

$(document).ready(function () {
  let data = $('#javascript_data').data();
  new TomSelect('#select-scans', {
    maxItems: 1,
    items: data.selected_scans.split(","),
    plugins: {
      remove_button:{
        title:'Remove scan',
      }
    },
  });
  $("form").submit(function (event) {
    event.preventDefault();
    event.stopPropagation();
    var form = $(document.templateScan);

    $.ajax({
      url: form.attr("action"),
      type: form.attr("method"),
      data: getFormData(form),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function () {
        var url = window.location.href;
        parent_url = url.substring(0, url.lastIndexOf("/"));
        location.href = parent_url;
      },
    });
  });
});
