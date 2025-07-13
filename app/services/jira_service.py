from jira import JIRA
import asyncio
import datetime
from typing import List, Optional
from app.config import settings
from app.utils.logger import logger
from app.models.schemas import JiraTicketCreate, JiraTicketResponse, RequirementExtracted

class JiraService:
     def __init__(self):
          self.jira = JIRA(
               server= settings.JIRA_SERVER,
               basic_auth=(settings.JIRA_EMAIL, settings.JIRA_API_TOKEN)
          )

     async def create_ticket(self, ticket_data: JiraTicketCreate) -> JiraTicketResponse:
          """
          Create a single Jira ticket
          """
          try:
               issue_dict = {
                    'project': {'key': ticket_data.project_key},
                    'summary': ticket_data.summary,
                    'description': ticket_data.description,
                    'issuetype': {'name': ticket_data.issue_type},
                    #  'priority': {'name': ticket_data.priority},
                    'labels': ticket_data.labels
               }

               if ticket_data.assignee:
                    issue_dict['assignee'] = {'name': ticket_data.assignee}

               new_issue = self.jira.create_issue(fields=issue_dict)
               return JiraTicketResponse(
                    key=new_issue.key,
                    url=f"{settings.JIRA_SERVER}/browse/{new_issue.key}",
                    summary=ticket_data.summary,
                    status=str(new_issue.fields.status),
                    created_at=datetime.datetime.now()
               )
          except Exception as e:
               logger.error(f"Failed to create Jira ticket: {str(e)}")
               raise Exception(f"Failed to create Jira ticket: {str(e)}")
     
     async def create_tickets_from_requirements(
          self,
          requirements: List[RequirementExtracted],
          project_key: str,
          assignee: Optional[str] = None
     ) -> List[JiraTicketResponse]:
          """
          Create multiple Jira tickets from extracted requirements
          """
          tickets = []
          for req in requirements:
               try:
                    issue_type = self._map_requirement_type(req.type)
                    description = self._build_description(req)

                    ticket_data = JiraTicketCreate(
                         project_key=project_key,
                         summary=req.summary,
                         description=description,
                         issue_type=issue_type,
                         # priority=req.priority.value
                         labels=req.labels + ['meeting_derived', 'auto-generated'],
                         assignee=assignee
                    )

                    ticket = await self.create_ticket(ticket_data)
                    tickets.append(ticket)
                    logger.info(f"Created Jira ticket: {ticket.key}")
               except Exception as e:
                    logger.error(f"Failed to create ticket for requirement: {str(e)}")
                    continue
          return tickets

     def _map_requirement_type(self, req_type: str) -> str:
          """
          Map internal requirement types to Jira issue types
          """
          mapping = {
               'feature': 'Story',
               'bug': 'Bug',
               'task': 'Task',
               'story': 'Story',
               'epic': 'Epic'
          }
          return mapping.get(req_type.lower(), 'Task')

     def _build_description(self, req: RequirementExtracted) -> str:
          """
          Build formatted description for Jira ticket
          """
          description = f"*Original Requirement:*\n{req.text}\n\n"
          description += f"*Description:*\n{req.description}\n\n"

          if req.acceptance_criteria:
               description += "*Acceptance Criteria:*\n"
               for i, criteria in enumerate(req.acceptance_criteria, 1):
                    description += f"{i}. {criteria}\n"
               description += "\n"

          if req.timestamp:
               description += f"*Mentioned at:* {req.timestamp}\n"

          description += f"*Confidence Score:* {req.confidence:.2f}\n"
          description += f"*Source:* Meeting transcription (auto-generated)"

          return description

     
     async def get_projects(self) -> List[dict]:
          """
          Get avialable Jira projects
          """
          try:
               projects = self.jira.projects()
               return [{'key': p.key, 'name': p.name} for p in projects]
          except Exception as e:
               logger.error(f"Failed to get the Jira projects: {str(e)}")
               return []