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
      "<button class='text-sm uppercase text-red-500 px-2 py-1 rounded hover:bg-red-100' onclick='deleteRow(this)'>x</button>" +
      "</tr>"
  );
}

function deleteRow(button) {
  var $row = $(button).closest("tr");
  $row.remove();
}

$(document).ready(function () {
  let data = $('#javascript_data').data();
  new TomSelect('#select-scans', {
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
    var dat = JSON.stringify(form.serializeArray());

    output = {};
    data = {};
    $('tr[data-id]:not([data-id=""])')
      .each(function () {
        key = $(this).find("input")[0].value;
        data[key] = $(this).find("input")[1].value;
      })
      .get();

    output["data"] = data;

    var scans = $("input[id^='scanType-']")
      .map(function () {
        return {
          scanType: this.value,
        };
      })
      .get();

    output["scan_types"] = scans;

    $.ajax({
      url: form.attr("action"),
      type: form.attr("method"),
      data: JSON.stringify(output),
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
