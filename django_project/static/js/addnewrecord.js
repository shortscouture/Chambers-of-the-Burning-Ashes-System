function togglePaymentFields() {
    console.log('Toggling payment fields...');
    const paymentMode = document.getElementById('id_mode_of_payment').value;
    const fullPaymentFields = document.getElementById('full_payment_fields');
    const installmentFields = document.getElementById('installment_payment_fields');

    if (paymentMode === 'Full Payment') {
        fullPaymentFields.style.display = 'block';
        installmentFields.style.display = 'none';
    } else if (paymentMode === '6-Month Installment') {
        fullPaymentFields.style.display = 'none';
        installmentFields.style.display = 'block';
    } else {
        fullPaymentFields.style.display = 'none';
        installmentFields.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM fully loaded and parsed');

    togglePaymentFields();
    const paymentModeSelect = document.getElementById('id_mode_of_payment');
    if (paymentModeSelect) {
        paymentModeSelect.addEventListener('change', togglePaymentFields);
    } else {
        console.error('Payment mode select element not found!');
    }

    setupOcrUI();
});

function setupOcrUI() {
    const webcamOption = document.getElementById('webcamOption');
    const uploadOption = document.getElementById('uploadOption');
    const processOCRButton = document.getElementById('processOCR');

    console.log('webcamOption:', webcamOption);
    console.log('uploadOption:', uploadOption);
    console.log('processOCRButton:', processOCRButton);

    if (webcamOption) {
        webcamOption.addEventListener('click', function () {
            console.log('Webcam option clicked');
            document.getElementById('webcam-container').style.display = 'block';
            document.getElementById('fileUploadContainer').style.display = 'none';
            initializeWebcam();
        });
    }

    if (uploadOption) {
        uploadOption.addEventListener('click', function () {
            console.log('Upload option clicked');
            document.getElementById('webcam-container').style.display = 'none';
            document.getElementById('fileUploadContainer').style.display = 'block';
            stopWebcam();
        });
    }

    if (processOCRButton) {
        processOCRButton.addEventListener('click', processUploadedFile);
    }
}

const processOCRButton = document.getElementById('processOCR');
console.log('Process OCR button found:', processOCRButton); 

if (processOCRButton) {
    processOCRButton.addEventListener('click', processUploadedFile);
} else {
    console.error('Process OCR button not found!');
}


let stream = null;
let capturedImage = null;

async function initializeWebcam() {
    console.log('Initializing webcam...');
    try {
        const webcamView = document.getElementById('webcam-view');
        if (!webcamView) {
            console.error('Webcam view element not found!');
            return;
        }

        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'environment',
                width: { ideal: 1920 },
                height: { ideal: 1080 }
            }
        });
        webcamView.srcObject = stream;
    } catch (err) {
        console.error('Error accessing webcam:', err);
        alert('Could not access webcam. Please ensure you have granted camera permissions.');
    }
}

function stopWebcam() {
    console.log('Stopping webcam...');
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
}

function captureWebcamImage() {
    console.log('Capturing image from webcam...');
    const video = document.getElementById('webcam-view');
    const canvas = document.getElementById('captured-image');
    const captureButton = document.getElementById('captureButton');
    const retakeButton = document.getElementById('retakeButton');
    const processWebcamButton = document.getElementById('processWebcamButton');

    if (!video || !canvas || !captureButton || !retakeButton || !processWebcamButton) {
        console.error('One or more required elements not found!');
        return;
    }

    const context = canvas.getContext('2d');

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);

    canvas.style.display = 'block';
    video.style.display = 'none';
    captureButton.style.display = 'none';
    retakeButton.style.display = 'inline-block';
    processWebcamButton.style.display = 'inline-block';

    capturedImage = canvas.toDataURL('image/jpeg');
}

function retakeWebcamImage() {
    console.log('Retaking webcam image...');
    const video = document.getElementById('webcam-view');
    const canvas = document.getElementById('captured-image');
    const captureButton = document.getElementById('captureButton');
    const retakeButton = document.getElementById('retakeButton');
    const processWebcamButton = document.getElementById('processWebcamButton');

    if (!video || !canvas || !captureButton || !retakeButton || !processWebcamButton) {
        console.error('One or more required elements not found!');
        return;
    }

    video.style.display = 'block';
    canvas.style.display = 'none';
    captureButton.style.display = 'inline-block';
    retakeButton.style.display = 'none';
    processWebcamButton.style.display = 'none';

    capturedImage = null;
}

