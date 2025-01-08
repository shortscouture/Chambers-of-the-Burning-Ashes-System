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
        function showPopup(title, description) {
            // Get the popup elements
            const popup = document.getElementById('popup');
            const popupTitle = document.getElementById('popup-title');
            const popupDescription = document.getElementById('popup-description');
        
            // Set the content
            popupTitle.textContent = title;
            popupDescription.textContent = description;
        
            // Show the popup
            popup.classList.remove('hidden');
        }
        
        function closePopup() {
            // Hide the popup
            const popup = document.getElementById('popup');
            popup.classList.add('hidden');
        }
        