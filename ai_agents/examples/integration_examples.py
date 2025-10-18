#!/usr/bin/env python3
"""
Real-World Integration Example

This shows how to integrate the Project Management Client into a real application,
such as an AI agent, automation script, or web service.

Scenarios covered:
1. Simple script integration
2. Web service integration (FastAPI example)
3. AI agent integration
4. Background task integration
"""

import asyncio
from typing import List, Dict, Any
from project_management_client import ProjectManagementClient


# ============================================================================
# Scenario 1: Simple Script Integration
# ============================================================================

async def simple_script_example():
    """
    Example: Simple automation script that processes projects.
    Use case: Nightly job to check project status and send reports.
    """
    print("="*80)
    print("SCENARIO 1: Simple Script Integration")
    print("="*80 + "\n")
    
    async with ProjectManagementClient() as pm_client:
        tenant_id = "tenant-123"
        
        # Get all projects
        projects = await pm_client.list_projects(tenant_id)
        print(f"Found {len(projects.data)} projects")
        
        # Process each project
        for project in projects.data:
            project_id = project["id"]
            
            # Get project details
            details = await pm_client.get_project(project_id)
            
            # Check project status
            if details.data.get("status") == "in_progress":
                # Get risks for in-progress projects
                risks = await pm_client.list_project_risks(project_id)
                high_risks = [r for r in risks.data if r.get("severity") == "high"]
                
                if high_risks:
                    print(f"⚠️  Project {project['name']} has {len(high_risks)} high risks")
                    # Could send alert here


# ============================================================================
# Scenario 2: Web Service Integration (FastAPI)
# ============================================================================