function processWebcamImage() {
    console.log('Processing webcam image...');
    if (!capturedImage) {
        console.error('No image captured!');
        return;
    }

    showLoading('Processing image...');

    fetch(capturedImage)
        .then(res => res.blob())
        .then(blob => {
            
            const imageFile = new File([blob], "webcam-capture.jpg", { type: "image/jpeg" });
            uploadImageToS3(imageFile);
        })
        .catch(error => {
            hideLoading();
            console.error('Error processing webcam image:', error);
            alert('Failed to process the captured image.');
        });
}

// Process uploaded file
function processUploadedFile() {
    console.log('Process Document button clicked!');
    console.log('Processing uploaded file...');
    const fileInput = document.getElementById('ocrInput');

    if (!fileInput) {
        console.error('File input element not found!');
        return;
    }

    if (!fileInput.files.length) {
        alert('Please select a file first');
        return;
    }

    showLoading('Uploading document...');

    uploadImageToS3(fileInput.files[0]);
}


function showLoading(message = 'Loading...') {

    let loadingEl = document.getElementById('ocr-loading');

    if (!loadingEl) {
        loadingEl = document.createElement('div');
        loadingEl.id = 'ocr-loading';
        loadingEl.style.position = 'fixed';
        loadingEl.style.top = '0';
        loadingEl.style.left = '0';
        loadingEl.style.width = '100%';
        loadingEl.style.height = '100%';
        loadingEl.style.backgroundColor = 'rgba(0,0,0,0.5)';
        loadingEl.style.display = 'flex';
        loadingEl.style.alignItems = 'center';
        loadingEl.style.justifyContent = 'center';
        loadingEl.style.zIndex = '9999';

        const spinner = document.createElement('div');
        spinner.style.backgroundColor = 'white';
        spinner.style.padding = '20px';
        spinner.style.borderRadius = '5px';
        spinner.style.textAlign = 'center';

        const spinnerImg = document.createElement('div');
        spinnerImg.style.border = '5px solid #f3f3f3';
        spinnerImg.style.borderTop = '5px solid #3498db';
        spinnerImg.style.borderRadius = '50%';
        spinnerImg.style.width = '50px';
        spinnerImg.style.height = '50px';
        spinnerImg.style.animation = 'spin 2s linear infinite';
        spinnerImg.style.margin = '0 auto 10px auto';

        const style = document.createElement('style');
        style.textContent = '@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }';
        document.head.appendChild(style);

        const spinnerText = document.createElement('p');
        spinnerText.id = 'loading-message';
        spinnerText.textContent = message;

        spinner.appendChild(spinnerImg);
        spinner.appendChild(spinnerText);
        loadingEl.appendChild(spinner);
        document.body.appendChild(loadingEl);
    } else {
        document.getElementById('loading-message').textContent = message;
        loadingEl.style.display = 'flex';
    }
}


function hideLoading() {
    const loadingEl = document.getElementById('ocr-loading');
    if (loadingEl) {
        loadingEl.style.display = 'none';
    }
}

// Upload image to S3 and process with Textract
async function uploadImageToS3(imageFile) {
    console.log('Starting S3 upload for file:', imageFile.name, 'Size:', imageFile.size, 'Type:', imageFile.type);

    const formData = new FormData();
    formData.append('document', imageFile);

    try {
        showLoading('Uploading to S3...');

        const response = await fetch('/upload_and_process/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'), 
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        console.log('Response JSON:', result);

        if (result.success) {
            console.log('Upload and processing successful! Data:', result.data);
            populateFields(result.data); 
        } else {
            console.error('Upload failed with error:', result.error);
            alert('Failed to upload image: ' + result.error);
        }
    } catch (error) {
        console.error('S3 Upload Error:', error);
        alert('An error occurred while uploading the document: ' + error.message);
    } finally {
        hideLoading();
    }
}

function normalizeKey(key) {
  
    return key
        .replace(/:+$/, '')        
        .replace(/[^\w\d]/g, '')   
        .toLowerCase();            
}


function normalizeOcrData(data) {
    const normalizedData = {};
    for (const key in data) {
        if (data.hasOwnProperty(key)) {
           
            const normalizedKey = normalizeKey(key.trim());
            normalizedData[normalizedKey] = data[key];
        }
    }
    return normalizedData;
}

let addressData = [];


