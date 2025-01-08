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