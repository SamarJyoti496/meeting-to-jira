from google import genai
from google.genai import types
import json
import re
from typing import List
from app.config import settings
from app.models.schemas import RequirementExtracted, RequirementType, Priority
from app.utils.logger import logger


class RequirementExtractionService:
     def __init__(self):
          self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

     async def extract_requirements(self, transcription: str) -> List[RequirementExtracted]:
          """
          Extract the requirements from meeting transcription
          """
          try:
               prompt = self._build_extraction_prompt(transcription)
               response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                         temperature=0.2,
                         response_mime_type="application/json",
                    )
               )

               content = response.text
               requirement_data = json.loads(content)

               requirements = []
               for req_data in requirement_data.get("requirements", []):
                    try:
                         requirement = RequirementExtracted(
                              text=req_data.get('text', 'N/A'),
                              summary=req_data.get('summary', 'N/A'),
                              description=req_data.get('description', ''),
                              type=RequirementType(req_data.get('type', 'task')),
                              priority=Priority(req_data.get('priority', 'Medium')),
                              labels=req_data.get('labels', []),
                              acceptance_criteria=req_data.get('acceptance_criteria', []),
                              confidence=req_data.get('confidence', 0.8),
                              timestamp=req_data.get('timestamp')
                         )
                         requirements.append(requirement)
                    except Exception as e:
                         logger.warning(f"Failed to parse single requirement: {req_data}. Error: {e}")
                    
               return requirements
          except Exception as e:
               logger.error(f"Requirement extraction with Gemini failed: {str(e)}")
               return []
     
     def _build_extraction_prompt(self, transcription: str) -> str:
          cleaned_text = self._clean_transcripton(transcription)
          return f"""
You are an expert business analyst AI specialized in extracting software requirements from meeting transcriptions. 
Your task is to analyze the following transcription and identify all actionable software requirements.

Follow these instructions carefully:
1. Identify all explicit and implicit requirements. Look for phrases like "we need to", "the system should", "let's add", "it would be great if".
2. For each requirement, create a clear, concise summary that can be used as a Jira ticket title.
3. Provide a detailed description suitable for a developer.
4. Categorize the requirement type as one of: "feature", "bug", "task", "story", or "epic". Default to "task" if unsure.
5. Determine the priority as one of: "Low", "Medium", "High", or "Critical". Default to "Medium".
6. Extract any relevant labels.
7. List any acceptance criteria mentioned.
8. Provide a confidence score from 0.0 to 1.0 on how certain you are that this is an actionable requirement.

Return your response as a single, valid JSON object. Do not include any introductory text or markdown formatting. The JSON object must have a single key "requirements" which is a list of requirement objects.

Here is the JSON structure for each requirement:
{{
  "text": "The original text from the transcript that implies the requirement.",
  "summary": "A clear, concise title for the requirement.",
  "description": "A detailed description for developers, including context.",
  "type": "feature|bug|task|story|epic",
  "priority": "Low|Medium|High|Critical",
  "labels": ["label1", "label2"],
  "acceptance_criteria": ["criteria1", "criteria2"],
  "confidence": 0.9,
  "timestamp": "The approximate time mentioned in the transcript (e.g., [00:15:32]) if available."
}}

Here is the meeting transcription to analyze:

--- TRANSCRIPT ---
{cleaned_text}
--- END TRANSCRIPT ---

Now, provide the JSON object.
"""

     def _clean_transcripton(self, text: str) -> str:
          text = re.sub(r'\s+', ' ', text)

          text = re.sub('\b(um|uh|er|ah|like|you know)\b', '', text, flags=re.IGNORECASE)

          text = re.sub('r\b(gonna|wanna|gotta)\b', lambda m:{
               'gonna': 'going to',
               'wanna': 'want to',
               'gotta': 'got to'
          } [m.group().lower()], text, flags=re.IGNORECASE)

          return text.strip()