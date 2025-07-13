from openai import OpenAI
import os
import tempfile
import ffmpeg
from typing import Tuple
from app.config import settings
from app.utils.logger import logger


class TranscriptionService:
     def __init__(self):
          self.client  = OpenAI(api_key=settings.OPENAI_API_KEY)
     
     async def transcribe_audio(self, file_path: str) -> Tuple[str, float]:
          """
          Transcribe audio file using OpenAI whisper
          Returns: (transcription_text, confidence_score)
          """
          try:
               processed_path = await self._preprocess_audio(file_path)
               print(processed_path)

               with open(processed_path, 'rb') as audio_file:
                    transcript = await self.client.audio.transcriptions.create(
                         model="whisper-1",
                         file=audio_file,
                         response_format="verbose_json"
                    )
               
               confidence =  self._calculate_confidence(transcript.get('segments', []))

               if processed_path != file_path:
                    os.remove(processed_path)
               
               return transcript['text'], confidence
          except Exception as e:
               logger.error(f"Audio preprocessing failed: {str(e)}")
               return file_path  # Return original if preprocessing fails

     async def _preprocess_audio(self, file_path: str) -> str:
          """
          Preprocess audio file for optimal transcription
          """
          try: 
               file_ext = os.path.splitext(file_path)[1].lower()
               if file_ext in ['.mp3', '.wav', '.m4a']:
                    return file_path
               
               with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                    output_path = temp_file.name
               
               (
                    ffmpeg
                    .input(file_path)
                    .output(
                         output_path,
                         acodec='mp3',
                         ar=16000,
                         ac=1,
                         ab='64k'
                    )
                    .overwrite_output()
                    .run(quiet=True)
               )

               return output_path
          except Exception as e:
               logger.error(f"Audio preprocessing failed: {str(e)}")
               return file_path  # Return original if preprocessing fails

     async def _calculate_confidence(self, segments: list) -> float:
          """
          Calculate average confidence score from transcription segments
          """
          if not segments:
               return 0.8
          
          total_confidence = 0.0
          for segment in segments:
               if 'confidence' in segment:
                    total_confidence += segment['confidence']
               else:
                    text_length = len(segment.get('text', ''))
                    total_confidence += min(0.9, 0.6 + (text_length / 100))
          return total_confidence / len(segments)