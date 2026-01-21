"""
Service layer for Directory operations
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from datetime import datetime

from ..models import Directory, DirectoryStatus, DirectorySubmission
from ..schemas import DirectoryCreate, DirectoryUpdate
from loguru import logger


class DirectoryService:
    """Service for managing directories"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, directory_data: DirectoryCreate) -> Directory:
        """Create a new directory"""
        directory = Directory(**directory_data.model_dump())
        self.db.add(directory)
        await self.db.flush()
        await self.db.refresh(directory)
        logger.info(f"Created directory: {directory.name} (ID: {directory.id})")
        return directory
    
    async def bulk_create(self, directories_data: List[DirectoryCreate]) -> List[Directory]:
        """Create multiple directories at once"""
        directories = [Directory(**d.model_dump()) for d in directories_data]
        self.db.add_all(directories)
        await self.db.flush()
        
        for d in directories:
            await self.db.refresh(d)
        
        logger.info(f"Bulk created {len(directories)} directories")
        return directories
    
    async def get_by_id(self, directory_id: int) -> Optional[Directory]:
        """Get a directory by ID"""
        result = await self.db.execute(
            select(Directory).where(Directory.id == directory_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_url(self, url: str) -> Optional[Directory]:
        """Get a directory by URL"""
        result = await self.db.execute(
            select(Directory).where(Directory.url == url)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[DirectoryStatus] = None,
        category: Optional[str] = None
    ) -> List[Directory]:
        """Get all directories with optional filtering"""
        query = select(Directory)
        
        if status:
            query = query.where(Directory.status == status)
        if category:
            query = query.where(Directory.category == category)
        
        query = query.offset(skip).limit(limit).order_by(Directory.domain_authority.desc().nullslast())
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_count(self, status: Optional[DirectoryStatus] = None) -> int:
        """Get total count of directories"""
        query = select(func.count(Directory.id))
        
        if status:
            query = query.where(Directory.status == status)
        
        result = await self.db.execute(query)
        return result.scalar()
    
    async def get_active_directories(self) -> List[Directory]:
        """Get all active directories for submissions"""
        result = await self.db.execute(
            select(Directory)
            .where(Directory.status == DirectoryStatus.ACTIVE)
            .order_by(Directory.domain_authority.desc().nullslast())
        )
        return result.scalars().all()
    
    async def update(
        self,
        directory_id: int,
        directory_data: DirectoryUpdate
    ) -> Optional[Directory]:
        """Update a directory"""
        directory = await self.get_by_id(directory_id)
        if not directory:
            return None
        
        update_data = directory_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(directory, field, value)
        
        directory.updated_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(directory)
        logger.info(f"Updated directory: {directory.name} (ID: {directory.id})")
        return directory
    
    async def delete(self, directory_id: int) -> bool:
        """Delete a directory"""
        directory = await self.get_by_id(directory_id)
        if not directory:
            return False
        
        await self.db.delete(directory)
        logger.info(f"Deleted directory ID: {directory_id}")
        return True
    
    async def update_form_schema(self, directory_id: int, form_schema: dict) -> Optional[Directory]:
        """Update the cached form schema for a directory"""
        directory = await self.get_by_id(directory_id)
        if not directory:
            return None
        
        directory.form_schema = form_schema
        directory.last_checked_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(directory)
        return directory
    
    async def update_success_rate(self, directory_id: int) -> Optional[Directory]:
        """Recalculate and update the success rate for a directory"""
        directory = await self.get_by_id(directory_id)
        if not directory:
            return None
        
        # Get submission statistics
        result = await self.db.execute(
            select(
                func.count(DirectorySubmission.id).label('total'),
                func.sum(
                    func.cast(DirectorySubmission.status.in_(['submitted', 'approved']), type_=int)
                ).label('successful')
            )
            .where(DirectorySubmission.directory_id == directory_id)
        )
        row = result.one()
        
        if row.total and row.total > 0:
            directory.success_rate = int((row.successful or 0) / row.total * 100)
        else:
            directory.success_rate = 0
        
        await self.db.flush()
        await self.db.refresh(directory)
        return directory
    
    async def get_categories(self) -> List[str]:
        """Get all unique directory categories"""
        result = await self.db.execute(
            select(Directory.category)
            .where(Directory.category.isnot(None))
            .distinct()
        )
        return [row[0] for row in result.all()]
