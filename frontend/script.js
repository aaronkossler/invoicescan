document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const chooseBtn = document.getElementById('chooseBtn');
    const fileName = document.getElementById('fileName');
    const processBtn = document.getElementById('processBtn');
    const outputBox = document.getElementById('outputBox');

    chooseBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            fileName.textContent = fileInput.files[0].name;
            processBtn.disabled = false;
            outputBox.textContent = 'File selected. Click "Process Invoice" to continue.';
        } else {
            fileName.textContent = 'No file selected';
            processBtn.disabled = true;
            outputBox.textContent = 'Upload an image and click Process Invoice to see results here.';
        }
    });

    processBtn.addEventListener('click', async () => {
        if (fileInput.files.length === 0) return;

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        processBtn.disabled = true;
        processBtn.textContent = 'Processing...';
        outputBox.textContent = 'Processing invoice...';

        try {
            const response = await fetch('/process', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                outputBox.textContent = JSON.stringify(data, null, 2);
            } else {
                outputBox.textContent = 'Error: ' + (data.detail || 'Unknown error');
            }
        } catch (error) {
            outputBox.textContent = 'Error: ' + error.message;
        } finally {
            processBtn.disabled = false;
            processBtn.textContent = 'Process Invoice';
        }
    });
});
