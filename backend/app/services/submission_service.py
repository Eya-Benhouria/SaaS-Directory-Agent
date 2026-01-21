"""
Service layer for Submission operations
"""
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta

from ..models import (
    DirectorySubmission, SubmissionStatus, Directory, 
    SaaSProduct, SubmissionQueue, ActivityLog
)
from ..schemas import SubmissionCreate
from loguru import logger


class SubmissionService:
    """Service for managing submissions"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, submission_data: SubmissionCreate) -> DirectorySubmission:
        """Create a new submission"""
        submission = DirectorySubmission(
            saas_product_id=submission_data.saas_product_id,
            directory_id=submission_data.directory_id,
            status=SubmissionStatus.PENDING
        )
        self.db.add(submission)
        await self.db.flush()
        await self.db.refresh(submission)
        
        # Log activity
        await self._log_activity(
            "submission_created",
            "submission",
            submission.id,
            f"Created submission for directory ID {submission_data.directory_id}"
        )
        
        return submission
    
    async def bulk_create(
        self,
        saas_product_id: int,
        directory_ids: List[int]
    ) -> List[DirectorySubmission]:
        """Create submissions for multiple directories"""
        # Check which submissions already exist
        existing = await self.db.execute(
            select(DirectorySubmission.directory_id)
            .where(
                and_(
                    DirectorySubmission.saas_product_id == saas_product_id,
                    DirectorySubmission.directory_id.in_(directory_ids)
                )
            )
        )
        existing_ids = {row[0] for row in existing.all()}
        
        # Create only new submissions
        new_submissions = []
        for directory_id in directory_ids:
            if directory_id not in existing_ids:
                submission = DirectorySubmission(
                    saas_product_id=saas_product_id,
                    directory_id=directory_id,
                    status=SubmissionStatus.PENDING
                )
                self.db.add(submission)
                new_submissions.append(submission)
        
        await self.db.flush()
        
        for s in new_submissions:
            await self.db.refresh(s)
        
        logger.info(f"Bulk created {len(new_submissions)} submissions (skipped {len(existing_ids)} existing)")
        return new_submissions
    
    async def get_by_id(self, submission_id: int) -> Optional[DirectorySubmission]:
        """Get a submission by ID"""
        result = await self.db.execute(
            select(DirectorySubmission)
            .options(
                selectinload(DirectorySubmission.saas_product),
                selectinload(DirectorySubmission.directory)
            )
            .where(DirectorySubmission.id == submission_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        saas_product_id: Optional[int] = None,
        directory_id: Optional[int] = None,
        status: Optional[SubmissionStatus] = None
    ) -> Tuple[List[DirectorySubmission], int]:
        """Get all submissions with optional filtering"""
        query = select(DirectorySubmission).options(
            selectinload(DirectorySubmission.saas_product),
            selectinload(DirectorySubmission.directory)
        )
        count_query = select(func.count(DirectorySubmission.id))
        
        conditions = []
        if saas_product_id:
            conditions.append(DirectorySubmission.saas_product_id == saas_product_id)
        if directory_id:
            conditions.append(DirectorySubmission.directory_id == directory_id)
        if status:
            conditions.append(DirectorySubmission.status == status)
        
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))
        
        # Get total count
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(DirectorySubmission.created_at.desc())
        result = await self.db.execute(query)
        
        return result.scalars().all(), total
    
    async def get_pending_submissions(self, limit: int = 10) -> List[DirectorySubmission]:
        """Get pending submissions that are ready to be processed"""
        result = await self.db.execute(
            select(DirectorySubmission)
            .options(
                selectinload(DirectorySubmission.saas_product),
                selectinload(DirectorySubmission.directory)
            )
            .where(
                and_(
                    DirectorySubmission.status == SubmissionStatus.PENDING,
                    DirectorySubmission.attempt_count < DirectorySubmission.max_attempts
                )
            )
            .order_by(DirectorySubmission.created_at.asc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_retryable_submissions(self, limit: int = 10) -> List[DirectorySubmission]:
        """Get failed submissions that can be retried"""
        # Only retry submissions that failed more than 1 hour ago
        retry_after = datetime.utcnow() - timedelta(hours=1)
        
        result = await self.db.execute(
            select(DirectorySubmission)
            .options(
                selectinload(DirectorySubmission.saas_product),
                selectinload(DirectorySubmission.directory)
            )
            .where(
                and_(
                    DirectorySubmission.status == SubmissionStatus.FAILED,
                    DirectorySubmission.attempt_count < DirectorySubmission.max_attempts,
                    or_(
                        DirectorySubmission.last_attempt_at.is_(None),
                        DirectorySubmission.last_attempt_at < retry_after
                    )
                )
            )
            .order_by(DirectorySubmission.last_attempt_at.asc().nullsfirst())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def update_status(
        self,
        submission_id: int,
        status: SubmissionStatus,
        error_message: Optional[str] = None,
        listing_url: Optional[str] = None,
        screenshot_path: Optional[str] = None
    ) -> Optional[DirectorySubmission]:
        """Update the status of a submission"""
        submission = await self.get_by_id(submission_id)
        if not submission:
            return None
        
        submission.status = status
        submission.updated_at = datetime.utcnow()
        
        if status == SubmissionStatus.SUBMITTED:
            submission.submitted_at = datetime.utcnow()
        elif status == SubmissionStatus.APPROVED:
            submission.approved_at = datetime.utcnow()
        
        if error_message:
            submission.error_message = error_message
        if listing_url:
            submission.listing_url = listing_url
        if screenshot_path:
            submission.screenshot_path = screenshot_path
        
        await self.db.flush()
        await self.db.refresh(submission)
        
        # Log activity
        await self._log_activity(
            f"submission_{status.value}",
            "submission",
            submission_id,
            f"Submission status changed to {status.value}"
        )
        
        return submission
    
    async def record_attempt(
        self,
        submission_id: int,
        log_entry: dict,
        detected_fields: Optional[dict] = None,
        filled_fields: Optional[dict] = None
    ) -> Optional[DirectorySubmission]:
        """Record a submission attempt"""
        submission = await self.get_by_id(submission_id)
        if not submission:
            return None
        
        submission.attempt_count += 1
        submission.last_attempt_at = datetime.utcnow()
        
        # Append to submission log
        logs = submission.submission_log or []
        logs.append({
            **log_entry,
            'timestamp': datetime.utcnow().isoformat(),
            'attempt': submission.attempt_count
        })
        submission.submission_log = logs
        
        if detected_fields:
            submission.detected_fields = detected_fields
        if filled_fields:
            submission.filled_fields = filled_fields
        
        await self.db.flush()
        await self.db.refresh(submission)
        return submission
    
    async def get_stats(self) -> dict:
        """Get submission statistics"""
        result = await self.db.execute(
            select(
                DirectorySubmission.status,
                func.count(DirectorySubmission.id).label('count')
            )
            .group_by(DirectorySubmission.status)
        )
        
        status_counts = {row.status.value: row.count for row in result.all()}
        total = sum(status_counts.values())
        
        # Get today's submissions
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_result = await self.db.execute(
            select(func.count(DirectorySubmission.id))
            .where(DirectorySubmission.submitted_at >= today_start)
        )
        today_count = today_result.scalar() or 0
        
        # Get this week's submissions
        week_start = today_start - timedelta(days=today_start.weekday())
        week_result = await self.db.execute(
            select(func.count(DirectorySubmission.id))
            .where(DirectorySubmission.submitted_at >= week_start)
        )
        week_count = week_result.scalar() or 0
        
        successful = status_counts.get('submitted', 0) + status_counts.get('approved', 0)
        success_rate = (successful / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'pending': status_counts.get('pending', 0),
            'in_progress': status_counts.get('in_progress', 0),
            'submitted': status_counts.get('submitted', 0),
            'approved': status_counts.get('approved', 0),
            'failed': status_counts.get('failed', 0),
            'rejected': status_counts.get('rejected', 0),
            'requires_review': status_counts.get('requires_review', 0),
            'success_rate': round(success_rate, 2),
            'today': today_count,
            'this_week': week_count
        }
    
    async def delete(self, submission_id: int) -> bool:
        """Delete a submission"""
        submission = await self.get_by_id(submission_id)
        if not submission:
            return False
        
        await self.db.delete(submission)
        return True
    
    async def _log_activity(
        self,
        action: str,
        entity_type: str,
        entity_id: int,
        message: str,
        level: str = "info"
    ):
        """Log an activity"""
        log = ActivityLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            message=message,
            level=level
        )
        self.db.add(log)
