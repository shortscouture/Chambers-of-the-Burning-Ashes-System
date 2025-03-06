jQuery(document).ready(function($) {

	'use strict';


        $('.counter').each(function() {
          var $this = $(this),
              countTo = $this.attr('data-count');
          
          $({ countNum: $this.text()}).animate({
            countNum: countTo
          },

          {

            duration: 8000,
            easing:'linear',
            step: function() {
              $this.text(Math.floor(this.countNum));
            },
            complete: function() {
              $this.text(this.countNum);
              //alert('finished');
            }

          });  
          
        });



        $(".b1").click(function () {
            $(".pop").fadeIn(300);
            
        });
		
		$(".b2").click(function () {
            $(".pop2").fadeIn(300);
            
        });
		
		$(".b3").click(function () {
            $(".pop3").fadeIn(300);
            
        });

        $(".pop > span, .pop").click(function () {
            $(".pop").fadeOut(300);
        });
		
		$(".pop2 > span, .pop2").click(function () {
            $(".pop2").fadeOut(300);
        });
		
		$(".pop3 > span, .pop3").click(function () {
            $(".pop3").fadeOut(300);
        });


        $(window).on("scroll", function() {
            if($(window).scrollTop() > 100) {
                $(".header").addClass("active");
            } else {
                //remove the background property so it comes transparent again (defined in your css)
               $(".header").removeClass("active");
            }
        });


	/************** Mixitup (Filter Projects) *********************/
    	$('.projects-holder').mixitup({
            effects: ['fade','grayscale'],
            easing: 'snap',
            transitionSpeed: 400
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
