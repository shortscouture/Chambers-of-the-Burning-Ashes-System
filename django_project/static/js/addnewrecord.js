// Function to toggle payment fields based on selected payment mode
function togglePaymentFields() {
    var paymentMode = document.getElementById("id_mode_of_payment").value;
    var fullPaymentFields = document.getElementById("full_payment_fields");
    var installmentFields = document.getElementById("installment_payment_fields");

    if (paymentMode === "Full Payment") {
        fullPaymentFields.style.display = "block";
        installmentFields.style.display = "none";
    } else if (paymentMode === "6-Month Installment") {
        fullPaymentFields.style.display = "none";
        installmentFields.style.display = "block";
    } else {
        fullPaymentFields.style.display = "none";
        installmentFields.style.display = "none";
    }
}

// Initialize payment fields on page load
document.addEventListener("DOMContentLoaded", function () {
    togglePaymentFields();
});

// Webcam and OCR variables
let stream = null;
let capturedImage = null;

// Toggle between webcam and file upload
document.getElementById('webcamOption').addEventListener('click', function () {
    document.getElementById('webcam-container').style.display = 'block';
    document.getElementById('fileUploadContainer').style.display = 'none';
    initializeWebcam();
});

document.getElementById('uploadOption').addEventListener('click', function () {
    document.getElementById('webcam-container').style.display = 'none';
    document.getElementById('fileUploadContainer').style.display = 'block';
    stopWebcam();
});

// Initialize webcam
async function initializeWebcam() {
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
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
}

// Capture image from webcam
document.getElementById('captureButton').addEventListener('click', function () {
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

    // Store captured image as base64
    capturedImage = canvas.toDataURL('image/jpeg');
});

// Retake photo
document.getElementById('retakeButton').addEventListener('click', function () {
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
    if (!capturedImage) return;

    // Convert base64 to blob
    fetch(capturedImage)
        .then(res => res.blob())
        .then(blob => {
            processImage(blob);
        });
});

// Process uploaded file
document.getElementById('processFileButton').addEventListener('click', function () {
    const fileInput = document.getElementById('ocrInput');
    if (!fileInput.files.length) {
        alert('Please select a file first');
        return;
    }

    processImage(fileInput.files[0]);
});

// Common image processing function
function processImage(imageBlob) {
    const formData = new FormData();
    formData.append('document', imageBlob);
    formData.append('csrfmiddlewaretoken', '{{ csrf_token }}');

    // Show processing overlay
    document.getElementById('processingOverlay').style.display = 'flex';

    fetch('/process-ocr/', {
        method: 'POST',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Populate form fields with extracted data
                const nameParts = data.data.full_name.split(' ');
                if (nameParts.length > 0) {
                    document.querySelector('[name="first_name"]').value = nameParts[0] || '';
                    if (nameParts.length > 1) {
                        document.querySelector('[name="last_name"]').value = nameParts[nameParts.length - 1] || '';
                    }
                    if (nameParts.length > 2) {
                        document.querySelector('[name="middle_name"]').value = nameParts.slice(1, -1).join(' ') || '';
                    }
                }

                const addressParts = data.data.permanent_address.split(',');
                if (addressParts.length > 0) {
                    document.querySelector('[name="address_line_1"]').value = addressParts[0].trim() || '';
                    if (addressParts.length > 1) {
                        document.querySelector('[name="city"]').value = addressParts[1].trim() || '';
                    }
                    if (addressParts.length > 2) {
                        document.querySelector('[name="province_or_state"]').value = addressParts[2].trim() || '';
                    }
                }

                document.querySelector('[name="mobile_number"]').value = data.data.mobile_number || '';
                document.querySelector('[name="landline_number"]').value = data.data.landline_number || '';
                document.querySelector('[name="email_address"]').value = data.data.email_address || '';

                document.querySelector('[name="first_beneficiary_name"]').value = data.data.first_beneficiary_name || '';
                document.querySelector('[name="second_beneficiary_name"]').value = data.data.second_beneficiary_name || '';
                document.querySelector('[name="third_beneficiary_name"]').value = data.data.third_beneficiary_name || '';

                document.querySelector('[name="vault_id"]').value = data.data.vault_id || '';
                document.querySelector('[name="issuance_date"]').value = data.data.issuance_date || '';
                document.querySelector('[name="expiration_date"]').value = data.data.expiration_date || '';
                document.querySelector('[name="inurnment_date"]').value = data.data.inurnment_date || '';
                document.querySelector('[name="issuing_parish_priest"]').value = data.data.issuing_parish_priest || '';
                document.querySelector('[name="urns_per_columbary"]').value = data.data.urns_per_columbary || '';
            } else {
                alert('Error processing document: ' + data.error);
            }
        })
        .catch(error => {
            alert('Error: ' + error);
        })
        .finally(() => {
            // Hide processing overlay
            document.getElementById('processingOverlay').style.display = 'none';
        });
}

// Clean up on page unload
window.addEventListener('beforeunload', stopWebcam);