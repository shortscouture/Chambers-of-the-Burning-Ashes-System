/* 

Vanilla Template

https://templatemo.com/tm-526-vanilla

*/

jQuery(document).ready(function($) {

	'use strict';

    var top_header = $('.parallax-content');
    top_header.css({'background-position':'center center'}); // better use CSS

    $(window).scroll(function () {
    var st = $(this).scrollTop();
    top_header.css({'background-position':'center calc(50% + '+(st*.5)+'px)'});
    });


    $('body').scrollspy({ 
        target: '.fixed-side-navbar',
        offset: 200
    });
      
      // smoothscroll on sidenav click

    var owl = $("#owl-testimonials");

      owl.owlCarousel({
        
        pagination : true,
        paginationNumbers: false,
        autoPlay: 6000, //Set AutoPlay to 3 seconds
        items : 3, //10 items above 1000px browser width
        itemsDesktop : [1000,3], //5 items between 1000px and 901px
        itemsDesktopSmall : [900,2], // betweem 900px and 601px
        itemsTablet: [600,1], //2 items between 600 and 0
        itemsMobile : false // itemsMobile disabled - inherit from itemsTablet option
        
    });




});

function showInfoBox(event) {
  event.stopPropagation();
  document.getElementById('infobox').style.display = 'block';
  document.addEventListener('click', hideInfoBox);
}

function hideInfoBox(event) {
  const infobox = document.getElementById('infobox');
  if (!infobox.contains(event.target)) {
    infobox.style.display = 'none';
    document.removeEventListener('click', hideInfoBox);
  }
}

function toggleChat() {
  let chatContainer = document.getElementById("chatContainer");
  chatContainer.style.display = (chatContainer.style.display === "none" || chatContainer.style.display === "") ? "flex" : "none";
}

function sendMessage() {
  const inputField = document.getElementById("userInput");
  const message = inputField.value.trim();
  const chatbox = document.getElementById("chatbox");

  if (message === "") return;

  // Create user message element
  const userMessage = document.createElement("div");
  userMessage.className = "message user-message";
  userMessage.textContent = message;

  // Adjust width based on message length
  let messageLength = message.length;
  if (messageLength < 10) {
      userMessage.style.width = "20%";  // Small width for short messages
  } else if (messageLength < 30) {
      userMessage.style.width = "40%";  // Medium width for medium messages
  } else {
      userMessage.style.width = "60%";  // Large width for long messages
  }

  chatbox.appendChild(userMessage);
  inputField.value = "";

  // Send message to API
  axios.post("/api/chatbot/", { message: message })
      .then(response => {
          const botMessage = document.createElement("div");
          botMessage.className = "message bot-message";
          botMessage.textContent = response.data.response || "No response from bot.";
          chatbox.appendChild(botMessage);
          chatbox.scrollTop = chatbox.scrollHeight;
      })
      .catch(error => {
          console.error("Error:", error);
      });
}

document.getElementById("contact").addEventListener("submit", function(event) {
  event.preventDefault();  // Stop the page from reloading

  let formData = new FormData(this);

  fetch("{% url 'contact' %}", {
      method: "POST",
      body: formData,
      headers: {
          "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
      }
  })
  .then(response => response.json())
  .then(data => {
      if (data.success) {
          alert("Your message has been sent successfully!");
          document.getElementById("contact").reset();
      } else {
          alert("There was an error sending your message.");
      }
  })
  .catch(error => console.error("Error:", error));
});
