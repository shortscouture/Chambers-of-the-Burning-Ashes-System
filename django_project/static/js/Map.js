const loadingTexts = [
    "Fetching vault statuses...",
    "Checking availability...",
    "Updating crypt colors...",
    "Please wait a moment...",
    "If bored please recite ama namin",
    "Pray for faster loading",
    "Ensuring data is accurate...",
    "Almost done...",
];

function changeLoadingText() {
    const loadingTextElement = document.getElementById("loading-text");
    if (!loadingTextElement) return;

    // Pick a random text
    const randomText = loadingTexts[Math.floor(Math.random() * loadingTexts.length)];
    loadingTextElement.textContent = randomText;
   
} 
async function updateCryptColor(section) {
    try {
        let response = await fetch(`/get_crypt_status/${section}/`);
        let data = await response.json();
        const cryptElement = document.getElementById(section);
        if (cryptElement) {
            cryptElement.setAttribute("fill", data.color);
        }
    } catch (error) {
        console.error(`Error updating ${section}:`, error);
    }
}

async function updateAllCrypts() {
    const loadingScreen = document.getElementById("loading-screen");
    loadingScreen.style.display = "flex"; // Show loading screen

    // Change loading text every 2 seconds
    const textInterval = setInterval(changeLoadingText, 30000);
    const cryptSections = [
"E-1", "E-2", "E-3", "E-4", "E-4A", "E-5", "E-6", "E-7", "E-8", "E-9", "E-10", "E-11", "E-12", "E-13", "E-14", "E-15", "E-16", "E-17", "E-18", "E-19", "E-20", "E-21", "E-22", "E-23", "E-24", "E-25", "E-26", "E-27", "E-28", "E-29", "E-30", "E-31", "E-32", "E-33", "E-34", "E-35", "E-36", "E-37", "E-38", "E-39", "E-41", "E-42", "E-43", "E-44", "E-45", "E-46", "E-47", "E-48", "E-49", "E-50", "E-51", "E-52", "E-53", "E-54", "E-55", "E-56", "E-57", "E-58", "E-60", "E-61", "E-62", "E-63", "E-64", "E-65", "E-66", "E-67", "E-68", "E-69", "E-70", "E-71", "E-72", "E-73", "E-74", "E-75", "E-76", "E-77", "E-78", "E-79", "E-80", "E-81", "E-82", "E-83", "E-84", "E-85", "E-86", "E-87", "E-88", "E-89", "E-90", "E-91", "E-92", "E-93", "E-94", "E-95", "E-96", "E-97", "E-97A", "E-98", "E-98A", "E-99", "E-99A", "E-100", "E-101", "E-102", "E-103", "E-104", "E-105", "E-106", "E-107", "E-108", "E-109", "E-110", "E-111", "E-112", "E-113", "E-114", "E-115", "E-116", "E-117", "E-118", "E-119", "E-120", "E-121", "E-122", "E-123", "E-124", "E-125", "E-126", "E-127", "E-128", "E-129", "E-130", "E-131", "E-132", "E-133", "E-134", "E-135", "E-136", "E-137", "E-138", "E-139", "E-140", "E-141", "E-142", "E-143", "E-144", "E-145", "E-146", "E-147", "E-148", "E-149", "E-150", "E-150A", "E-151", "E-152", "E-153", "E-154", "E-155", "E-156", "E-157", "E-158", "E-158A", "E-158B", "E-158C", "E-158D", "E-158E", "E-158F", "E-158G", "E-158H", "E-159", "E-160", "E-161", "E-162", "E-163", "E-164", "E-164A", "E-165", "E-166", "E-167", "E-168", "E-169", "E-170", "E-171", "E-172", "E-173", "E-174", "E-175", "E-176", "E-177", "E-178", "E-179", "E-180", "E-181", "E-182", "E-183", "E-184", "E-185", "E-186", "E-187", "E-188", "E-189", "E-190", "E-191", "E-192", "E-193", "E-194", "E-195", "E-196", "E-197", "E-198", "E-199", "E-200", "E-201", "E-202", "E-203", "E-204",
"N-1", "N-2", "N-3", "N-4", "N-5", "N-6", "N-7", "N-8", "N-9", "N-10", "N-11", "N-12", "N-13", "N-14", "N-15", "N-16", "N-17", "N-18", "N-19", "N-20", "N-21", "N-22", "N-23", "N-24", "N-25", "N-26", "N-27", "N-28", "N-29", "N-30", "N-31", "N-32",
"W-1", "W-2", "W-3", "W-4", "W-4A", "W-5", "W-6", "W-7", "W-8", "W-9", "W-10", "W-11", "W-12", "W-13", "W-14", "W-15", "W-16", "W-17", "W-18", "W-19", "W-20", "W-21", "W-22", "W-23", "W-24", "W-25", "W-26", "W-27", "W-28", "W-29", "W-30", "W-31", "W-32", "W-33", "W-34", "W-35", "W-36", "W-37", "W-38", "W-39", "W-41", "W-42", "W-43", "W-44", "W-45", "W-46", "W-47", "W-48", "W-49", "W-50", "W-51", "W-52", "W-53", "W-54", "W-55", "W-56", "W-57", "W-58", "W-60", "W-61", "W-62", "W-63", "W-64", "W-65", "W-66", "W-67", "W-68", "W-69", "W-70", "W-71", "W-72", "W-73", "W-74", "W-75", "W-76", "W-77", "W-78", "W-79", "W-80", "W-81", "W-82", "W-83", "W-84", "W-85", "W-86", "W-87", "W-88", "W-89", "W-90", "W-91", "W-92", "W-93", "W-94", "W-95", "W-96", "W-97", "W-98", "W-99", "W-99A", "W-100", "W-101", "W-102", "W-103", "W-104", "W-105", "W-106", "W-106A", "W-107", "W-107A", "W-108", "W-109", "W-110", "W-111", "W-112", "W-113", "W-114", "W-115", "W-116", "W-117", "W-118", "W-119", "W-120", "W-121", "W-122", "W-123", "W-124", "W-125", "W-126", "W-127", "W-128", "W-129", "W-130", "W-131", "W-132", "W-133", "W-134", "W-135", "W-136", "W-137", "W-138", "W-139", "W-140", "W-141", "W-142", "W-143", "W-144", "W-145", "W-146", "W-147", "W-148", "W-149", "W-150", "W-151", "W-152", "W-153", "W-154", "W-155", "W-156", "W-156A", "W-156B", "W-156C", "W-156D", "W-157", "W-158", "W-159", "W-160", "W-161", "W-162", "W-163", "W-164", "W-164A", "W-164B", "W-164C", "W-164D", "W-164I", "W-164E", "W-164F", "W-164G", "W-164H", "W-165", "W-166", "W-167", "W-168", "W-169", "W-170", "W-171", "W-172", "W-173", "W-174", "W-175", "W-176", "W-177", "W-178", "W-179", "W-180", "W-181A", "W-181", "W-182", "W-183", "W-184", "W-185", "W-186", "W-187", "W-188", "W-189", "W-190", "W-191", "W-192", "W-193", "W-194A", "W-194", "W-195", "W-196", "W-197", "W-198", "W-199", "W-200", "W-201", "W-202", "W-203", "W-204", "W-205", "W-206", "W-207", "W-208", "W-209", "W-210", "W-211", "W-212"
    ];

    // Wait for all crypt updates to finish
    await Promise.all(cryptSections.map(updateCryptColor));

    // Stop changing text and hide loading screen
    clearInterval(textInterval);
    loadingScreen.style.display = "none";
}

