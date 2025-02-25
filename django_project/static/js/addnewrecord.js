// Debugging: Check if the JavaScript file is loaded
console.log('addnewrecord.js loaded!');

// Function to toggle payment fields based on selected payment mode
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

// Initialize payment fields on page load
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM fully loaded and parsed');

    // Initialize payment fields
    togglePaymentFields();
    const paymentModeSelect = document.getElementById('id_mode_of_payment');
    if (paymentModeSelect) {
        paymentModeSelect.addEventListener('change', togglePaymentFields);
    } else {
        console.error('Payment mode select element not found!');
    }

    // Initialize OCR UI elements
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
    // Set up file upload processing
const processOCRButton = document.getElementById('processOCR');
console.log('Process OCR button found:', processOCRButton); // Debug log

if (processOCRButton) {
    processOCRButton.addEventListener('click', processUploadedFile);
} else {
    console.error('Process OCR button not found!');
}


// Webcam and OCR variables
let stream = null;
let capturedImage = null;

// Initialize webcam
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

// Stop webcam
function stopWebcam() {
    console.log('Stopping webcam...');
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
}

// Capture image from webcam
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

// Retake photo
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

// Process webcam image
function processWebcamImage() {
    console.log('Processing webcam image...');
    if (!capturedImage) {
        console.error('No image captured!');
        return;
    }

    // Show loading indicator
    showLoading('Processing image...');

    fetch(capturedImage)
        .then(res => res.blob())
        .then(blob => {
            // Create a file from the blob
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

    // Show loading indicator
    showLoading('Uploading document...');

    uploadImageToS3(fileInput.files[0]);
}

// Show loading indicator
function showLoading(message = 'Loading...') {
    // Create loading element if it doesn't exist
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

// Hide loading indicator
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
                'X-CSRFToken': getCookie('csrftoken'), // Ensure CSRF token is included
            },
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        console.log('Response JSON:', result);

        if (result.success) {
            console.log('Upload and processing successful! Data:', result.data);
            populateFields(result.data); // Populate form fields with extracted data
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


// Populate form fields with OCR data
function populateFields(data) {
    console.log('Populating fields with data:', data);

    // Helper function to set value if field exists
    function setValue(fieldId, value) {
        if (!value) return;

        const element = document.getElementById(fieldId) ||
            document.getElementsByName(fieldId)[0];

        if (element) {
            console.log(`Setting ${fieldId} to "${value}"`);
            element.value = value;

            // Trigger change event for any listeners
            const event = new Event('change', { bubbles: true });
            element.dispatchEvent(event);
        } else {
            console.warn(`Field not found: ${fieldId}`);
        }
    }

    // Extract first, middle, and last name from the "Name" field
    const fullName = data.Name || '';
    const nameParts = fullName.split(' ');
    const firstName = nameParts[0] || '';
    const middleName = nameParts.slice(1, -1).join(' ') || '';
    const lastName = nameParts[nameParts.length - 1] || '';

    // Map OCR data to form fields
    setValue('id_first_name', firstName);
    setValue('id_middle_name', middleName);
    setValue('id_last_name', lastName);
    setValue('id_suffix', ''); 
    setValue('id_country', 'Philippines'); 
    setValue('id_address_line_1', data.Address || data.Addres || ''); 
    setValue('id_address_line_2', ''); 
    setValue('id_city', ''); 
    setValue('id_province_or_state', ''); 
    setValue('id_postal_code', ''); 
    setValue('id_landline_number', data['Landline No.'] || '');
    setValue('id_mobile_number', data['Mobile No.'] || '');
    setValue('id_email_address', ''); 

    // Beneficiary fields
    setValue('id_first_beneficiary_name', data['1'] || ''); 
    setValue('id_second_beneficiary_name', data['2'] || ''); 
    setValue('id_third_beneficiary_name', data['3'] || ''); 

    // Other fields
    setValue('id_vault_id', ''); 
    setValue('id_inurnment_date', ''); 
    setValue('id_urns_per_columbary', '1'); 
}

// Function to get CSRF token
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

// Clean up webcam when leaving the page
window.addEventListener('beforeunload', stopWebcam);