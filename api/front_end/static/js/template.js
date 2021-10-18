$(document).ready(function() {
  $(document).on("click", "#deleteScan a", function(event) {
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
      data: form.serializeArray(),
      dataType: "json",
      success: function () {
        location.href = window.location.href;;
      },
    });
  });
});