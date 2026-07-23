import os
import shutil
import uuid
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET")

has_cloudinary = bool(CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET)

if has_cloudinary:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET
    )

def upload_image_or_file(file: UploadFile, folder: str = "campusconnect") -> str:
    """
    Uploads a file to Cloudinary if available, otherwise saves it locally
    and returns the relative URL.
    """
    if has_cloudinary:
        try:
            resource_type = "raw" if file.filename.lower().endswith(".pdf") else "auto"
            upload_result = cloudinary.uploader.upload(
                file.file,
                folder=folder,
                resource_type=resource_type
            )
            return upload_result.get("secure_url")
        except Exception as e:
            print(f"Cloudinary upload failed: {e}. Falling back to local upload.")
    
    # Local fallback
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    upload_dir = os.path.join(base_dir, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Create unique filename to prevent collisions
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    file.file.seek(0)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return f"/uploads/{unique_filename}"
