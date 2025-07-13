from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class RequirementType(str, Enum):
     FEATURE = "feature"
     BUG = "bug"
     TASK = "task"
     STORY = "story"
     EPIC = "epic"

class Priority(str, Enum):
     LOW = "Low"
     MEDIUM = "Medium"
     HIGH = "High"
     CRITICAL = "Critical"

class TranscriptionCreate(BaseModel):
     filename: str
     duration: Optional[float] = None

class TranscriptionReponse(BaseModel):
     id: str
     filename: str
     text: str
     duration: float
     confidence: float
     created_at: datetime

class RequirementExtracted(BaseModel):
     text: str
     summary: str
     description: str
     type: RequirementType
     priority: Optional[str] = None 
     labels: List[str]
     acceptance_criteria: List[str]
     confidence: float
     timestamp: Optional[str] = None

class JiraTicketCreate(BaseModel):
     project_key: str
     summary: str
     description: str
     issue_type: str
     priority: Optional[str] = None 
     labels: List[str] = []
     assignee: Optional[str] = None

class JiraTicketResponse(BaseModel):
     key: str
     url: str
     summary: str
     status: str
     created_at: datetime

class ProcessingJob(BaseModel):
     id: str
     status: str
     progress: int
     message: str
     result: Optional[dict] = None
     created_at: datetime
