from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from cryptography.fernet import Fernet
import os

# FastAPI instance
app = FastAPI()

# CORS middleware to allow React frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow any origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow any HTTP methods
    allow_headers=["*"],  # Allow any headers
)

# Define the folder to store images
UPLOAD_FOLDER = 'uploaded_images'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Generate a secret key for encryption (you should store this key securely and reuse it)
key = Fernet.generate_key()
cipher_suite = Fernet(key)

# Save this key securely in a safe location (e.g., environment variable or key management system)
print(f"Encryption key: {key.decode()}")  # Output the key, make sure to save it somewhere

@app.post("/upload/")
async def upload_image(image: UploadFile = File(...)):
    try:
        # Read the image content
        image_data = await image.read()

        # Encrypt the image content using the Fernet cipher
        encrypted_data = cipher_suite.encrypt(image_data)
        
        # Save the encrypted data to the file system
        file_path = os.path.join(UPLOAD_FOLDER, f"{image.filename}.enc")
        with open(file_path, "wb") as f:
            f.write(encrypted_data)

        return JSONResponse(content={"message": "Image uploaded and encrypted successfully!"}, status_code=200)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Endpoint to download and decrypt the image
@app.get("/download/{filename}")
async def download_image(filename: str):
    try:
        # Construct the path of the encrypted file
        file_path = os.path.join(UPLOAD_FOLDER, f"{filename}.enc")

        if not os.path.exists(file_path):
            return JSONResponse(content={"error": "File not found"}, status_code=404)

        # Read the encrypted file content
        with open(file_path, "rb") as f:
            encrypted_data = f.read()

        # Decrypt the file content
        decrypted_data = cipher_suite.decrypt(encrypted_data)

        # Return the decrypted file content as a response
        return JSONResponse(content={"message": "File decrypted successfully", "file_content": decrypted_data.decode('utf-8')}, status_code=200)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
