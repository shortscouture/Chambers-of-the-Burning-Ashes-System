const csrfToken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
function toggleChat() {
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.style.display = (chatContainer.style.display === 'none') ? 'block' : 'none';
}
function sendMessage() {
    const userInput = document.getElementById('userInput').value;
    const chatbox = document.getElementById('chatbox');
    
    setTimeout(() => { // Small delay to ensure the element is rendered
        chatbox.scrollTop = chatbox.scrollHeight;
    }, 0); 

    // Check if there's input and display user's message
    if (userInput.trim() !== '') {
        chatbox.innerHTML += `<div class="user-message">${userInput}</div>`;

        // Clear the input field
        document.getElementById('userInput').value = '';

        // Make a POST request to the chatbot API
        fetch('/api/chatbot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            body: JSON.stringify({ message: userInput })
        })
        .then(response => {
            console.log("Response Status:", response.status);
            return response.json();
        })
        .then(data => {
            console.log("Chatbot Response:", data);
        })
        .catch(error => {
            console.error('Fetch Error:', error);
        });
    
    }
}
document.addEventListener('DOMContentLoaded', function() {
    const closeButton = document.querySelector('.close-btn');
    if (closeButton) {
        closeButton.addEventListener('click', () => {
            document.getElementById('chatContainer').style.display = 'none';
        });
    }
});
const chatTitle = document.querySelector('.chat-title'); // Or the element you are using for the title