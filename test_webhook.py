import requests
import os

# --- 1. Configuration ---

# **IMPORTANT:** Use the full Webhook URL shown in your n8n node (Test or Production)
WEBHOOK_URL = 'http://localhost:5678/webhook-test/image-upload'

# **IMPORTANT:** This must match the 'Field Name for Binary Data' in your n8n node.
FILE_FIELD_NAME = 'data'

# Path to the image file you want to upload
# Replace 'test_image.jpg' with the actual path to your local image file.
IMAGE_FILE_PATH = "./rvl_cdip_invoice_images/invoice_00002.png"

# --- 2. Request Logic ---

try:
    if not os.path.exists(IMAGE_FILE_PATH):
        raise FileNotFoundError(f"File not found at: {IMAGE_FILE_PATH}")

    # Open the file in binary mode for the POST request
    with open(IMAGE_FILE_PATH, 'rb') as f:
        # The 'files' dictionary is used for multipart/form-data.
        # Format: {'field_name': (filename, file_object, content_type)}
        files = {
            FILE_FIELD_NAME: (os.path.basename(IMAGE_FILE_PATH), f, 'image/jpeg')
            # You can change 'image/jpeg' to 'image/png' or 'image/webp' depending on your file type
        }

        print(f"Sending POST request to: {WEBHOOK_URL}")
        print(f"File field name used: {FILE_FIELD_NAME}")
        print(f"Attempting to upload file: {os.path.basename(IMAGE_FILE_PATH)}")

        # Send the POST request
        response = requests.post(WEBHOOK_URL, files=files)

    # --- 3. Check Response ---
    
    print("\n--- Response ---")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

    if response.status_code == 200:
        print("\n✅ Success! The webhook received the file.")
    else:
        print("\n❌ Failure. Check your n8n workflow for errors.")

except FileNotFoundError as e:
    print(f"Error: {e}")
except requests.exceptions.RequestException as e:
    print(f"An error occurred during the request: {e}")