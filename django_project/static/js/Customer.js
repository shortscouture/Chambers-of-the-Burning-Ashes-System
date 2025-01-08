        // Open the modal
        function openModal() {
            document.getElementById('modal').style.display = 'flex';
        }

        // Close the modal if clicked outside of it
        window.onclick = function(event) {
            const modal = document.getElementById('modal');
            if (event.target === modal) {
                modal.style.display = 'none';
            }
        }
        function openPopup(title, content) {
            const popup = document.getElementById("popup");
            document.getElementById("popup-title").innerText = title;
            document.getElementById("popup-content").innerText = content;
            popup.classList.add("active");
        }
        
        function closePopup() {
            const popup = document.getElementById("popup");
            popup.classList.remove("active");
        }
        