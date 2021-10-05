
function toggleAPIKey() {
  var toggleButton = document.getElementById("show");
  toggleButton.remove();
  var token = document.getElementById("token");
  token.style.visibility = "visible";
}