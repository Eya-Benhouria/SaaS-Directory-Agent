"""
API Routes for Dashboard
"""
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..database import get_db
from ..models import SaaSProduct, Directory, DirectorySubmission, ActivityLog
from ..services import SubmissionService, SaaSProductService, DirectoryService
from ..schemas import DashboardStats, SubmissionTrend
from ..config import settings

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get overall dashboard statistics"""
    product_service = SaaSProductService(db)
    directory_service = DirectoryService(db)
    submission_service = SubmissionService(db)
    
    # Get counts
    total_products = await product_service.get_count(is_active=True)
    total_directories = await directory_service.get_count()
    
    # Get submission stats
    submission_stats = await submission_service.get_stats()
    
    return DashboardStats(
        total_products=total_products,
        total_directories=total_directories,
        total_submissions=submission_stats['total'],
        pending_submissions=submission_stats['pending'],
        in_progress_submissions=submission_stats['in_progress'],
        submitted_submissions=submission_stats['submitted'],
        approved_submissions=submission_stats['approved'],
        failed_submissions=submission_stats['failed'],
        success_rate=submission_stats['success_rate'],
        submissions_today=submission_stats['today'],
        submissions_this_week=submission_stats['this_week']
    )


@router.get("/trends", response_model=List[SubmissionTrend])
async def get_submission_trends(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """Get submission trends for the last N days"""
    trends = []
    
    for i in range(days - 1, -1, -1):
        date = datetime.utcnow().date() - timedelta(days=i)
        start_of_day = datetime.combine(date, datetime.min.time())
        end_of_day = datetime.combine(date, datetime.max.time())
        
        # Count submissions by status for this day
        result = await db.execute(
            select(
                DirectorySubmission.status,
                func.count(DirectorySubmission.id)
            )
            .where(
                DirectorySubmission.submitted_at >= start_of_day,
                DirectorySubmission.submitted_at <= end_of_day
            )
            .group_by(DirectorySubmission.status)
        )
        
        status_counts = {row[0].value: row[1] for row in result.all()}
        
        trends.append(SubmissionTrend(
            date=date.isoformat(),
            submitted=status_counts.get('submitted', 0),
            approved=status_counts.get('approved', 0),
            failed=status_counts.get('failed', 0)
        ))
    
    return trends


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get recent activity logs"""
    result = await db.execute(
        select(ActivityLog)
        .order_by(ActivityLog.created_at.desc())
        .limit(limit)
    )
    
    logs = result.scalars().all()
    
    return [
        {
            "id": log.id,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "message": log.message,
            "level": log.level,
            "created_at": log.created_at.isoformat()
        }
        for log in logs
    ]


@router.get("/top-directories")
async def get_top_directories(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get top directories by success rate"""
    result = await db.execute(
        select(Directory)
        .where(Directory.status == 'active')
        .order_by(Directory.success_rate.desc(), Directory.domain_authority.desc().nullslast())
        .limit(limit)
    )
    
    directories = result.scalars().all()
    
    return [
        {
            "id": d.id,
            "name": d.name,
            "url": d.url,
            "success_rate": d.success_rate,
            "domain_authority": d.domain_authority
        }
        for d in directories
    ]


@router.get("/submission-status-breakdown")
async def get_status_breakdown(
    saas_product_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """Get submission status breakdown"""
    query = select(
        DirectorySubmission.status,
        func.count(DirectorySubmission.id).label('count')
    )
    
    if saas_product_id:
        query = query.where(DirectorySubmission.saas_product_id == saas_product_id)
    
    query = query.group_by(DirectorySubmission.status)
    
    result = await db.execute(query)
    
    return {row.status.value: row.count for row in result.all()}


@router.get("/system-status")
async def get_system_status(
    db: AsyncSession = Depends(get_db)
):
    """Get system status including demo mode indicator"""
    product_service = SaaSProductService(db)
    directory_service = DirectoryService(db)
    
    total_products = await product_service.get_count(is_active=True)
    total_directories = await directory_service.get_count()
    
    return {
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "demo_mode": settings.DEMO_MODE,
        "llm_provider": settings.LLM_PROVIDER,
        "has_openai_key": bool(settings.OPENAI_API_KEY),
        "has_anthropic_key": bool(settings.ANTHROPIC_API_KEY),
        "browser_headless": settings.BROWSER_HEADLESS,
        "max_concurrent_submissions": settings.MAX_CONCURRENT_SUBMISSIONS,
        "database_connected": True,
        "total_products": total_products,
        "total_directories": total_directories,
        "status": "healthy"
    }
