#!/usr/bin/env python3
"""
Test runner for AI Agents package.

Usage:
    python -m ai_agents.tests
    
Or run individual tests:
    python -m ai_agents.tests.test_tenant_admin_agent
    python -m ai_agents.tests.test_mcp_auth
"""

import sys
import asyncio
from pathlib import Path

# Ensure project root is in path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


async def run_all_tests():
    """Run all available tests."""
    print("="*80)
    print("AI AGENTS - TEST SUITE")
    print("="*80)
    print()
    
    # Import test modules
    from ai_agents.tests import test_mcp_auth, test_tenant_admin_agent
    
    # Run authentication test
    print("📋 Test 1/2: MCP Authentication")
    print("-"*80)
    auth_result = await test_mcp_auth.test_authenticated_call()
    print()
    
    # Run agent test
    print("📋 Test 2/2: Tenant Admin Agent")
    print("-"*80)
    agent_result = await test_tenant_admin_agent.test_agent()
    print()
    
    # Summary
    print("="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = 0
    failed = 0
    
    if auth_result:
        print("✅ Authentication Test: PASSED")
        passed += 1
    else:
        print("❌ Authentication Test: FAILED")
        failed += 1
    
    if agent_result:
        print("✅ Tenant Admin Agent Test: PASSED")
        passed += 1
    else:
        print("❌ Tenant Admin Agent Test: FAILED")
        failed += 1
    
    print()
    print(f"Total: {passed + failed} tests, {passed} passed, {failed} failed")
    print("="*80)
    
    return failed == 0


def main():
    """Main entry point."""
    try:
        result = asyncio.run(run_all_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
