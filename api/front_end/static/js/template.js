$(document).ready(function() {
  $("#deleteScan a").click(function(event) {
    event.preventDefault();
    event.stopPropagation();
      // Jinja2 location not accessible, so translations moved here
      var text = "Are you sure you want to delete this scan ?"

      if (window.location.href.indexOf("/fr/") > -1) {
        text = "Etes-vous sûr de vouloir supprimer ce scan ?"
      }

      if (confirm(text)) {
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