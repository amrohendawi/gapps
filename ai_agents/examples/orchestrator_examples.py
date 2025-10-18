"""
Examples demonstrating the GRC Task Orchestrator

Shows how to use the orchestrator for various GRC tasks.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ai_agents.orchestrator.grc_orchestrator import GRCTaskOrchestrator


async def example_compliance_setup():
    """Example: Set up a complete compliance program"""
    print("\n" + "="*80)
    print("EXAMPLE 1: Complete Compliance Program Setup")
    print("="*80 + "\n")
    
    orchestrator = GRCTaskOrchestrator()
    
    task = """
    Help me set up a complete SOC 2 compliance program:
    1. List the available compliance frameworks to choose from
    2. Create a new project called "SOC 2 Type II Audit 2024"
    3. Add key security controls for access management to the project
    4. Create a risk assessment for data protection
    5. Generate a status report for the project
    """
    
    print(f"📝 Task:\n{task}\n")
    print("🤖 Orchestrator working...\n")
    
    async for chunk in orchestrator.stream(task):
        for node_name, node_output in chunk.items():
            if "messages" in node_output:
                for msg in node_output["messages"]:
                    if hasattr(msg, 'content'):
                        print(f"\n[{node_name}] {msg.content}")
    
    print("\n✅ Complete!\n")


async def example_vendor_management():
    """Example: Vendor risk assessment"""
    print("\n" + "="*80)
    print("EXAMPLE 2: Vendor Risk Assessment")
    print("="*80 + "\n")
    
    orchestrator = GRCTaskOrchestrator()
    
    task = """
    I need to assess a new cloud service provider:
    1. List our current vendors to see if they're already in the system
    2. Show me the vendor questionnaire template for cloud providers
    3. Create a risk assessment for using cloud services
    4. Recommend which controls to verify during vendor assessment
    """
    
    print(f"📝 Task:\n{task}\n")
    
    result = await orchestrator.run(task)
    print(f"\n📊 Result:\n{result}\n")


async def example_project_lifecycle():
    """Example: Complete project lifecycle"""
    print("\n" + "="*80)
    print("EXAMPLE 3: Project Lifecycle Management")
    print("="*80 + "\n")
    
    orchestrator = GRCTaskOrchestrator()
    
    task = """
    Manage our HIPAA compliance project:
    1. Check if a HIPAA project already exists
    2. If not, create one for Q1 2024 HIPAA compliance
    3. Add privacy controls related to patient data protection
    4. Assign team members to key controls
    5. Track evidence collection progress
    """
    
    print(f"📝 Task:\n{task}\n")
    
    result = await orchestrator.run(task)
    print(f"\n📊 Result:\n{result}\n")


async def example_risk_management():
    """Example: Risk assessment and management"""
    print("\n" + "="*80)
    print("EXAMPLE 4: Risk Assessment & Management")
    print("="*80 + "\n")
    
    orchestrator = GRCTaskOrchestrator()
    
    task = """
    Help me with risk management for our web application:
    1. List current risks in the risk register
    2. Create a new risk for SQL injection vulnerabilities
    3. Add it to our Application Security project
    4. Recommend controls to mitigate this risk
    5. Generate a risk report
    """
    
    print(f"📝 Task:\n{task}\n")
    
    result = await orchestrator.run(task)
    print(f"\n📊 Result:\n{result}\n")


async def example_user_management():
    """Example: User and access management"""
    print("\n" + "="*80)
    print("EXAMPLE 5: User & Access Management")
    print("="*80 + "\n")
    
    orchestrator = GRCTaskOrchestrator()
    
    task = """
    Onboard a new compliance team member:
    1. Create a new user account for jane.smith@company.com
    2. Add her to our SOC 2 compliance project with Contributor access
    3. Generate an API token for her to access the system
    4. Show me all project members and their access levels
    """
    
    print(f"📝 Task:\n{task}\n")
    
    result = await orchestrator.run(task)
    print(f"\n📊 Result:\n{result}\n")


async def example_policy_management():
    """Example: Policy lifecycle management"""
    print("\n" + "="*80)
    print("EXAMPLE 6: Policy Management")
    print("="*80 + "\n")
    
    orchestrator = GRCTaskOrchestrator()
    
    task = """
    Update our access control policies:
    1. List all current policies related to access control
    2. Create a new version of the Access Control Policy
    3. Link it to our SOC 2 compliance project
    4. Map it to relevant controls in the project
    5. Generate a policy compliance report
    """
    
    print(f"📝 Task:\n{task}\n")
    
    result = await orchestrator.run(task)
    print(f"\n📊 Result:\n{result}\n")


async def example_audit_preparation():
    """Example: Audit preparation"""
    print("\n" + "="*80)
    print("EXAMPLE 7: Audit Preparation")
    print("="*80 + "\n")
    
    orchestrator = GRCTaskOrchestrator()
    
    task = """
    Prepare for our upcoming SOC 2 audit:
    1. Generate a complete project status report
    2. List all controls and their implementation status
    3. Identify controls with missing evidence
    4. Show all project risks and their mitigation status
    5. Create a summary for the audit committee
    """
    
    print(f"📝 Task:\n{task}\n")
    
    result = await orchestrator.run(task)
    print(f"\n📊 Result:\n{result}\n")


async def example_framework_comparison():
    """Example: Framework comparison and mapping"""
    print("\n" + "="*80)
    print("EXAMPLE 8: Framework Comparison")
    print("="*80 + "\n")
    
    orchestrator = GRCTaskOrchestrator()
    
    task = """
    We need to choose between SOC 2 and ISO 27001:
    1. List both frameworks and their key requirements
    2. Show overlapping controls between them
    3. Compare the effort needed for each
    4. Recommend which framework to pursue first
    """
    
    print(f"📝 Task:\n{task}\n")
    
    result = await orchestrator.run(task)
    print(f"\n📊 Result:\n{result}\n")


def print_menu():
    """Print the examples menu"""
    print("\n" + "="*80)
    print("GRC TASK ORCHESTRATOR - EXAMPLES")
    print("="*80)
    print("\nChoose an example to run:\n")
    print("  1. Complete Compliance Program Setup")
    print("  2. Vendor Risk Assessment")
    print("  3. Project Lifecycle Management")
    print("  4. Risk Assessment & Management")
    print("  5. User & Access Management")
    print("  6. Policy Management")
    print("  7. Audit Preparation")
    print("  8. Framework Comparison")
    print("  0. Exit\n")


async def main():
    """Main function to run examples"""
    
    # Check environment
    if not os.getenv("GAPPS_API_TOKEN"):
        print("\n⚠️  Warning: No authentication token found")
        print("Get token via: curl -X POST http://localhost:8000/login -H 'Content-Type: application/json' -d '{\"email\":\"admin@example.com\",\"password\":\"your_password\"}'")
        print("Then set: export GAPPS_API_TOKEN='your-token-here'\n")
    
    examples = {
        "1": ("Compliance Setup", example_compliance_setup),
        "2": ("Vendor Assessment", example_vendor_management),
        "3": ("Project Lifecycle", example_project_lifecycle),
        "4": ("Risk Management", example_risk_management),
        "5": ("User Management", example_user_management),
        "6": ("Policy Management", example_policy_management),
        "7": ("Audit Preparation", example_audit_preparation),
        "8": ("Framework Comparison", example_framework_comparison),
    }
    
    while True:
        print_menu()
        choice = input("Enter your choice (0-8): ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye!\n")
            break
        
        if choice in examples:
            name, func = examples[choice]
            try:
                await func()
                input("\nPress Enter to continue...")
            except KeyboardInterrupt:
                print("\n\n⚠️  Example interrupted by user\n")
                input("Press Enter to continue...")
            except Exception as e:
                print(f"\n❌ Error running example: {e}\n")
                import traceback
                traceback.print_exc()
                input("Press Enter to continue...")
        else:
            print("\n❌ Invalid choice. Please try again.\n")
            input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
