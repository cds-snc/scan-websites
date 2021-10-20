$(document).ready(function() {
  $(document).on("click", "#deleteConfirm", function(event) {
    event.preventDefault();
    event.stopPropagation();   
      if (confirm($(this).data("confirm"))) {
        $.ajax({
          url:this.href,
          type:"DELETE",
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
});