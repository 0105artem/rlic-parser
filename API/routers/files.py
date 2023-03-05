import os

from fastapi import status, HTTPException, APIRouter
from fastapi.responses import FileResponse

router = APIRouter(
    prefix="/files",
    tags=["Files"]
)


@router.get("/csv/{file_name}")
async def download_csv_file(file_name: str):
    csv_files = os.listdir("./files/csv")
    if file_name not in csv_files:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"CSV file with name {file_name} was not found.")
    return FileResponse(f"./files/csv/{file_name}")