updateAllCrypts();
setInterval(updateAllCrypts, 10 * 60 * 1000);


  const svg = document.getElementById("zoomable-svg");
  let viewBox = { x: 0, y: 0, width: 1000, height: 1000 }; // Set initial viewBox
  let isPanning = false;
  let startX, startY;
  let zoomFactor = 1.5; // 🔹 Increased zoom effect
  
  // Mouse Wheel Zoom (INVERTED)
  svg.addEventListener("wheel", (event) => {
      event.preventDefault();
      
      let scale = event.deltaY > 0 ? zoomFactor : 1 / zoomFactor; // 🔹 Inverted mouse wheel direction
      let newWidth = viewBox.width * scale;
      let newHeight = viewBox.height * scale;
      
      // Prevent excessive zooming
      if (newWidth < 100 || newWidth > 5000) return; // 🔹 Adjusted min/max zoom levels
  
      // Center zoom around mouse
      let mouseX = event.offsetX / svg.clientWidth * viewBox.width + viewBox.x;
      let mouseY = event.offsetY / svg.clientHeight * viewBox.height + viewBox.y;
      
      viewBox.x = mouseX - (mouseX - viewBox.x) * scale;
      viewBox.y = mouseY - (mouseY - viewBox.y) * scale;
      viewBox.width = newWidth;
      viewBox.height = newHeight;
  
      updateViewBox();
  });
  
  // Drag Navigation
  svg.addEventListener("mousedown", (event) => {
      isPanning = true;
      startX = event.clientX;
      startY = event.clientY;
  });
  
  svg.addEventListener("mousemove", (event) => {
      if (!isPanning) return;
      let dx = (startX - event.clientX) * (viewBox.width / svg.clientWidth);
      let dy = (startY - event.clientY) * (viewBox.height / svg.clientHeight);
      viewBox.x += dx;
      viewBox.y += dy;
      startX = event.clientX;
      startY = event.clientY;
      updateViewBox();
  });
  
  svg.addEventListener("mouseup", () => { isPanning = false; });
  svg.addEventListener("mouseleave", () => { isPanning = false; });
  
  // Update the SVG ViewBox
  function updateViewBox() {
      svg.setAttribute("viewBox", `${viewBox.x} ${viewBox.y} ${viewBox.width} ${viewBox.height}`);
  }
  
  function openPopup(sectionId) {
    fetch(`/get_vault_data/${sectionId}/`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert("No records found for this section.");
                return;
            }

            // Update the displayed section name
            document.getElementById('selected-section').textContent = `Section: ${sectionId}`;
            
            // Store section ID in hidden input
            document.getElementById('section-input').value = sectionId;

            // Update SVG colors dynamically
            ['A', 'B', 'C', 'D', 'E'].forEach(level => {
                let levelElement = document.getElementById(`level-${level}`);
                if (levelElement) {
                    if (data.levels[level] === undefined) {
                        levelElement.style.display = 'none'; // Hide non-existent levels
                    } else {
                        levelElement.style.display = 'block';
                        levelElement.setAttribute('fill', data.levels[level] ? 'red' : 'green');
                    }
                }
            });

            // Populate dropdown with available levels
            let dropdown = document.getElementById('level-select');
            dropdown.innerHTML = ''; // Clear previous options
            let foundVacant = false; // Track if there's at least one vacant level

            Object.keys(data.levels).forEach(level => {
                if (!data.levels[level]) {  // If level is vacant
                    let option = document.createElement('option');
                    option.value = level;
                    option.textContent = level;
                    dropdown.appendChild(option);
                    
                    if (!foundVacant) {
                        document.getElementById('level-input').value = level; // Set the first vacant level
                        foundVacant = true;
                    }
                }
            });

            // Show the popup
            document.getElementById('popup').style.display = 'block';
        })
        .catch(error => console.error("Error fetching data:", error));
}

// Ensure level selection updates the hidden input field
document.getElementById("level-select").addEventListener("change", function () {
    document.getElementById("level-input").value = this.value;
});
