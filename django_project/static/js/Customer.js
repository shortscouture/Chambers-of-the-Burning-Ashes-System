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

        document.getElementById('customerForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Reset errors
            document.querySelectorAll('.error').forEach(error => error.style.display = 'none');
            
            // Validate form
            let isValid = true;
            const full_name = document.getElementById('full_name').value.trim();
            const address = document.getElementById('permanent_address').value.trim();
            
            if (!full_name) {
                document.getElementById('full_name_error').style.display = 'block';
                isValid = false;
            }
            
            if (!address) {
                document.getElementById('address_error').style.display = 'block';
                isValid = false;
            }
            
            const email = document.getElementById('email_addrress').value.trim();
            if (email && !email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
                document.getElementById('email_error').style.display = 'block';
                isValid = false;
            }
            
            if (isValid) {
                const formData = {
                    full_name: full_name,
                    address: address,
                    landline: document.getElementById('landline_number').value.trim(),
                    mobile: document.getElementById('mobile_number').value.trim(),
                    email: email
                };
                
                fetch('/register/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(formData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert('Customer registered successfully!');
                        document.getElementById('customerForm').reset();
                    } else {
                        alert('Error: ' + data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while submitting the form');
                });
            }
        });