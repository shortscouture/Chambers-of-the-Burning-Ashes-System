// Get the modal
var modal = document.getElementById("logoutPrompt");

// Get the button that opens the modal
var btn = document.getElementById("logoutBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

// Get the confirm and cancel buttons
var confirmBtn = document.getElementById("confirmLogout");
var cancelBtn = document.getElementById("cancelLogout");

// When the user clicks the button, open the modal 
btn.onclick = function() {
    modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks on confirm, log out
confirmBtn.onclick = function() {
    alert("Logged out!");
    modal.style.display = "none";
    // Add your logout logic here
}

// When the user clicks on cancel, close the modal
cancelBtn.onclick = function() {
    modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}
