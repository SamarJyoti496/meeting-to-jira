from faster_whisper import WhisperModel
from fastapi.concurrency import run_in_threadpool
import math
from typing import Tuple
from app.utils.logger import logger
from pprint import pprint



class TranscriptionService:
     def __init__(self):
          """
          Initializes the self-hosted transcription pipeline using faster-whisper.
          """

          model_size = "small"
          self.device = "cpu"
          self.compute_type = "int8"
          try:
               self.model = WhisperModel(model_size, device=self.device, compute_type=self.compute_type)
               logger.info("fatser-whisper model loaded successfully")
          except Exception as e:
               logger.error(f"Failed to load faster-whisper model: {e}")
               self.model = None
               raise RuntimeError("Could not initialize the transcription pipeline.")

     async def transcribe_audio(self, file_path: str) -> Tuple[str, float]:
          if not self.model:
               raise Exception("Transcription pipeline is not available")
          
          logger.info(f"Starting faster-whisper transcription for: {file_path}")

          try:
               segments, info = await run_in_threadpool(
                    self.model.transcribe, file_path, beam_size=5
               )

               transcription_text = "".join(segment.text for segment in segments)
               
               # print(segments)
               confidence = math.exp(info.all_language_probs[0][1])
               return transcription_text.strip(), confidence
          except Exception as e:
               logger.error(f"faster-whisper transcription failed: {str(e)}")
               raise Exception(f"faster-whisper transcription failed: {str(e)}")