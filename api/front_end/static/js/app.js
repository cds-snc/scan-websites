function getFormData($form){
  var unindexed_array = $form.serializeArray();
  var indexed_array = {};

  $.map(unindexed_array, function(n, i){
      indexed_array[n['name']] = n['value'];
  });

  return indexed_array;
} 

function submitJSON(event){

  event.preventDefault();
  form = $(this);

  if (confirm(form.data("confirm"))) {
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
  }
  return false;
}

$(document).ready(function() {
  $(document).on("click", "#confirmBeforeAction", function(event) {
    event.preventDefault();
    event.stopPropagation();   

    let requestType = "DELETE";
    const link = $(this);

    if (link.data("method")){
      requestType = link.data("method");
    }

    if (confirm(link.data("confirm"))) {
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

  $(".submitFormAsJSON").on("submit", submitJSON)
});


