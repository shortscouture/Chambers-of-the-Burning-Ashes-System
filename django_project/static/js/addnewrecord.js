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
    togglePaymentFields();

    // Add event listener for payment mode change
    const paymentModeSelect = document.getElementById('id_mode_of_payment');
    if (paymentModeSelect) {
        paymentModeSelect.addEventListener('change', togglePaymentFields);
    } else {
        console.error('Payment mode select element not found!');
    }
});

// Webcam and OCR variables
let stream = null;
let capturedImage = null;

// Toggle between webcam and file upload
document.getElementById('webcamOption').addEventListener('click', function () {
    console.log('Webcam option clicked');
    document.getElementById('webcam-container').style.display = 'block';
    document.getElementById('fileUploadContainer').style.display = 'none';
    initializeWebcam();
});

document.getElementById('uploadOption').addEventListener('click', function () {
    console.log('Upload option clicked');
    document.getElementById('webcam-container').style.display = 'none';
    document.getElementById('fileUploadContainer').style.display = 'block';
    stopWebcam();
});

// Initialize webcam
async function initializeWebcam() {
    console.log('Initializing webcam...');
    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: 'environment', // Use the rear camera
                width: { ideal: 1920 },
                height: { ideal: 1080 }
            }
        });
        document.getElementById('webcam-view').srcObject = stream;
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
document.getElementById('captureButton').addEventListener('click', function () {
    console.log('Capture button clicked');
    const video = document.getElementById('webcam-view');
    const canvas = document.getElementById('captured-image');
    const context = canvas.getContext('2d');

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame to canvas
    context.drawImage(video, 0, 0);

    // Show captured image
    canvas.style.display = 'block';
    video.style.display = 'none';

    // Update buttons
    this.style.display = 'none';
    document.getElementById('retakeButton').style.display = 'inline-block';
    document.getElementById('processWebcamButton').style.display = 'inline-block';

    capturedImage = canvas.toDataURL('image/jpeg');
});

// Retake photo
document.getElementById('retakeButton').addEventListener('click', function () {
    console.log('Retake button clicked');
    const video = document.getElementById('webcam-view');
    const canvas = document.getElementById('captured-image');

    // Show video stream again
    video.style.display = 'block';
    canvas.style.display = 'none';

    // Reset buttons
    document.getElementById('captureButton').style.display = 'inline-block';
    this.style.display = 'none';
    document.getElementById('processWebcamButton').style.display = 'none';

    capturedImage = null;
});

// Process captured image from webcam
document.getElementById('processWebcamButton').addEventListener('click', function () {
    console.log('Process webcam button clicked');
    if (!capturedImage) return;

    // Convert base64 to blob
    fetch(capturedImage)
        .then(res => res.blob())
        .then(blob => {
            processImage(blob);
        });
});

// Process uploaded file
document.getElementById('processOCR').addEventListener('click', function () {
    console.log('Process OCR button clicked');
    const fileInput = document.getElementById('ocrInput');
    if (!fileInput.files.length) {
        alert('Please select a file first');
        return;
    }

    processImage(fileInput.files[0]);
});

// Common image processing function
function processImage(imageBlob) {
    console.log('Processing image...');
    const formData = new FormData();
    formData.append('document', imageBlob);
    formData.append('csrfmiddlewaretoken', '{{ csrf_token }}');

    // Show processing overlay
    document.getElementById('processingOverlay').style.display = 'flex';

    fetch('/process-ocr/', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            console.log('Received response:', response);
            return response.json();
        })
        .then(data => {
            console.log('Parsed data:', data);
            if (data.success) {
                // Populate form fields with extracted data
                document.querySelector('[name="first_name"]').value = data.data.first_name || '';
                document.querySelector('[name="middle_name"]').value = data.data.middle_name || '';
                document.querySelector('[name="last_name"]').value = data.data.last_name || '';
                document.querySelector('[name="suffix"]').value = data.data.suffix || '';
                document.querySelector('[name="country"]').value = data.data.country || 'Philippines';
                document.querySelector('[name="address_line_1"]').value = data.data.address_line_1 || '';
                document.querySelector('[name="address_line_2"]').value = data.data.address_line_2 || '';
                document.querySelector('[name="city"]').value = data.data.city || '';
                document.querySelector('[name="province_or_state"]').value = data.data.province_or_state || '';
                document.querySelector('[name="postal_code"]').value = data.data.postal_code || '';
                document.querySelector('[name="landline_number"]').value = data.data.landline_number || '';
                document.querySelector('[name="mobile_number"]').value = data.data.mobile_number || '';
                document.querySelector('[name="email_address"]').value = data.data.email_address || '';
                
                // Populate Beneficiary fields
                document.querySelector('[name="first_beneficiary_name"]').value = data.data.first_beneficiary_name || '';
                document.querySelector('[name="second_beneficiary_name"]').value = data.data.second_beneficiary_name || '';
                document.querySelector('[name="third_beneficiary_name"]').value = data.data.third_beneficiary_name || '';
                
                // Populate ColumbaryRecord fields
                document.querySelector('[name="vault_id"]').value = data.data.vault_id || '';
                document.querySelector('[name="inurnment_date"]').value = data.data.inurnment_date || '';
                document.querySelector('[name="urns_per_columbary"]').value = data.data.urns_per_columbary || '';
            } else {
                alert('Error processing document: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Fetch error:', error);
            alert('Error: ' + error);
        })
        .finally(() => {
            // Hide processing overlay
            document.getElementById('processingOverlay').style.display = 'none';
        });
}

// Clean up on page unload
window.addEventListener('beforeunload', stopWebcam);