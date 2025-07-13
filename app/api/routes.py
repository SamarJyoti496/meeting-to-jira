from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.models.database import ProcessingJob, Meeting, Requirement, JiraTicket, get_db
from app.services.jira_service import JiraService
from app.utils.logger import logger
from app.services.file_service import FileService
from app.services.transcription import TranscriptionService
from app.services.extraction import RequirementExtractionService
from app.models.schemas import RequirementExtracted, RequirementType, Priority

router = APIRouter()

file_service = FileService()
transcription_service = TranscriptionService()
extraction_service = RequirementExtractionService()
jira_service = JiraService()

@router.post("/upload", response_model=dict)
async def upload_meeting_file(
     background_tasks: BackgroundTasks,
     file: UploadFile = File(...),
     project_key: str = "PROJ",
     assignee: Optional[str] = None,
     db: Session = Depends(get_db)):
     """
     Upload meeting recording and start processing
     """
     try:
          await file_service.validate_file(file)

          file_path, unique_filename = await file_service.save_uploaded_file(file)

          meeting = Meeting(
               filename=unique_filename,
               original_filename=file.filename,
               file_path=file_path
          )

          db.add(meeting)
          db.commit()

          background_tasks.add_task(
               process_meeting_async,
               meeting.id,
               file_path,
               project_key,
               assignee,
               db
          )

          return {
               "message": "File Upload Successfully",
               "meeting_id": meeting.id,
               "status" : "processing"
          }
     except Exception as e:
          logger.error(f"Upload failed: {str(e)}")
          raise HTTPException(status_code=400, detail=str(e))


@router.get('/meetings/{meeting_id}/status')
async def get_meeting_status(meeting_id: str, db: Session=Depends(get_db)):
     try:
          meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
          if not meeting:
               raise HTTPException(status_code=404, detail="Meeting not found")
          
          job = db.query(ProcessingJob).filter(ProcessingJob.meeting_id == meeting_id).first()

          return {
               "meeting_id" : meeting_id,
               "file_name" : meeting.original_filename,
               "status" : job.status if job else "pending",
               "progress" : job.progress if job else 0,
               "message" : job.message,
               "processed" : meeting.processed,
               "created_at" : meeting.created_at
          }
     except HTTPException:
          raise
     except Exception as e:
          logger.error(f"status check failed: {str(e)}")
          raise HTTPException(status_code=500, detail="Failed to get status")

@router.get("meetings/{meeting_id}/requirements")
async def get_meeeting_requirements(meeting_id: str, db: Session=Depends(get_db)):
     """Get eextracted requirements for a meeting
     """
     try:
          requirements = db.query(Meeting).filter(Requirement.meeting_id == meeting_id).all()

          if not requirements:
               raise HTTPException(status_code=404, detail="No requirements found")
          
          return {
               "meeting_id": meeting_id,
               "requirements": [
                    {
                         "id": req.id,
                         "summary": req.summary,
                         "description": req.description,
                         "type": req.requirement_type,
                         "priority": req.priority,
                         "labels": req.labels,
                         "acceptance_criteria": req.acceptance_criteria,
                         "confidence": req.confidence,
                         "jira_ticket_key": req.jira_ticket_key,
                         "created_at": req.created_at
                    }
                    for req in requirements
               ]
          }
     except HTTPException:
          raise
     except Exception as e:
          logger.error(f"Requirements fetch failed: {str(e)}")
          raise HTTPException(status_code=500, detail="Failed to get requirements")

@router.get("/meetings/{meeting_id}/tickets")
async def get_meeting_tickets(meeting_id: str, db: Session = Depends(get_db)):
     """
     Get Jira tickets created for a meeting
     """
     try:
          requirements = db.query(Requirement).filter(
               Requirement.meeting_id == meeting_id
          ).all()

          if not requirements:
               raise HTTPException(status_code=404, detail="No requirements found")
          
          requirement_ids = [req.id for req in requirements]

          tickets = db.query(JiraTicket).filter(
               JiraTicket.requirement_id.in_(requirement_ids)
          ).all()

          return {
               "meeting_id": meeting_id,
               "tickets": [
                    {
                         "id": ticket.id,
                         "ticket_key": ticket.ticket_key,
                         "url": ticket.url,
                         "summary": ticket.summary,
                         "status": ticket.status,
                         "created_at": ticket.created_at
                    }
                    for ticket in tickets
               ]
          }
     except HTTPException:
          raise
     except Exception as e:
          logger.error(f"Tickets fetch failed: {str(e)}")
          raise HTTPException(status_code=500, detail="Failed to get tickets")

@router.get("/projects")
async def get_jira_projects():
     """
     Get Avialable Projects
     """
     try:
          projects = await jira_service.get_projects()
          return {"projects": projects}
     except Exception as e:
          logger.error(f"Project fetch failed: {str(e)}")
          raise HTTPException(status_code=500,detail="Failed tp get projects")

