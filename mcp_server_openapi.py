import httpx
from fastmcp import FastMCP
import os
import time
import sys

# Configuration
OPENAPI_SPEC_URL = os.getenv(
    "OPENAPI_SPEC_URL", "http://localhost:8000/api/v1/swagger.json"
)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")


def wait_for_api():
    """Wait for the API server to be ready"""
    max_retries = 30
    retry_delay = 2

    for i in range(max_retries):
        try:
            response = httpx.get(OPENAPI_SPEC_URL, timeout=10)
            if response.status_code == 200:
                print(
                    f"✅ API server is ready! Fetched OpenAPI spec from {OPENAPI_SPEC_URL}"
                )
                return response.json()
        except Exception as e:
            print(
                f"⏳ Waiting for API server... attempt {i+1}/{max_retries} ({str(e)})"
            )
            time.sleep(retry_delay)

    print(
        f"❌ Failed to connect to API server at {OPENAPI_SPEC_URL} after {max_retries} attempts"
    )
    sys.exit(1)


def create_mcp_server():
    """Create and return the MCP server"""
    print("🚀 Starting Gapps OpenAPI MCP Server...")
    print(f"📡 OpenAPI Spec URL: {OPENAPI_SPEC_URL}")
    print(f"🔗 API Base URL: {API_BASE_URL}")

    # Wait for API and fetch OpenAPI spec
    openapi_spec = wait_for_api()

    # Configure authentication for the HTTP client
    auth_headers = {}

    # Get authentication token from environment (REQUIRED - provided by user)
    api_token = os.getenv("GAPPS_API_TOKEN")

    if not api_token:
        print("❌ ERROR: GAPPS_API_TOKEN environment variable is required")
        print("� The token should be obtained from the Gapps API and passed through the orchestrator state")
        sys.exit(1)

    # Use custom 'token' header (as expected by Gapps API)
    auth_headers["token"] = api_token
    print(f"🔑 Using token authentication (token: {api_token[:20]}...)")

    # CRITICAL: Set Content-Type header for JSON requests
    # Without this, POST/PUT/PATCH requests will fail with 415 UNSUPPORTED MEDIA TYPE
    auth_headers["Content-Type"] = "application/json"

    # Create authenticated HTTP client
    client = httpx.AsyncClient(
        base_url=API_BASE_URL,
        headers=auth_headers,
        timeout=30.0,  # 30 second timeout for all requests
    )

    # Create the MCP server from the OpenAPI spec
    print("🔨 Creating MCP server from OpenAPI specification...")
    return FastMCP.from_openapi(
        openapi_spec=openapi_spec, client=client, name="Gapps OpenAPI MCP"
    )


# Create the MCP server instance that FastMCP can find
try:
    # Only create server if we're not in daemon mode and API is available
    if os.getenv("MCP_DAEMON_MODE", "false").lower() != "true":
        mcp = create_mcp_server()
    else:
        mcp = None
except Exception as e:
    print(f"⚠️  Could not initialize MCP server at module level: {e}")
    print("🔄 Server will be created on-demand when main() is called")
    mcp = None


def main():
    global mcp

    # Create the MCP server if not already created
    if mcp is None:
        mcp = create_mcp_server()

    # Check if running in daemon mode (Docker container)
    daemon_mode = os.getenv("MCP_DAEMON_MODE", "false").lower() == "true"

    if daemon_mode:
        # In daemon mode, keep the server alive and ready for connections
        print("🐳 Running MCP server in daemon mode (Docker container)")
        print("🔄 Server is ready and waiting for MCP client connections...")
        print("💡 Connect via: docker exec -i mcp-openapi python mcp_server_openapi.py")
        print("⏹️  Press Ctrl+C to stop")

        try:
            # Keep the container alive - the actual MCP server runs when exec'd into
            while True:
                time.sleep(60)  # Sleep for 60 seconds at a time
                print(
                    "🟢 MCP OpenAPI server daemon alive - ready for client connections"
                )
        except KeyboardInterrupt:
            print("🛑 MCP OpenAPI server daemon stopped")
            sys.exit(0)
    else:
        # Normal mode: Run with STDIO transport for Claude Desktop compatibility
        print("🖥️  Running MCP server in interactive mode (local development)")
        print("✅ MCP server ready! Starting...")
        mcp.run()


if __name__ == "__main__":
    main()
