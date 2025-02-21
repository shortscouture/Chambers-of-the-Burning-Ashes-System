function updateCryptColor(section) {
    fetch(`/get_crypt_status/${section}/`)
        .then(response => response.json())
        .then(data => {
            const cryptElement = document.getElementById(section);
            if (cryptElement) {
                cryptElement.setAttribute("fill", data.color);
            }
        })
        .catch(error => console.error("Error:", error));
  }
  updateAllCrypts();
  setInterval(updateAllCrypts, 10 * 60 * 1000);

  function updateAllCrypts() {
    updateCryptColor("E-1"); updateCryptColor("E-2"); updateCryptColor("E-3"); updateCryptColor("E-4"); updateCryptColor("E-4A"); updateCryptColor("E-5"); updateCryptColor("E-6"); updateCryptColor("E-7"); updateCryptColor("E-8"); updateCryptColor("E-9"); updateCryptColor("E-10"); updateCryptColor("E-11"); updateCryptColor("E-12"); updateCryptColor("E-13"); updateCryptColor("E-14"); updateCryptColor("E-15"); updateCryptColor("E-16"); updateCryptColor("E-17"); updateCryptColor("E-18"); updateCryptColor("E-19"); updateCryptColor("E-20"); updateCryptColor("E-21"); updateCryptColor("E-22"); updateCryptColor("E-23"); updateCryptColor("E-24"); updateCryptColor("E-25"); updateCryptColor("E-26"); updateCryptColor("E-27"); updateCryptColor("E-28"); updateCryptColor("E-29"); updateCryptColor("E-30"); updateCryptColor("E-31"); updateCryptColor("E-32"); updateCryptColor("E-33"); updateCryptColor("E-34"); updateCryptColor("E-35"); updateCryptColor("E-36"); updateCryptColor("E-37"); updateCryptColor("E-38"); updateCryptColor("E-39"); updateCryptColor("E-41"); updateCryptColor("E-42"); updateCryptColor("E-43"); updateCryptColor("E-44"); updateCryptColor("E-45"); updateCryptColor("E-46"); updateCryptColor("E-47"); updateCryptColor("E-48"); updateCryptColor("E-49"); updateCryptColor("E-50"); updateCryptColor("E-51"); updateCryptColor("E-52"); updateCryptColor("E-53"); updateCryptColor("E-54"); updateCryptColor("E-55"); updateCryptColor("E-56"); updateCryptColor("E-57"); updateCryptColor("E-58"); updateCryptColor("E-60"); updateCryptColor("E-61"); updateCryptColor("E-62"); updateCryptColor("E-63"); updateCryptColor("E-64"); updateCryptColor("E-65"); updateCryptColor("E-66"); updateCryptColor("E-67"); updateCryptColor("E-68"); updateCryptColor("E-69"); updateCryptColor("E-70"); updateCryptColor("E-71"); updateCryptColor("E-72"); updateCryptColor("E-73"); updateCryptColor("E-74"); updateCryptColor("E-75"); updateCryptColor("E-76"); updateCryptColor("E-77"); updateCryptColor("E-78"); updateCryptColor("E-79"); updateCryptColor("E-80"); updateCryptColor("E-81"); updateCryptColor("E-82"); updateCryptColor("E-83"); updateCryptColor("E-84"); updateCryptColor("E-85"); updateCryptColor("E-86"); updateCryptColor("E-87"); updateCryptColor("E-88"); updateCryptColor("E-89"); updateCryptColor("E-90"); updateCryptColor("E-91"); updateCryptColor("E-92"); updateCryptColor("E-93"); updateCryptColor("E-94"); updateCryptColor("E-95"); updateCryptColor("E-96"); updateCryptColor("E-97"); updateCryptColor("E-97A"); updateCryptColor("E-98"); updateCryptColor("E-98A"); updateCryptColor("E-99"); updateCryptColor("E-99A"); updateCryptColor("E-100"); updateCryptColor("E-101"); updateCryptColor("E-102"); updateCryptColor("E-103"); updateCryptColor("E-104"); updateCryptColor("E-105"); updateCryptColor("E-106"); updateCryptColor("E-107"); updateCryptColor("E-108"); updateCryptColor("E-109"); updateCryptColor("E-110"); updateCryptColor("E-111"); updateCryptColor("E-112"); updateCryptColor("E-113"); updateCryptColor("E-114"); updateCryptColor("E-115"); updateCryptColor("E-116"); updateCryptColor("E-117"); updateCryptColor("E-118"); updateCryptColor("E-119"); updateCryptColor("E-120"); updateCryptColor("E-121"); updateCryptColor("E-122"); updateCryptColor("E-123"); updateCryptColor("E-124"); updateCryptColor("E-125"); updateCryptColor("E-126"); updateCryptColor("E-127"); updateCryptColor("E-128"); updateCryptColor("E-129"); updateCryptColor("E-130"); updateCryptColor("E-131"); updateCryptColor("E-132"); updateCryptColor("E-133"); updateCryptColor("E-134"); updateCryptColor("E-135"); updateCryptColor("E-136"); updateCryptColor("E-137"); updateCryptColor("E-138"); updateCryptColor("E-139"); updateCryptColor("E-140"); updateCryptColor("E-141"); updateCryptColor("E-142"); updateCryptColor("E-143"); updateCryptColor("E-144"); updateCryptColor("E-145"); updateCryptColor("E-146"); updateCryptColor("E-147"); updateCryptColor("E-148"); updateCryptColor("E-149"); updateCryptColor("E-150"); updateCryptColor("E-150A"); updateCryptColor("E-151"); updateCryptColor("E-152"); updateCryptColor("E-153"); updateCryptColor("E-154"); updateCryptColor("E-155"); updateCryptColor("E-156"); updateCryptColor("E-157"); updateCryptColor("E-158"); updateCryptColor("E-158A"); updateCryptColor("E-158B"); updateCryptColor("E-158C"); updateCryptColor("E-158D"); updateCryptColor("E-158E"); updateCryptColor("E-158F"); updateCryptColor("E-158G"); updateCryptColor("E-158H"); updateCryptColor("E-159"); updateCryptColor("E-160"); updateCryptColor("E-161"); updateCryptColor("E-162"); updateCryptColor("E-163"); updateCryptColor("E-164"); updateCryptColor("E-164A"); updateCryptColor("E-165"); updateCryptColor("E-166"); updateCryptColor("E-167"); updateCryptColor("E-168"); updateCryptColor("E-169"); updateCryptColor("E-170"); updateCryptColor("E-171"); updateCryptColor("E-172"); updateCryptColor("E-173"); updateCryptColor("E-174"); updateCryptColor("E-175"); updateCryptColor("E-176"); updateCryptColor("E-177");updateCryptColor("E-178"); updateCryptColor("E-179"); updateCryptColor("E-180"); updateCryptColor("E-181"); updateCryptColor("E-182"); updateCryptColor("E-183"); updateCryptColor("E-184"); updateCryptColor("E-185"); updateCryptColor("E-186"); updateCryptColor("E-187"); updateCryptColor("E-188"); updateCryptColor("E-189"); updateCryptColor("E-190"); updateCryptColor("E-191"); updateCryptColor("E-192"); updateCryptColor("E-193"); updateCryptColor("E-194"); updateCryptColor("E-195"); updateCryptColor("E-196"); updateCryptColor("E-197"); updateCryptColor("E-198"); updateCryptColor("E-199"); updateCryptColor("E-200"); updateCryptColor("E-201"); updateCryptColor("E-202"); updateCryptColor("E-203"); updateCryptColor("E-204");
    updateCryptColor("N-1"); updateCryptColor("N-2"); updateCryptColor("N-3"); updateCryptColor("N-4"); updateCryptColor("N-5"); updateCryptColor("N-6"); updateCryptColor("N-7"); updateCryptColor("N-8"); updateCryptColor("N-9"); updateCryptColor("N-10"); updateCryptColor("N-11"); updateCryptColor("N-12"); updateCryptColor("N-13"); updateCryptColor("N-14"); updateCryptColor("N-15"); updateCryptColor("N-16"); updateCryptColor("N-17"); updateCryptColor("N-18"); updateCryptColor("N-19"); updateCryptColor("N-20"); updateCryptColor("N-21"); updateCryptColor("N-22"); updateCryptColor("N-23"); updateCryptColor("N-24"); updateCryptColor("N-25"); updateCryptColor("N-26"); updateCryptColor("N-27"); updateCryptColor("N-28"); updateCryptColor("N-29"); updateCryptColor("N-30"); updateCryptColor("N-31"); updateCryptColor("N-32");
    updateCryptColor("W-1"); updateCryptColor("W-2"); updateCryptColor("W-3"); updateCryptColor("W-4"); updateCryptColor("W-4A"); updateCryptColor("W-5"); updateCryptColor("W-6"); updateCryptColor("W-7"); updateCryptColor("W-8"); updateCryptColor("W-9"); updateCryptColor("W-10"); updateCryptColor("W-11"); updateCryptColor("W-12"); updateCryptColor("W-13"); updateCryptColor("W-14"); updateCryptColor("W-15"); updateCryptColor("W-16"); updateCryptColor("W-17"); updateCryptColor("W-18"); updateCryptColor("W-19"); updateCryptColor("W-20"); updateCryptColor("W-21"); updateCryptColor("W-22"); updateCryptColor("W-23"); updateCryptColor("W-24"); updateCryptColor("W-25"); updateCryptColor("W-26"); updateCryptColor("W-27"); updateCryptColor("W-28"); updateCryptColor("W-29"); updateCryptColor("W-30"); updateCryptColor("W-31"); updateCryptColor("W-32"); updateCryptColor("W-33"); updateCryptColor("W-34"); updateCryptColor("W-35"); updateCryptColor("W-36"); updateCryptColor("W-37"); updateCryptColor("W-38"); updateCryptColor("W-39"); updateCryptColor("W-41"); updateCryptColor("W-42"); updateCryptColor("W-43"); updateCryptColor("W-44"); updateCryptColor("W-45"); updateCryptColor("W-46"); updateCryptColor("W-47"); updateCryptColor("W-48"); updateCryptColor("W-49"); updateCryptColor("W-50"); updateCryptColor("W-51"); updateCryptColor("W-52"); updateCryptColor("W-53"); updateCryptColor("W-54"); updateCryptColor("W-55"); updateCryptColor("W-56"); updateCryptColor("W-57"); updateCryptColor("W-58"); updateCryptColor("W-60"); updateCryptColor("W-61"); updateCryptColor("W-62"); updateCryptColor("W-63"); updateCryptColor("W-64"); updateCryptColor("W-65"); updateCryptColor("W-66"); updateCryptColor("W-67"); updateCryptColor("W-68"); updateCryptColor("W-69"); updateCryptColor("W-70"); updateCryptColor("W-71"); updateCryptColor("W-72"); updateCryptColor("W-73"); updateCryptColor("W-74"); updateCryptColor("W-75"); updateCryptColor("W-76"); updateCryptColor("W-77"); updateCryptColor("W-78"); updateCryptColor("W-79"); updateCryptColor("W-80"); updateCryptColor("W-81"); updateCryptColor("W-82"); updateCryptColor("W-83"); updateCryptColor("W-84"); updateCryptColor("W-85"); updateCryptColor("W-86"); updateCryptColor("W-87"); updateCryptColor("W-88"); updateCryptColor("W-89"); updateCryptColor("W-90"); updateCryptColor("W-91"); updateCryptColor("W-92"); updateCryptColor("W-93"); updateCryptColor("W-94"); updateCryptColor("W-95"); updateCryptColor("W-96"); updateCryptColor("W-97"); updateCryptColor("W-98"); updateCryptColor("W-99"); updateCryptColor("W-99A"); updateCryptColor("W-100"); updateCryptColor("W-101"); updateCryptColor("W-102"); updateCryptColor("W-103"); updateCryptColor("W-104"); updateCryptColor("W-105"); updateCryptColor("W-106"); updateCryptColor("W-106A"); updateCryptColor("W-107"); updateCryptColor("W-107A"); updateCryptColor("W-108"); updateCryptColor("W-109"); updateCryptColor("W-110"); updateCryptColor("W-111"); updateCryptColor("W-112"); updateCryptColor("W-113"); updateCryptColor("W-114"); updateCryptColor("W-115"); updateCryptColor("W-116"); updateCryptColor("W-117"); updateCryptColor("W-118"); updateCryptColor("W-119"); updateCryptColor("W-120"); updateCryptColor("W-121"); updateCryptColor("W-122"); updateCryptColor("W-123"); updateCryptColor("W-124"); updateCryptColor("W-125"); updateCryptColor("W-126"); updateCryptColor("W-127"); updateCryptColor("W-128"); updateCryptColor("W-129"); updateCryptColor("W-130"); updateCryptColor("W-131"); updateCryptColor("W-132"); updateCryptColor("W-133"); updateCryptColor("W-134"); updateCryptColor("W-135"); updateCryptColor("W-136"); updateCryptColor("W-137"); updateCryptColor("W-138"); updateCryptColor("W-139"); updateCryptColor("W-140"); updateCryptColor("W-141"); updateCryptColor("W-142"); updateCryptColor("W-143"); updateCryptColor("W-144"); updateCryptColor("W-145"); updateCryptColor("W-146"); updateCryptColor("W-147"); updateCryptColor("W-148"); updateCryptColor("W-149"); updateCryptColor("W-150"); updateCryptColor("W-151"); updateCryptColor("W-152"); updateCryptColor("W-153"); updateCryptColor("W-154"); updateCryptColor("W-155"); updateCryptColor("W-156"); updateCryptColor("W-156A"); updateCryptColor("W-156B"); updateCryptColor("W-156C"); updateCryptColor("W-156D"); updateCryptColor("W-157"); updateCryptColor("W-158"); updateCryptColor("W-159"); updateCryptColor("W-160"); updateCryptColor("W-161"); updateCryptColor("W-162"); updateCryptColor("W-163"); updateCryptColor("W-164"); updateCryptColor("W-164A"); updateCryptColor("W-164B"); updateCryptColor("W-164C"); updateCryptColor("W-164D");updateCryptColor("W-164I"); updateCryptColor("W-164E"); updateCryptColor("W-164F"); updateCryptColor("W-164G"); updateCryptColor("W-164H"); updateCryptColor("W-165"); updateCryptColor("W-166"); updateCryptColor("W-167"); updateCryptColor("W-168"); updateCryptColor("W-169"); updateCryptColor("W-170"); updateCryptColor("W-171");updateCryptColor("W-172"); updateCryptColor("W-173"); updateCryptColor("W-174"); updateCryptColor("W-175"); updateCryptColor("W-176"); updateCryptColor("W-177"); updateCryptColor("W-178"); updateCryptColor("W-179"); updateCryptColor("W-180"); updateCryptColor("W-181A"); updateCryptColor("W-181"); updateCryptColor("W-182"); updateCryptColor("W-183"); updateCryptColor("W-184"); updateCryptColor("W-185"); updateCryptColor("W-187"); updateCryptColor("W-188");updateCryptColor("W-184"); updateCryptColor("W-185");updateCryptColor("W-186");updateCryptColor("W-187");updateCryptColor("W-188");updateCryptColor("W-189");updateCryptColor("W-190");updateCryptColor("W-191");updateCryptColor("W-192");updateCryptColor("W-193");updateCryptColor("W-194A"); updateCryptColor("W-194"); updateCryptColor("W-195");updateCryptColor("W-196");updateCryptColor("W-197");updateCryptColor("W-198");updateCryptColor("W-199");updateCryptColor("W-200");updateCryptColor("W-201");updateCryptColor("W-202");updateCryptColor("W-203");updateCryptColor("W-204");updateCryptColor("W-205");updateCryptColor("W-206");updateCryptColor("W-207");updateCryptColor("W-208");updateCryptColor("W-209");updateCryptColor("W-210");updateCryptColor("W-211");updateCryptColor("W-212");
    // Add more sections as needed...
  }

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
            // Loop through potential levels (A to E)
            ['A', 'B', 'C', 'D', 'E'].forEach(level => {
                let levelElement = document.getElementById(`level-${level}`);
                if (levelElement) { // Ensure element exists
                    if (data.levels.hasOwnProperty(level)) {
                        // Set color if the level exists
                        levelElement.setAttribute('fill', data.levels[level] ? 'red' : 'green');
                    } else {
                        // Remove the level from SVG if it doesn't exist
                        levelElement.remove();
                    }
                }
            });

            // Populate dropdown with available levels
            let dropdown = document.getElementById('level-select');
            dropdown.innerHTML = ''; // Clear previous options
            Object.keys(data.levels).forEach(level => {
                if (!data.levels[level]) {  // If level is vacant
                    let option = document.createElement('option');
                    option.value = level;
                    option.textContent = level;
                    dropdown.appendChild(option);
                }
            });

            document.getElementById('popup').style.display = 'block';
            document.getElementById('overlay').style.display = 'block';
        });
}



function closePopup() {
    document.getElementById('popup').style.display = 'none';
    document.getElementById('overlay').style.display = 'none';
}
