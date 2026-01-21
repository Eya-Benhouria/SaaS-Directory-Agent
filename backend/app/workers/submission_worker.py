"""
Submission Worker - Background task processor
Handles queued submissions using async processing
"""
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
import random
from loguru import logger

from ..database import async_session_maker
from ..services import SubmissionService
from ..models import DirectorySubmission, SubmissionStatus, SaaSProduct, Directory
from ..automation.browser import SubmissionExecutor
from ..automation.demo_simulator import demo_simulator
from ..config import settings


class SubmissionWorker:
    """Background worker for processing submission queue"""
    
    def __init__(self):
        self.executor = SubmissionExecutor()
        self.is_running = False
        self.max_concurrent = settings.MAX_CONCURRENT_SUBMISSIONS
        self.current_tasks = 0
    
    async def start(self):
        """Start the worker"""
        self.is_running = True
        logger.info("Submission worker started")
        
        while self.is_running:
            try:
                await self._process_queue()
                # Wait before next check
                await asyncio.sleep(30)
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(60)
    
    async def stop(self):
        """Stop the worker"""
        self.is_running = False
        logger.info("Submission worker stopped")
    
    async def _process_queue(self):
        """Process pending submissions"""
        async with async_session_maker() as db:
            service = SubmissionService(db)
            
            # Get pending submissions
            submissions = await service.get_pending_submissions(
                limit=self.max_concurrent - self.current_tasks
            )
            
            if not submissions:
                return
            
            logger.info(f"Processing {len(submissions)} submissions")
            
            for submission in submissions:
                if self.current_tasks >= self.max_concurrent:
                    break
                
                # Process submission
                await self._process_submission(submission.id)
                
                # Random delay between submissions (30-90 seconds)
                delay = random.randint(30, 90)
                await asyncio.sleep(delay)
    
    async def _process_submission(self, submission_id: int):
        """Process a single submission"""
        self.current_tasks += 1
        
        try:
            async with async_session_maker() as db:
                service = SubmissionService(db)
                
                # Get submission with related data
                submission = await service.get_by_id(submission_id)
                if not submission:
                    return
                
                # Update status to in_progress
                await service.update_status(
                    submission_id, 
                    SubmissionStatus.IN_PROGRESS
                )
                await db.commit()
                
                # Prepare SaaS data
                saas_data = self._prepare_saas_data(submission.saas_product)
                
                # Get directory URL
                directory_url = submission.directory.submission_url or submission.directory.url
                
                logger.info(f"Executing submission {submission_id} to {directory_url}")
                
                # Execute submission - use demo mode if enabled
                if settings.DEMO_MODE:
                    logger.info(f"[DEMO MODE] Simulating submission to {submission.directory.name}")
                    result = await demo_simulator.execute_full_submission(
                        directory_name=submission.directory.name,
                        directory_url=submission.directory.url,
                        submission_url=directory_url,
                        saas_data=saas_data
                    )
                else:
                    result = await self.executor.execute_submission(
                        directory_url=directory_url,
                        saas_data=saas_data,
                        logo_path=submission.saas_product.logo_path
                    )
                
                # Record attempt
                await service.record_attempt(
                    submission_id,
                    log_entry={
                        "status": "success" if result["success"] else "failed",
                        "logs": result.get("logs", []),
                        "error": result.get("error")
                    },
                    detected_fields=result.get("detected_fields"),
                    filled_fields=result.get("filled_fields")
                )
                
                # Update final status
                if result["success"]:
                    await service.update_status(
                        submission_id,
                        SubmissionStatus.SUBMITTED,
                        screenshot_path=result.get("screenshot_path")
                    )
                else:
                    # Check if max attempts reached
                    if submission.attempt_count >= submission.max_attempts - 1:
                        status = SubmissionStatus.FAILED
                    else:
                        status = SubmissionStatus.PENDING  # Will retry
                    
                    await service.update_status(
                        submission_id,
                        status,
                        error_message=result.get("error"),
                        screenshot_path=result.get("screenshot_path")
                    )
                
                await db.commit()
                
        except Exception as e:
            logger.error(f"Error processing submission {submission_id}: {e}")
            
            async with async_session_maker() as db:
                service = SubmissionService(db)
                await service.update_status(
                    submission_id,
                    SubmissionStatus.FAILED,
                    error_message=str(e)
                )
                await db.commit()
                
        finally:
            self.current_tasks -= 1
    
    def _prepare_saas_data(self, product: SaaSProduct) -> dict:
        """Prepare SaaS data for form filling"""
        return {
            "name": product.name,
            "saas_name": product.name,
            "website_url": product.website_url,
            "url": product.website_url,
            "tagline": product.tagline or "",
            "short_description": product.short_description or product.tagline or "",
            "long_description": product.long_description or product.short_description or "",
            "category": product.category or "",
            "contact_email": product.contact_email,
            "contact_name": product.contact_name or "",
            "twitter_url": product.twitter_url or "",
            "linkedin_url": product.linkedin_url or "",
            "github_url": product.github_url or "",
            "pricing_model": product.pricing_model or "",
            "pricing_details": product.pricing_details or "",
            "tags": ", ".join(product.tags) if product.tags else "",
        }


