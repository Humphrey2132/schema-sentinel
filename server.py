from mcp.server.fastmcp import FastMCP
import httpx

# Initialize FastMCP server instance
mcp = FastMCP("SchemaSentinel")

@mcp.tool()
async def check_endpoint_drift(openapi_url: str, target_path: str, http_method: str) -> str:
    """
    Fetches an OpenAPI JSON specification from a URL and checks if a specific endpoint path 
    and HTTP method exist, and whether it is marked as deprecated.
    """
    method_clean = http_method.lower().strip()
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(openapi_url)
            response.raise_for_status()
            spec = response.json()
        except Exception as e:
            return f"Error fetching OpenAPI spec: {str(e)}"
            
    paths = spec.get("paths", {})
    if target_path not in paths:
        return f"Drift Detected: Path '{target_path}' does not exist in the OpenAPI spec."
        
    path_item = paths[target_path]
    if method_clean not in path_item:
        return f"Drift Detected: Method '{http_method.upper()}' does not exist for path '{target_path}'."
        
    operation = path_item[method_clean]
    is_deprecated = operation.get("deprecated", False)
    
    if is_deprecated:
        return f"Warning: Endpoint '{http_method.upper()} {target_path}' exists but is marked as DEPRECATED."
        
    return f"Success: Endpoint '{http_method.upper()} {target_path}' is active and matching the spec."

if __name__ == "__main__":
    mcp.run()