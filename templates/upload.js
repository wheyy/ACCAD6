// Video preview functionality
const videoInput = document.getElementById('videoFile');
const videoPreview = document.getElementById('videoPreview');
const previewContainer = document.getElementById('previewContainer');

videoInput.addEventListener('change', (event) => {
    const file = event.target.files[0];
    if (file) {
        const url = URL.createObjectURL(file);
        videoPreview.src = url;
        previewContainer.style.display = 'block'; // Show the preview container
    } else {
        previewContainer.style.display = 'none'; // Hide the preview if no file is selected
        videoPreview.src = '';
    }
});

// Cancel button functionality
const cancelButton = document.getElementById('cancelButton');
cancelButton.addEventListener('click', () => {
    document.getElementById('uploadForm').reset();
    previewContainer.style.display = 'none'; // Hide the preview
    videoPreview.src = ''; // Clear the video source
});