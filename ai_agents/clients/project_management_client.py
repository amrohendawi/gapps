"""
MCP Client for Project Management

This client handles all project-related operations including:
- Project CRUD operations
- Project controls and sub-controls
- Project evidence management
- Project members and access control
- Project policies and versions
- Project risks and comments
- Project tags and history
- Project reports and findings
"""

from ai_agents.base.base_client import BaseClient


class ProjectManagementClient(BaseClient):
    """
    MCP Client for managing projects and all associated resources.
    
    This client provides access to:
    - Projects: Create, read, update, delete projects
    - Controls: Manage project controls, sub-controls, applicability
    - Evidence: Upload and manage evidence for controls
    - Members: Add/remove project members, manage access levels
    - Policies: Associate policies with projects, manage versions
    - Risks: Track and manage project risks
    - Comments: Add comments to projects, controls, sub-controls
    - Tags: Organize projects with tags
    - Reports: Generate project reports
    - History: Track project changes
    - Findings: Review project findings
    
    Filters from 166 total tools to ~69 project-related tools.
    """
    
    # Tool patterns to match project-related endpoints
    TOOL_PATTERNS = [
        "project",           # Matches /projects/* and /project-controls/*
        "project-control",   # Matches project control operations
        "project_control",   # Alternative pattern for project controls
    ]
    
    def get_client_name(self) -> str:
        """Return the name of this client"""
        return "Project Management"
