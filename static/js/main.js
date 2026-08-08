// Main JavaScript for AI Lost & Found Matching System

document.addEventListener('DOMContentLoaded', function () {
    // Auto dismiss alerts after 6 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 6000);
    });

    // Image Upload Live Preview Handler
    const imageInputs = document.querySelectorAll('input[type="file"][name="image"]');
    imageInputs.forEach(function (input) {
        input.addEventListener('change', function (event) {
            const file = event.target.files[0];
            const previewContainer = document.getElementById('image-preview-container');
            const previewImg = document.getElementById('image-preview');

            if (file && previewContainer && previewImg) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    previewImg.src = e.target.result;
                    previewContainer.classList.remove('d-none');
                };
                reader.readAsDataURL(file);
            }
        });
    });
});