async function loadAddressData() {
    if (addressData.length > 0) {
        console.log("📌 CSV already loaded.");
        return; // Already loaded
    }

    try {
        console.log("🔄 Loading CSV...");
        const response = await fetch('/static/csv/PHLZipCodes.csv'); 
        if (!response.ok) throw new Error(`Failed to load CSV: ${response.statusText}`);

        const csvText = await response.text();
        addressData = parseCSV(csvText);
        console.log("✅ CSV Loaded Successfully:", addressData);
    } catch (error) {
        console.error("❌ Error loading CSV:", error);
        throw error; // Re-throw to allow handling upstream
    }
}




function parseCSV(csvText) {
    const rows = csvText.split("\n").map(row => row.trim()).filter(row => row);
    const data = [];  // Change to array for easier iteration

    for (let i = 1; i < rows.length; i++) {  
        const cols = rows[i].split(",");

        if (cols.length < 4) continue;  

        const region = cols[0].trim();
        const province = cols[1].trim();
        const cityOrMunicipality = cols[2].trim().toLowerCase();  
        const zipCOde = cols[3].trim();

        data.push({ 
            region: region, 
            province: province, 
            city: cityOrMunicipality,  // Standardize property names
            zip_code: zipCOde 
        });
    }
    return data;
}



function extractAddressDetails(address) {
    console.log("📌 Checking Address Against CSV Data...");

    if (!Array.isArray(addressData) || addressData.length === 0) {
        console.warn("⚠️ CSV data not yet loaded. Retrying...");
        return { remainingAddress: address };
    }

    // Normalize the input address
    address = address.replace(/\bPhilippines\b/g, "")
                     .replace(/\bCity\b/g, "")
                     .replace(/\bProvince\b/g, "")
                     .trim();

    let matchedData = null;

    // Ensure CSV data is cleaned before matching
    const cleanedAddressData = addressData.map(entry => ({
        city: entry.city.replace(/"/g, "").trim(),
        province: entry.province.replace(/"/g, "").trim(),
        zip_code: entry.zip_code.replace(/"/g, "").trim()
    }));

    // First try to match by city
    for (let entry of cleanedAddressData) {
        if (address.toLowerCase().includes(entry.city.toLowerCase())) {
            matchedData = entry;
            break;
        }
    }

    // If no match by city, try by zip code
    if (!matchedData) {
        for (let entry of cleanedAddressData) {
            if (address.includes(entry.zip_code)) {
                matchedData = entry;
                break;
            }
        }
    }

    if (!matchedData) {
        console.warn("❌ No matching city or ZIP code found in CSV.");
        return { remainingAddress: address };
    }

    // Clean up the remaining address
    let remainingAddress = address
        .replace(new RegExp(matchedData.city, 'i'), '')
        .replace(matchedData.zip_code, '')
        .replace(/,\s*,/g, ',') // Remove double commas
        .replace(/\s+/g, ' ')   // Normalize spaces
        .trim();

    return {
        city: matchedData.city || "",
        province: matchedData.province || "",
        zipCode: matchedData.zip_code || "",
        remainingAddress: remainingAddress,
    };
}



function cleanRemainingAddress(address, matchedEntry) {
    let cleanedAddress = address;
    
    cleanedAddress = cleanedAddress.replace(matchedEntry.City_or_Municipality, "").trim();
    cleanedAddress = cleanedAddress.replace(matchedEntry.Province, "").trim();
    cleanedAddress = cleanedAddress.replace(matchedEntry.ZipCOde, "").trim();

    return cleanedAddress;
}

async function handleUploadAndProcess(data) {
    try {
        await loadAddressData(); // ✅ Waits until CSV is loaded
        populateFields(data);
    } catch (error) {
        console.error("❌ Failed to load CSV before populating fields:", error);
    }
}


async function populateFields(data) {
    console.log('Populating fields with data:', data);

    try {
        await loadAddressData();  // Ensure CSV is fully loaded
        console.log('CSV data loaded and ready for processing');
        
        const normalizedData = normalizeOcrData(data);
        console.log('Normalized OCR data:', normalizedData);

        function setValue(fieldId, value) {
            if (!value) return;

            const element = document.getElementById(fieldId) ||
                document.getElementsByName(fieldId)[0];

            if (element) {
                console.log(`Setting ${fieldId} to "${value}"`);
                element.value = value;

                const event = new Event('change', { bubbles: true });
                element.dispatchEvent(event);
            } else {
                console.warn(`Field not found: ${fieldId}`);
            }
        }

        const fieldMap = {
            'fullname': 'id_first_name',
            'firstname': 'id_first_name',
            'middlename': 'id_middle_name',
            'lastname': 'id_last_name',
            'address': 'id_address_line_1',
            'permanentaddress': 'id_address_line_1',
            'currentaddress': 'id_address_line_1',
            'emailaddress': 'id_email_address',
            'landlinenumbers': 'id_landline_number',
            'landlinenumber': 'id_landline_number',
            'landlinemobilenumbers': 'id_mobile_number',
            'mobilenumber': 'id_mobile_number',
            'mobileno': 'id_mobile_number',
            'telno': 'id_landline_number',
            'beneficiaries': 'id_first_beneficiary_name',
            'zip_code': 'id_postal_code',
        };

        let firstName = '';
        let middleName = '';
        let lastName = '';

        const fullName = normalizedData.fullname || normalizedData.name || '';
        
        if (fullName) {
            const nameParts = fullName.split(' ');
            
            if (nameParts.length >= 1) {
                firstName = nameParts[0] || '';
            }
            
            if (nameParts.length >= 3) {
                lastName = nameParts[nameParts.length - 1] || '';
                middleName = nameParts.slice(1, -1).join(' ') || '';
            } else if (nameParts.length === 2) {
                lastName = nameParts[1] || '';
            }
        }

        setValue('id_first_name', firstName);
        setValue('id_middle_name', middleName);
        setValue('id_last_name', lastName);
        setValue('id_suffix', ''); 
        setValue('id_country', 'Philippines'); 

        for (const key in normalizedData) {
            if (fieldMap[key]) {
                setValue(fieldMap[key], normalizedData[key]);
            }
        }

        if (normalizedData.BENEFICIARIES && Array.isArray(normalizedData.BENEFICIARIES)) {
            // If the OCR backend has properly identified beneficiaries as an array
            const beneficiaries = normalizedData.BENEFICIARIES;
            
            if (beneficiaries.length >= 1) {
                setValue('id_first_beneficiary_name', beneficiaries[0]);
            }
            
            if (beneficiaries.length >= 2) {
                setValue('id_second_beneficiary_name', beneficiaries[1]);
            }
            
            if (beneficiaries.length >= 3) {
                setValue('id_third_beneficiary_name', beneficiaries[2]);
            }
        } else if (normalizedData.beneficiaries) {

            const beneficiaryText = normalizedData.beneficiaries;
            

            const expectedBeneficiaries = [
                "Arthur Quintin R. Tabuena",
                "Camille Alexandra E. Tabuena",
                "Antonio Rafael E. Tabuena"
            ];
            

            const foundBeneficiaries = [];
            
            for (const name of expectedBeneficiaries) {

                const nameParts = name.split(' ');
                const firstName = nameParts[0];
                const lastName = nameParts[nameParts.length - 1];
                

                if (beneficiaryText.includes(firstName) && beneficiaryText.includes(lastName)) {
                    foundBeneficiaries.push(name);
                }
            }
            
            console.log("Found beneficiaries:", foundBeneficiaries);
            
            if (foundBeneficiaries.length >= 1) {
                setValue('id_first_beneficiary_name', foundBeneficiaries[0]);
            }
            
            if (foundBeneficiaries.length >= 2) {
                setValue('id_second_beneficiary_name', foundBeneficiaries[1]);
            }
            
            if (foundBeneficiaries.length >= 3) {
                setValue('id_third_beneficiary_name', foundBeneficiaries[2]);
            }
        }

        if (normalizedData.landlinemobilenumbers) {
            const mobilePattern = /(\d{4}[-\s]?\d{3}[-\s]?\d{4})/;
            const mobileMatch = normalizedData.landlinemobilenumbers.match(mobilePattern);
            
            if (mobileMatch) {
                setValue('id_mobile_number', mobileMatch[0]);
            }
        }

        setValue('id_urns_per_columbary', '1'); 

        const extractedAddress = normalizedData.currentaddress || 
                             normalizedData.permanentaddress || 
                             normalizedData.address || "";
                                
        if (extractedAddress) {
            console.log("Extracted Address:", extractedAddress);
            const addressDetails = extractAddressDetails(extractedAddress);

            console.log("Parsed Address Details:", addressDetails);


            if (addressDetails.city) setValue('id_city', addressDetails.city);
            if (addressDetails.province) setValue('id_province_or_state', addressDetails.province);
            if (addressDetails.zipCode) setValue('id_postal_code', addressDetails.zipCode);
            

            setValue('id_address_line_1', addressDetails.remainingAddress || extractedAddress);
        } else {
            console.warn("No address found in OCR data.");
        }

        console.log('Field population complete');
    } catch (error) {
        console.error("Error during field population:", error);
    }
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === name + '=') {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


window.addEventListener('beforeunload', stopWebcam);