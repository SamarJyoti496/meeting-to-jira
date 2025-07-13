import os
import aiofiles
import uuid
from fastapi import UploadFile
from app.config  import settings
from app.utils.logger import logger


class FileService:
     def __init__(self):
          self.upload_dir = settings.UPLOAD_DIR
          os.makedirs(self.upload_dir, exist_ok=True)

     async def save_uploaded_file(self, file: UploadFile):
          """
          Save uploaded file and return (file_path, unique_filename)
          """
          try:
               # Generate unique filename
               file_ext = os.path.splitext(file.filename)[1].lower()
               unique_filename = f"{uuid.uuid4()}{file_ext}"
               file_path = os.path.join(self.upload_dir, unique_filename)

               # Save file
               async with aiofiles.open(file_path, 'wb') as f:
                    content = await file.read()
                    await f.write(content)

               logger.info(f"File saved: {file_path}")
               return file_path, unique_filename
          except Exception as e:
               logger.error(f"Failed to save file: {str(e)}")
               raise Exception(f"Failed to save file: {str(e)}")
     
     async def validate_file(self, file: UploadFile) -> bool:
          """
          Validate the uploaded file
          """
          file_ext = os.path.splitext(file.filename)[1].lower().replace(".","")
          if file_ext not in settings.SUPPORTED_FORMATS:
               return ValueError(f"Unsupported file format :  {file_ext}")
          
          if file.size > settings.MAX_FILE_SIZE:
               return ValueError(f"File too large: {file.size} bytes")
          
          return True
     
     async def delete_file(self, file_path: str) -> bool:
          """
          Delete file from storage
          """
          try:
               if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"File deleted: {file_path}")
                    return True
               return False
          except Exception as e:
               logger.error(f"Failed to delete file: {str(e)}")
               return False
     
     async def get_file_info(self, file_path: str) -> dict:
          """
          Get file information
          """
          try:
               stat = os.stat(file_path)
               return {
                    "size" : stat.st_size,
                    "created": stat.st_ctime,
                    "modified": stat.st_mtime,
                    "exits": True
               }
          except Exception:
               return {'exits' : False}




