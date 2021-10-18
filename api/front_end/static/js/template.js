$(document).ready(function() {
  $(document).on("click", "#deleteConfirm a", function(event) {
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
});