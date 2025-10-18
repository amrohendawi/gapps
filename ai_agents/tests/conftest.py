#!/usr/bin/env python3
"""
Test configuration and fixtures for AI Agents tests.

This file ensures that tests can properly import modules from the ai_agents package
and sets up any necessary environment or path configurations.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path so we can import ai_agents
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set defaults for environment variables (if not already set)
# These are used by the tests to authenticate with the Gapps API

# NOTE: Tests now require GAPPS_API_TOKEN to be set
# Get token via: curl -X POST http://localhost:8000/login -H "Content-Type: application/json" -d '{"email":"admin@example.com","password":"admin1234567"}'
if not os.getenv("GAPPS_API_TOKEN"):
    print("⚠️  Warning: GAPPS_API_TOKEN not set. Tests may fail.")
    print("   Get token via: curl -X POST http://localhost:8000/login -H 'Content-Type: application/json' -d '{\"email\":\"admin@example.com\",\"password\":\"admin1234567\"}'")


# Default to local LLM provider for tests
if not os.getenv("AGENT_LLM_PROVIDER"):
    os.environ["AGENT_LLM_PROVIDER"] = "local"
