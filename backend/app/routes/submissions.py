"""
API Routes for Submissions
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services import SubmissionService, SaaSProductService, DirectoryService
from ..schemas import (
    SubmissionCreate, SubmissionBulkCreate, SubmissionResponse,
    SubmissionWithDetails, SubmissionStatus
)
from ..workers import run_single_submission

router = APIRouter(prefix="/submissions", tags=["Submissions"])


@router.post("/", response_model=SubmissionResponse)
async def create_submission(
    submission_data: SubmissionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new submission"""
    # Validate product exists
    product_service = SaaSProductService(db)
    product = await product_service.get_by_id(submission_data.saas_product_id)
    if not product:
        raise HTTPException(status_code=404, detail="SaaS product not found")
    
    # Validate directory exists
    directory_service = DirectoryService(db)
    directory = await directory_service.get_by_id(submission_data.directory_id)
    if not directory:
        raise HTTPException(status_code=404, detail="Directory not found")
    
    service = SubmissionService(db)
    submission = await service.create(submission_data)
    return submission


@router.post("/bulk", response_model=List[SubmissionResponse])
async def bulk_create_submissions(
    data: SubmissionBulkCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create submissions for multiple directories"""
    # Validate product exists
    product_service = SaaSProductService(db)
    product = await product_service.get_by_id(data.saas_product_id)
    if not product:
        raise HTTPException(status_code=404, detail="SaaS product not found")
    
    service = SubmissionService(db)
    submissions = await service.bulk_create(data.saas_product_id, data.directory_ids)
    return submissions


@router.get("/", response_model=List[SubmissionWithDetails])
async def list_submissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    saas_product_id: Optional[int] = None,
    directory_id: Optional[int] = None,
    status: Optional[SubmissionStatus] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all submissions with filtering"""
    service = SubmissionService(db)
    submissions, total = await service.get_all(
        skip=skip,
        limit=limit,
        saas_product_id=saas_product_id,
        directory_id=directory_id,
        status=status
    )
    return submissions


@router.get("/stats")
async def get_submission_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get submission statistics"""
    service = SubmissionService(db)
    stats = await service.get_stats()
    return stats


@router.get("/pending", response_model=List[SubmissionWithDetails])
async def get_pending_submissions(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get pending submissions ready to be processed"""
    service = SubmissionService(db)
    submissions = await service.get_pending_submissions(limit=limit)
    return submissions


@router.get("/retryable", response_model=List[SubmissionWithDetails])
async def get_retryable_submissions(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get failed submissions that can be retried"""
    service = SubmissionService(db)
    submissions = await service.get_retryable_submissions(limit=limit)
    return submissions


@router.get("/{submission_id}", response_model=SubmissionWithDetails)
async def get_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a submission by ID"""
    service = SubmissionService(db)
    submission = await service.get_by_id(submission_id)
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return submission


@router.post("/{submission_id}/run")
async def run_submission(
    submission_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Run a specific submission immediately"""
    service = SubmissionService(db)
    submission = await service.get_by_id(submission_id)
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Run in background
    background_tasks.add_task(run_single_submission, submission_id)
    
    return {
        "message": "Submission started",
        "submission_id": submission_id
    }


@router.post("/{submission_id}/retry")
async def retry_submission(
    submission_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Retry a failed submission"""
    service = SubmissionService(db)
    submission = await service.get_by_id(submission_id)
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if submission.status not in [SubmissionStatus.FAILED, SubmissionStatus.REJECTED]:
        raise HTTPException(
            status_code=400, 
            detail="Only failed or rejected submissions can be retried"
        )
    
    if submission.attempt_count >= submission.max_attempts:
        raise HTTPException(
            status_code=400, 
            detail="Maximum attempts reached"
        )
    
    # Reset status to pending
    await service.update_status(submission_id, SubmissionStatus.PENDING)
    
    # Run in background
    background_tasks.add_task(run_single_submission, submission_id)
    
    return {
        "message": "Retry started",
        "submission_id": submission_id
    }


@router.put("/{submission_id}/status")
async def update_submission_status(
    submission_id: int,
    status: SubmissionStatus,
    listing_url: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Manually update a submission status"""
    service = SubmissionService(db)
    submission = await service.update_status(
        submission_id, 
        status,
        listing_url=listing_url
    )
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return submission


@router.delete("/{submission_id}")
async def delete_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a submission"""
    service = SubmissionService(db)
    success = await service.delete(submission_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    return {"message": "Submission deleted successfully"}


@router.post("/run-batch")
async def run_batch_submissions(
    limit: int = Query(5, ge=1, le=20),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db)
):
    """Run a batch of pending submissions"""
    service = SubmissionService(db)
    submissions = await service.get_pending_submissions(limit=limit)
    
    if not submissions:
        return {"message": "No pending submissions", "count": 0}
    
    for submission in submissions:
        background_tasks.add_task(run_single_submission, submission.id)
    
    return {
        "message": f"Started {len(submissions)} submissions",
        "count": len(submissions),
        "submission_ids": [s.id for s in submissions]
    }
