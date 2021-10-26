$(document).ready(function() {
  $(document).on("click", "#confirmBeforeAction", function(event) {
    event.preventDefault();
    event.stopPropagation();   

    let requestType = "DELETE";

    if ($(this).data("method")){
      requestType = $(this).data("method");
    }

    if (confirm($(this).data("confirm"))) {
      $.ajax({
        url:this.href,
        type:requestType,
        success: function(){
          location.href = window.location.href;
        }
      })
    }
  });

  $("#newTemplateForm").on("submit", function(event) {
    event.preventDefault();
    event.stopPropagation();   
    let form = $("#newTemplateForm")
    $.ajax({
      url: form.attr("action"),
      type: form.attr("method"),
      data: JSON.stringify({"name": form.serializeArray()[0]["value"]}),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function () {
        location.href = window.location.href;;
      },
    });
  });

  function getFormData($form){
    var unindexed_array = $form.serializeArray();
    var indexed_array = {};

    $.map(unindexed_array, function(n, i){
        indexed_array[n['name']] = n['value'];
    });

    return indexed_array;
  }
  
  $("#jsonForm").on("submit", function(event) {
    console.log('cheese');
    event.preventDefault();
    event.stopPropagation();   
    const form = $("#jsonForm")

    $.ajax({
      url: form.attr("action"),
      type: form.attr("method"),
      data: JSON.stringify(getFormData(form)),
      contentType: "application/json; charset=utf-8",
      dataType: "json",
      success: function () {
        location.href = window.location.href;
      },
    });
  });
});