"""
API Routes for Directories
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services import DirectoryService
from ..schemas import (
    DirectoryCreate, DirectoryUpdate, DirectoryResponse,
    DirectoryBulkImport, DirectoryStatus
)
from ..automation import SubmissionExecutor

router = APIRouter(prefix="/directories", tags=["Directories"])


@router.post("/", response_model=DirectoryResponse)
async def create_directory(
    directory_data: DirectoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new directory"""
    service = DirectoryService(db)
    
    # Check for duplicate URL
    existing = await service.get_by_url(directory_data.url)
    if existing:
        raise HTTPException(status_code=400, detail="Directory with this URL already exists")
    
    directory = await service.create(directory_data)
    return directory


@router.post("/bulk", response_model=List[DirectoryResponse])
async def bulk_create_directories(
    data: DirectoryBulkImport,
    db: AsyncSession = Depends(get_db)
):
    """Bulk create multiple directories"""
    service = DirectoryService(db)
    directories = await service.bulk_create(data.directories)
    return directories


@router.get("/", response_model=List[DirectoryResponse])
async def list_directories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[DirectoryStatus] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all directories"""
    service = DirectoryService(db)
    directories = await service.get_all(
        skip=skip, 
        limit=limit, 
        status=status,
        category=category
    )
    return directories


@router.get("/categories", response_model=List[str])
async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    """Get all unique directory categories"""
    service = DirectoryService(db)
    categories = await service.get_categories()
    return categories


@router.get("/active", response_model=List[DirectoryResponse])
async def get_active_directories(
    db: AsyncSession = Depends(get_db)
):
    """Get all active directories for submissions"""
    service = DirectoryService(db)
    directories = await service.get_active_directories()
    return directories


@router.get("/{directory_id}", response_model=DirectoryResponse)
async def get_directory(
    directory_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a directory by ID"""
    service = DirectoryService(db)
    directory = await service.get_by_id(directory_id)
    
    if not directory:
        raise HTTPException(status_code=404, detail="Directory not found")
    
    return directory


@router.put("/{directory_id}", response_model=DirectoryResponse)
async def update_directory(
    directory_id: int,
    directory_data: DirectoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a directory"""
    service = DirectoryService(db)
    directory = await service.update(directory_id, directory_data)
    
    if not directory:
        raise HTTPException(status_code=404, detail="Directory not found")
    
    return directory


@router.delete("/{directory_id}")
async def delete_directory(
    directory_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a directory"""
    service = DirectoryService(db)
    success = await service.delete(directory_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Directory not found")
    
    return {"message": "Directory deleted successfully"}


@router.post("/{directory_id}/analyze")
async def analyze_directory(
    directory_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Analyze a directory to detect its form schema"""
    service = DirectoryService(db)
    directory = await service.get_by_id(directory_id)
    
    if not directory:
        raise HTTPException(status_code=404, detail="Directory not found")
    
    # Run form detection in background
    async def run_analysis(dir_id: int, url: str):
        executor = SubmissionExecutor()
        try:
            await executor.browser.start()
            page = await executor.browser.new_page()
            await executor.browser.navigate_to_url(page, url)
            
            form_result = await executor.browser.detect_form(page, url)
            
            # Save the form schema
            async with get_db() as db:
                await DirectoryService(db).update_form_schema(
                    dir_id,
                    {
                        "form_found": form_result.form_found,
                        "form_selector": form_result.form_selector,
                        "fields": [f.model_dump() for f in form_result.fields],
                        "submit_button_selector": form_result.submit_button_selector,
                        "confidence": form_result.confidence
                    }
                )
                await db.commit()
        finally:
            await executor.browser.stop()
    
    background_tasks.add_task(
        run_analysis, 
        directory_id, 
        directory.submission_url or directory.url
    )
    
    return {"message": "Analysis started", "directory_id": directory_id}
