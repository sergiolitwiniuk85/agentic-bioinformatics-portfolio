"""Simulated HPC + dataset catalog exposed as an MCP server (stdio transport).

Demonstrates connecting the agent to external resources (HPC job submission and an
internal dataset catalog) via the Model Context Protocol — the same pattern used to
wire a real cluster or database to an LLM agent.
"""

from mcp.server.mcpserver import MCPServer

mcp = MCPServer("hpc-catalog")

DATASETS = [
    {"id": "pbmc3k", "name": "PBMC 3k", "kind": "single-cell", "size": "5 MB"},
    {"id": "visium_sge", "name": "Visium lymph node", "kind": "spatial", "size": "25 MB"},
    {"id": "xenium_demo", "name": "Xenium breast cancer", "kind": "spatial (subcellular)", "size": "2 GB", "status": "planned"},
]

_jobs: dict[str, str] = {}


@mcp.tool()
def submit_job(job_name: str, script: str, partition: str = "cpu") -> str:
    """Submit an analysis job to the (simulated) HPC cluster."""
    job_id = f"job-{len(_jobs) + 1:04d}"
    _jobs[job_id] = "QUEUED"
    return f"Submitted '{job_name}' (script={script}) to partition '{partition}' -> {job_id}"


@mcp.tool()
def job_status(job_id: str) -> str:
    """Return the (simulated) status of a previously submitted job."""
    return f"{job_id}: {_jobs.get(job_id, 'UNKNOWN')} (simulated)"


@mcp.tool()
def list_datasets() -> str:
    """List datasets available in the internal catalog."""
    return "\n".join(f"{d['id']} — {d['name']} ({d['kind']}, {d['size']})" for d in DATASETS)


if __name__ == "__main__":
    mcp.run()
