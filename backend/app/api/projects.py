import io
import zipfile
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

# Replace with your actual project workspace/graph store import
# from app.core.engine import workspace_store 

router = APIRouter()

@router.get("/api/projects/{project_id}/download")
async def download_workspace_zip(project_id: str):
    # Retrieve files dictionary for the given project_id (e.g., {"string_utils.py": "code...", ...})
    # Adjust this line to match how your engine accesses workspace files
    workspace_files = workspace_store.get(project_id, {})

    if not workspace_files:
        raise HTTPException(status_code=404, detail="No generated files found for this project.")

    # Create an in-memory zip archive
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in workspace_files.items():
            zip_file.writestr(filename, content)

    zip_buffer.seek(0)

    filename = f"project_{project_id[:8]}.zip"
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )