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

  if ($("#container div").length == 0) {
    $("#container").append("<div id='child'></div>");

  // Currently only allowing one scan type per template
    var container = document.getElementById("child");

    var selectedOption = document.getElementById("scanType");
    var input = document.createElement("input");
    input.className = "bg-gray-200 appearance-none border-2 border-gray-200 rounded w-full py-2 px-4 text-gray-700 leading-tight focus:outline-none focus:bg-white focus:border-purple-500";
    var unique_id = "scanType-" + selectedOption.options[selectedOption.selectedIndex].value;

    var elementExists = document.getElementById(unique_id);

    if (typeof (elementExists) === 'undefined' || elementExists === null) {
      input.readonly = true;
      input.type = "text";
      input.id = unique_id
      input.name = "scanType"
      input.value = selectedOption.options[selectedOption.selectedIndex].id;
      
      var span = document.createElement('span');
      span.innerHTML = '<button class="bg-red-500 hover:bg-red-700 text-white font-bold  px-2 rounded" type="button" id="addScanButton" class="btn btn-primary" onclick="scanClear();">Clear</button>';
      
      var header_span = document.createElement('span');
      header_span.innerHTML = '<strong>Selected scan type</strong></br>'
      
      container.appendChild(header_span);
      container.appendChild(input);
      container.appendChild(span);
      container.appendChild(document.createElement("br"));
      
    }
  }
}

function scanClear() {
  var container = document.getElementById("container");
  container.innerHTML = '';
}

$(document).ready(function () {
  $("form").submit(function (event) {
    event.preventDefault();
    event.stopPropagation();
    var form = $(document.templateScan);
    var dat = JSON.stringify(form.serializeArray());

    output = {}
    var arr = $('tr[data-id]:not([data-id=""])').map(function() {
      key = $(this).find("input")[0].value;
      result = {}
      result[key] = $(this).find("input")[1].value;
      return result;
    }).get();

    output['data'] = arr;
    

    var scans = $("input[id^='scanType-']").map(function() {
      return {
        'scanType': this.value
      };
    }).get();

    output['scan_types'] = scans;

    $.ajax({
      url:form.attr("action"),
      type:"POST",
      data:JSON.stringify(output),
      contentType:"application/json; charset=utf-8",
      dataType:"json",
      success: function(){
        var url = window.location.href;
        parent_url = url.substring(0, url.lastIndexOf('\/'));
        location.href = parent_url;
      }
    })

  });
});