async def fastapi_example():
    """
    Example: FastAPI endpoint that uses the client.
    Use case: REST API service wrapping project management.
    """
    print("\n" + "="*80)
    print("SCENARIO 2: Web Service Integration (FastAPI)")
    print("="*80 + "\n")
    
    # Note: This is a conceptual example showing the pattern
    # In real FastAPI, you'd use dependency injection
    
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import JSONResponse
    
    app = FastAPI()
    
    @app.get("/api/projects/{tenant_id}")
    async def get_projects(tenant_id: str):
        """FastAPI endpoint to list projects."""
        try:
            async with ProjectManagementClient() as pm_client:
                result = await pm_client.list_projects(tenant_id)
                return JSONResponse(content=result.data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/projects/{tenant_id}")
    async def create_project(tenant_id: str, project_data: dict):
        """FastAPI endpoint to create a project."""
        try:
            async with ProjectManagementClient() as pm_client:
                result = await pm_client.create_project(tenant_id, project_data)
                return JSONResponse(content=result.data, status_code=201)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    print("FastAPI endpoints defined:")
    print("  GET  /api/projects/{tenant_id}")
    print("  POST /api/projects/{tenant_id}")
    print("\nTo run: uvicorn integration_example:app --reload")


# ============================================================================
# Scenario 3: AI Agent Integration
# ============================================================================

class ProjectManagementAgent:
    """
    Example: AI agent that manages projects based on natural language commands.
    Use case: Chatbot or AI assistant for project management.
    """
    
    def __init__(self):
        self.client = None
    
    async def __aenter__(self):
        self.client = ProjectManagementClient()
        await self.client.__aenter__()
        return self
    
    async def __aexit__(self, *args):
        if self.client:
            await self.client.__aexit__(*args)
    
    async def process_command(self, command: str, context: Dict[str, Any]) -> str:
        """
        Process a natural language command.
        
        Args:
            command: Natural language command (e.g., "create a new project")
            context: Context including tenant_id, user, etc.
            
        Returns:
            Response message
        """
        command_lower = command.lower()
        
        # Simple command routing (in real AI, use LLM for intent classification)
        if "list projects" in command_lower or "show projects" in command_lower:
            return await self._handle_list_projects(context)
        
        elif "create project" in command_lower or "new project" in command_lower:
            return await self._handle_create_project(command, context)
        
        elif "add risk" in command_lower:
            return await self._handle_add_risk(command, context)
        
        else:
            return "I don't understand that command. Try: 'list projects' or 'create project'"
    
    async def _handle_list_projects(self, context: Dict[str, Any]) -> str:
        """Handle list projects command."""
        tenant_id = context.get("tenant_id")
        projects = await self.client.list_projects(tenant_id)
        
        project_list = "\n".join(
            f"- {p['name']} (Status: {p.get('status', 'unknown')})"
            for p in projects.data
        )
        
        return f"Here are your projects:\n{project_list}"
    
    async def _handle_create_project(self, command: str, context: Dict[str, Any]) -> str:
        """Handle create project command."""
        # In real implementation, use LLM to extract project details from command
        tenant_id = context.get("tenant_id")
        
        project_data = {
            "name": "AI-Generated Project",
            "description": f"Created from command: {command}"
        }
        
        result = await self.client.create_project(tenant_id, project_data)
        project_id = result.data.get("id")
        
        return f"✅ Created project '{project_data['name']}' (ID: {project_id})"
    
    async def _handle_add_risk(self, command: str, context: Dict[str, Any]) -> str:
        """Handle add risk command."""
        project_id = context.get("project_id")
        
        risk_data = {
            "title": "Risk from AI command",
            "description": command,
            "severity": "medium"
        }
        
        await self.client.create_project_risk(project_id, risk_data)
        return "✅ Risk added to project"


async def ai_agent_example():
    """Demonstrate the AI agent."""
    print("\n" + "="*80)
    print("SCENARIO 3: AI Agent Integration")
    print("="*80 + "\n")
    
    async with ProjectManagementAgent() as agent:
        context = {
            "tenant_id": "tenant-123",
            "project_id": "proj-456",
            "user": "AI Assistant"
        }
        
        # Simulate user commands
        commands = [
            "list projects",
            "create a new project for Q4 security audit",
            "add risk about data breaches"
        ]
        
        for cmd in commands:
            print(f"User: {cmd}")
            response = await agent.process_command(cmd, context)
            print(f"Agent: {response}\n")


# ============================================================================
# Scenario 4: Background Task Integration
# ============================================================================

class ProjectMonitor:
    """
    Example: Background service that monitors projects.
    Use case: Continuous monitoring and alerting system.
    """
    
    def __init__(self, tenant_id: str, check_interval: int = 300):
        """
        Args:
            tenant_id: Tenant to monitor
            check_interval: Seconds between checks (default: 5 minutes)
        """
        self.tenant_id = tenant_id
        self.check_interval = check_interval
        self.running = False
    
    async def start(self):
        """Start the monitoring loop."""
        self.running = True
        print(f"📊 Starting project monitor for tenant {self.tenant_id}")
        print(f"   Check interval: {self.check_interval} seconds\n")
        
        while self.running:
            await self._check_projects()
            await asyncio.sleep(self.check_interval)
    
    def stop(self):
        """Stop the monitoring loop."""
        self.running = False
    
    async def _check_projects(self):
        """Check all projects and alert on issues."""
        async with ProjectManagementClient() as pm_client:
            # Get all projects
            projects = await pm_client.list_projects(self.tenant_id)
            
            for project in projects.data:
                project_id = project["id"]
                
                # Check for high risks
                risks = await pm_client.list_project_risks(project_id)
                high_risks = [r for r in risks.data if r.get("severity") == "high"]
                
                if high_risks:
                    await self._alert(
                        f"Project {project['name']} has {len(high_risks)} high-severity risks"
                    )
                
                # Check for missing evidence
                evidence = await pm_client.list_project_evidence(project_id)
                controls = await pm_client.list_project_controls(project_id)
                
                if len(controls.data) > 0 and len(evidence.data) == 0:
                    await self._alert(
                        f"Project {project['name']} has controls but no evidence"
                    )
    
    async def _alert(self, message: str):
        """Send alert (implement actual alerting here)."""
        print(f"⚠️  ALERT: {message}")
        # Could send email, Slack message, etc.


async def background_task_example():
    """Demonstrate background monitoring."""
    print("\n" + "="*80)
    print("SCENARIO 4: Background Task Integration")
    print("="*80 + "\n")
    
    monitor = ProjectMonitor(
        tenant_id="tenant-123",
        check_interval=10  # Check every 10 seconds for demo
    )
    
    # In production, this would run indefinitely
    # For demo, we'll just do one check
    print("Running one monitoring cycle...\n")
    await monitor._check_projects()
    print("\nMonitoring cycle complete")


# ============================================================================
# Scenario 5: Batch Processing
# ============================================================================

async def batch_processing_example():
    """
    Example: Batch process multiple projects.
    Use case: Bulk updates, migrations, or reporting.
    """
    print("\n" + "="*80)
    print("SCENARIO 5: Batch Processing")
    print("="*80 + "\n")
    
    async with ProjectManagementClient() as pm_client:
        tenant_id = "tenant-123"
        
        # Get all projects
        projects = await pm_client.list_projects(tenant_id)
        
        # Batch operation: Add compliance comment to all projects
        for project in projects.data:
            project_id = project["id"]
            
            comment = {
                "text": f"Automated compliance check completed on {project['name']}"
            }
            
            try:
                await pm_client.add_project_comment(project_id, comment)
                print(f"✅ Added comment to project: {project['name']}")
            except Exception as e:
                print(f"❌ Failed to add comment to {project['name']}: {e}")


# ============================================================================
# Main - Run All Examples
# ============================================================================

async def main():
    """Run all integration examples."""
    print("\n🎯 PROJECT MANAGEMENT CLIENT - INTEGRATION EXAMPLES\n")
    
    examples = [
        ("Simple Script", simple_script_example),
        ("Web Service (FastAPI)", fastapi_example),
        ("AI Agent", ai_agent_example),
        ("Background Task", background_task_example),
        ("Batch Processing", batch_processing_example),
    ]
    
    for name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"\n❌ Error in {name} example: {e}")
        
        print("\n" + "-"*80 + "\n")
    
    print("✅ All integration examples complete!")
    print("\n💡 Choose the pattern that fits your use case:")
    print("   1. Simple Script - For automation and cron jobs")
    print("   2. Web Service - For REST APIs and microservices")
    print("   3. AI Agent - For chatbots and assistants")
    print("   4. Background Task - For monitoring and alerts")
    print("   5. Batch Processing - For bulk operations")


if __name__ == "__main__":
    asyncio.run(main())