# Singleton worker instance
worker_instance: Optional[SubmissionWorker] = None


def get_worker() -> SubmissionWorker:
    """Get or create worker instance"""
    global worker_instance
    if worker_instance is None:
        worker_instance = SubmissionWorker()
    return worker_instance


async def run_single_submission(submission_id: int) -> dict:
    """Run a single submission immediately"""
    executor = SubmissionExecutor()
    
    async with async_session_maker() as db:
        service = SubmissionService(db)
        submission = await service.get_by_id(submission_id)
        
        if not submission:
            return {"error": "Submission not found"}
        
        # Update status
        await service.update_status(submission_id, SubmissionStatus.IN_PROGRESS)
        await db.commit()
        
        # Prepare data
        saas_data = {
            "name": submission.saas_product.name,
            "website_url": submission.saas_product.website_url,
            "tagline": submission.saas_product.tagline or "",
            "short_description": submission.saas_product.short_description or "",
            "long_description": submission.saas_product.long_description or "",
            "category": submission.saas_product.category or "",
            "contact_email": submission.saas_product.contact_email,
            "contact_name": submission.saas_product.contact_name or "",
            "twitter_url": submission.saas_product.twitter_url or "",
            "pricing_model": submission.saas_product.pricing_model or "",
        }
        
        directory_url = submission.directory.submission_url or submission.directory.url
        
        # Execute - use demo mode if enabled
        if settings.DEMO_MODE:
            logger.info(f"[DEMO MODE] Running single submission to {submission.directory.name}")
            result = await demo_simulator.execute_full_submission(
                directory_name=submission.directory.name,
                directory_url=submission.directory.url,
                submission_url=directory_url,
                saas_data=saas_data
            )
        else:
            result = await executor.execute_submission(
                directory_url=directory_url,
                saas_data=saas_data,
                logo_path=submission.saas_product.logo_path
            )
        
        # Record result
        await service.record_attempt(
            submission_id,
            log_entry={
                "status": "success" if result["success"] else "failed",
                "logs": result.get("logs", [])
            },
            detected_fields=result.get("detected_fields"),
            filled_fields=result.get("filled_fields")
        )
        
        if result["success"]:
            await service.update_status(
                submission_id,
                SubmissionStatus.SUBMITTED,
                screenshot_path=result.get("screenshot_path")
            )
        else:
            await service.update_status(
                submission_id,
                SubmissionStatus.FAILED,
                error_message=result.get("error"),
                screenshot_path=result.get("screenshot_path")
            )
        
        await db.commit()
        return result
