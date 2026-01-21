"""
API Routes for SaaS Products
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services import SaaSProductService, save_upload_file
from ..schemas import (
    SaaSProductCreate, SaaSProductUpdate, SaaSProductResponse,
    SaaSProductWithStats, APIResponse
)

router = APIRouter(prefix="/saas-products", tags=["SaaS Products"])


@router.post("/", response_model=SaaSProductResponse)
async def create_product(
    product_data: SaaSProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new SaaS product"""
    service = SaaSProductService(db)
    product = await service.create(product_data)
    return product


@router.get("/", response_model=List[SaaSProductResponse])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """List all SaaS products"""
    service = SaaSProductService(db)
    products = await service.get_all(skip=skip, limit=limit, is_active=is_active)
    return products


@router.get("/{product_id}", response_model=SaaSProductWithStats)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a SaaS product by ID with submission stats"""
    service = SaaSProductService(db)
    result = await service.get_with_submission_stats(product_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return result


@router.put("/{product_id}", response_model=SaaSProductResponse)
async def update_product(
    product_id: int,
    product_data: SaaSProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a SaaS product"""
    service = SaaSProductService(db)
    product = await service.update(product_id, product_data)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a SaaS product"""
    service = SaaSProductService(db)
    success = await service.delete(product_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Product deleted successfully"}


@router.post("/{product_id}/logo", response_model=SaaSProductResponse)
async def upload_logo(
    product_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload a logo for a SaaS product"""
    service = SaaSProductService(db)
    
    # Validate product exists
    product = await service.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/gif", "image/webp", "image/svg+xml"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Save file
    content = await file.read()
    file_path = await save_upload_file(content, file.filename, f"logos/{product_id}")
    
    # Update product
    product = await service.update_logo(product_id, file_path)
    return product


@router.post("/{product_id}/screenshots", response_model=SaaSProductResponse)
async def upload_screenshot(
    product_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload a screenshot for a SaaS product"""
    service = SaaSProductService(db)
    
    # Validate product exists
    product = await service.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Validate file type
    allowed_types = ["image/png", "image/jpeg", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    # Save file
    content = await file.read()
    file_path = await save_upload_file(content, file.filename, f"screenshots/{product_id}")
    
    # Update product
    product = await service.add_screenshot(product_id, file_path)
    return product
