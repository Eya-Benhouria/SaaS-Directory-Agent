"""
Service layer for SaaS Product operations
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import selectinload
import os
import aiofiles
from datetime import datetime

from ..models import SaaSProduct, DirectorySubmission, SubmissionStatus
from ..schemas import SaaSProductCreate, SaaSProductUpdate
from ..config import settings
from loguru import logger


class SaaSProductService:
    """Service for managing SaaS products"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, product_data: SaaSProductCreate) -> SaaSProduct:
        """Create a new SaaS product"""
        product = SaaSProduct(**product_data.model_dump())
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        logger.info(f"Created SaaS product: {product.name} (ID: {product.id})")
        return product
    
    async def get_by_id(self, product_id: int) -> Optional[SaaSProduct]:
        """Get a SaaS product by ID"""
        result = await self.db.execute(
            select(SaaSProduct).where(SaaSProduct.id == product_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[SaaSProduct]:
        """Get all SaaS products with pagination"""
        query = select(SaaSProduct)
        
        if is_active is not None:
            query = query.where(SaaSProduct.is_active == is_active)
        
        query = query.offset(skip).limit(limit).order_by(SaaSProduct.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_count(self, is_active: Optional[bool] = None) -> int:
        """Get total count of SaaS products"""
        query = select(func.count(SaaSProduct.id))
        
        if is_active is not None:
            query = query.where(SaaSProduct.is_active == is_active)
        
        result = await self.db.execute(query)
        return result.scalar()
    
    async def update(
        self, 
        product_id: int, 
        product_data: SaaSProductUpdate
    ) -> Optional[SaaSProduct]:
        """Update a SaaS product"""
        product = await self.get_by_id(product_id)
        if not product:
            return None
        
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        product.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(product)
        logger.info(f"Updated SaaS product: {product.name} (ID: {product.id})")
        return product
    
    async def delete(self, product_id: int) -> bool:
        """Delete a SaaS product"""
        product = await self.get_by_id(product_id)
        if not product:
            return False
        
        await self.db.delete(product)
        logger.info(f"Deleted SaaS product: {product.name} (ID: {product_id})")
        return True
    
    async def update_logo(self, product_id: int, logo_path: str) -> Optional[SaaSProduct]:
        """Update the logo path for a product"""
        product = await self.get_by_id(product_id)
        if not product:
            return None
        
        product.logo_path = logo_path
        product.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(product)
        return product
    
    async def add_screenshot(self, product_id: int, screenshot_path: str) -> Optional[SaaSProduct]:
        """Add a screenshot to a product"""
        product = await self.get_by_id(product_id)
        if not product:
            return None
        
        screenshots = product.screenshot_paths or []
        screenshots.append(screenshot_path)
        product.screenshot_paths = screenshots
        product.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(product)
        return product
    
    async def get_with_submission_stats(self, product_id: int) -> Optional[dict]:
        """Get a product with its submission statistics"""
        product = await self.get_by_id(product_id)
        if not product:
            return None
        
        # Get submission counts by status
        result = await self.db.execute(
            select(
                DirectorySubmission.status,
                func.count(DirectorySubmission.id).label('count')
            )
            .where(DirectorySubmission.saas_product_id == product_id)
            .group_by(DirectorySubmission.status)
        )
        
        status_counts = {row.status.value: row.count for row in result.all()}
        
        return {
            **product.__dict__,
            'total_submissions': sum(status_counts.values()),
            'pending_count': status_counts.get('pending', 0),
            'in_progress_count': status_counts.get('in_progress', 0),
            'submitted_count': status_counts.get('submitted', 0),
            'approved_count': status_counts.get('approved', 0),
            'failed_count': status_counts.get('failed', 0),
            'rejected_count': status_counts.get('rejected', 0),
        }


async def save_upload_file(
    file_content: bytes,
    filename: str,
    subfolder: str = ""
) -> str:
    """Save an uploaded file and return the path"""
    upload_dir = os.path.join(settings.UPLOAD_DIR, subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{filename}"
    file_path = os.path.join(upload_dir, safe_filename)
    
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(file_content)
    
    return file_path