@router.get("/requiremets/{requirement_id}/create-ticket")
async def create_single_ticket(
     requirement_id: str,
     project_key: str,
     assignee: Optional[str] = None,
     db: Session = Depends(get_db)
):
     try:
          requirement = db.query(Requirement).filter(
               Requirement.id == requirement_id
          ).first()

          if not requirement:
               raise HTTPException(status_code=404, detail="Requirement not found")
          
          if requirement.jira_ticket_key:
               raise HTTPException(
                    status_code=404,
                    detail="Ticket already exists for this requirement"
               )
          
          req_obj = RequirementExtracted(
               text=requirement.text,
               summary=requirement.summary,
               description=requirement.description,
               type=RequirementType(requirement.requirement_type),
               priority=Priority(requirement.priority),
               labels=requirement.labels or [],
               acceptance_criteria=requirement.acceptance_criteria or [],
               confidence=requirement.confidence,
               timestamp=requirement.timestamp
          )

          tickets = await jira_service.create_tickets_from_requirements(
               [req_obj], project_key, assignee
          )

          if tickets:
               ticket = tickets[0]

               requirement.jira_ticket_key = ticket.key

               jira_ticket = JiraTicket(
                    requirement_id=requirement_id,
                    ticket_key=ticket.key,
                    url=ticket.url,
                    summary=ticket.summary,
                    status=ticket.status
               )
               db.add(jira_ticket)
               db.commit()

               return {
                    "message": "Ticket created successfully",
                    "ticket": {
                         "key": ticket.key,
                         "url": ticket.url,
                         "summary": ticket.summary,
                         "status": ticket.status
                    }
               }
          
          raise HTTPException(status_code=500, detail="failed to create ticket")
     
     except HTTPException:
          raise
     except Exception as e:
          logger.error(f"Ticket creation failed: {str(e)}")
          raise HTTPException(status_code=500, detail="Failed to create ticket")

@router.get('/meetings')
async def get_meetings(
     limit: int = 10,
     offset: int = 0,
     db: Session = Depends(get_db)
):
     try:
          meetings = db.query(Meeting).order_by(
               Meeting.created_at.desc()
          ).offset(offset).limit(limit).all()

          return {
               "meetings": [
                    {
                         "id": meeting.id,
                         "filename": meeting.original_filename,
                         "duration": meeting.duration,
                         "processed": meeting.processed,
                         "created_at": meeting.created_at
                    }
                    for meeting in meetings
               ]
          }

     except Exception as e:
          logger.error(f"Meetings fetch failed: {str(e)}")
          raise HTTPException(status_code=500, detail="Failed to get meetings")




async def process_meeting_async(
     meeting_id: str,
     file_path: str,
     project_key: str,
     assignee: Optional[str],
     db
):
     """
     Background task to process meeting recording
     """
     try:
          job = ProcessingJob(
               meeting_id = meeting_id,
               status="processing",
               progress=0,
               message="Starting transcription...."
          )
          db.add(job)
          db.commit()

          logger.info(f"Starting transcription for meeting {meeting_id}")
          transcription_text, confidence = await transcription_service.transcribe_audio(file_path)

          meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
          meeting.transcription_text = transcription_text
          meeting.transcription_confidence = confidence

          job.progress = 30
          job.message = "Transcription complete, Extracting requirements ...."
          db.commit()

          logger.info(f"Extracting requirements for meeting {meeting_id}")
          requirements = await extraction_service.extract_requirements(transcription_text)

          for req in requirements:
               requirement = Requirement(
                    meeting_id=meeting_id,
                    text=req.text,
                    summary=req.summary,
                    description=req.description,
                    requirement_type=req.type.value,
                    # priority=req.priority.value,
                    labels=req.labels,
                    acceptance_criteria=req.acceptance_criteria,
                    timestamp = req.timestamp
               )

               db.add(requirement)
          
          job.progress = 60
          job.message = "Requirements extracted, Creating Jira Tickets ....."
          db.commit()

          logger.info(f"Creating Jira tickets for meeting {meeting_id}")

          tickets = await jira_service.create_tickets_from_requirements(requirements, project_key, assignee)

          for i, ticket in enumerate(tickets):
               if i < len(requirements):
                    req_in_db = db.query(Requirement).filter(
                         Requirement.meeting_id == meeting_id
                    ).offset(i).first()

                    req_in_db.jira_ticket_key = ticket.key

                    jira_ticket = JiraTicket(
                         requirement_id=req_in_db.id,
                         ticket_key=ticket.key,
                         url =  ticket.url,
                         summary = ticket.summary,
                         status = ticket.status
                    )

                    db.add(jira_ticket)

          meeting.processed = True
          job.status = 'completed'
          job.progress = 100
          job.message = f"Processing complete. Created {len(tickets)} tickets."
          job.result = {
               "transcription_confidence" : confidence,
               "requirement_count" : len(requirements),
               "ticket_count" : len(tickets)
          }
          db.commit()
          logger.info(f"Meeting {meeting_id} processed successfully")
     except Exception as e:
          logger.error(f"Meeting processing failed: {str(e)}")
          job.status = "failed"
          job.message = f"Processing failed: {str(e)}"
          db.commit()
          raise e
     finally:
          db.close()