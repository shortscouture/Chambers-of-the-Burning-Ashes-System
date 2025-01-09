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
        function showPopup(title, description, imageUrl, displayStyle = 'block') {
            let overlay = document.querySelector('.overlay');
            let popup = document.querySelector('.popup');
        
            // If popup and overlay exist, update their content and show them
            if (popup && overlay) {
                popup.querySelector('h2').textContent = title;
                popup.querySelector('img').src = imageUrl;
                popup.querySelector('img').alt = title;
                popup.querySelector('p').textContent = description;
        
                overlay.style.display = 'block';
                popup.style.display = displayStyle;
                return;
            }
        
            // Otherwise, create a new popup and overlay
            overlay = document.createElement('div');
            overlay.onclick = closePopup; // Attach close event to overlay
        
            popup = document.createElement('div');
            popup.className = 'popup';
            popup.style.display = displayStyle;
            popup.innerHTML = `
                <h2>${title}</h2>
                <img src="${imageUrl}" alt="${title}">
                <p>${description}</p>
            `;
        
            const closeButton = document.createElement('button');
            closeButton.textContent = 'Close';
            closeButton.addEventListener('click', closePopup); // Attach close event to button
            popup.appendChild(closeButton);
        
            document.body.appendChild(overlay);
            document.body.appendChild(popup);
        }
        
        function closePopup() {
            const popup = document.querySelector('.popup');
            const overlay = document.querySelector('.overlay');
            if (popup) popup.remove(); // Remove popup from DOM
            if (overlay) overlay.remove(); // Remove overlay from DOM
        }
        