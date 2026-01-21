"""
Demo Simulator for SaaS Directory Submission Agent
Simulates realistic submission workflows without requiring real API keys or external access
"""
import asyncio
import random
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger

# Simulated form schemas for different directory types
DEMO_FORM_SCHEMAS = {
    "product_hunt": {
        "fields": [
            {"name": "product_name", "field_type": "text", "label": "Product Name", "required": True},
            {"name": "tagline", "field_type": "text", "label": "Tagline", "required": True},
            {"name": "description", "field_type": "textarea", "label": "Description", "required": True},
            {"name": "website_url", "field_type": "url", "label": "Website URL", "required": True},
            {"name": "category", "field_type": "select", "label": "Category", "required": True},
            {"name": "logo", "field_type": "file", "label": "Logo", "required": False},
        ],
        "submit_button": "button[type='submit']",
        "form_selector": "form.product-submission"
    },
    "betalist": {
        "fields": [
            {"name": "startup_name", "field_type": "text", "label": "Startup Name", "required": True},
            {"name": "url", "field_type": "url", "label": "URL", "required": True},
            {"name": "pitch", "field_type": "textarea", "label": "One-line Pitch", "required": True},
            {"name": "description", "field_type": "textarea", "label": "Description", "required": True},
            {"name": "email", "field_type": "email", "label": "Contact Email", "required": True},
        ],
        "submit_button": "#submit-btn",
        "form_selector": "form#startup-form"
    },
    "saas_hub": {
        "fields": [
            {"name": "tool_name", "field_type": "text", "label": "Tool Name", "required": True},
            {"name": "website", "field_type": "url", "label": "Website", "required": True},
            {"name": "short_description", "field_type": "text", "label": "Short Description", "required": True},
            {"name": "long_description", "field_type": "textarea", "label": "Full Description", "required": True},
            {"name": "pricing", "field_type": "select", "label": "Pricing Model", "required": True},
            {"name": "category", "field_type": "select", "label": "Category", "required": True},
        ],
        "submit_button": "button.submit-tool",
        "form_selector": "form.tool-submission-form"
    },
    "generic": {
        "fields": [
            {"name": "name", "field_type": "text", "label": "Product/Company Name", "required": True},
            {"name": "url", "field_type": "url", "label": "Website URL", "required": True},
            {"name": "description", "field_type": "textarea", "label": "Description", "required": True},
            {"name": "email", "field_type": "email", "label": "Contact Email", "required": True},
            {"name": "category", "field_type": "select", "label": "Category", "required": False},
        ],
        "submit_button": "button[type='submit'], input[type='submit']",
        "form_selector": "form"
    }
}

# Success messages that directories typically show
SUCCESS_MESSAGES = [
    "Thank you for your submission! We'll review it within 24-48 hours.",
    "Your product has been submitted successfully. You'll receive a confirmation email.",
    "Submission received! Our team will review and publish within 3-5 business days.",
    "Thanks for submitting! Your listing is now pending review.",
    "Success! Your SaaS has been added to our review queue.",
    "We've received your submission. Expect an update within 1 week.",
]


class DemoSubmissionSimulator:
    """
    Simulates the entire submission workflow for demo purposes.
    Provides realistic delays, form detection, and submission results.
    """
    
    def __init__(self):
        self.simulation_speed = 1.0  # Adjust for faster/slower demos
    
    async def _simulate_delay(self, min_seconds: float, max_seconds: float):
        """Add realistic delays to simulate real browser operations"""
        delay = random.uniform(min_seconds, max_seconds) * self.simulation_speed
        await asyncio.sleep(delay)
    
    def _get_form_schema_for_directory(self, directory_name: str, url: str) -> Dict[str, Any]:
        """Get appropriate form schema based on directory"""
        name_lower = directory_name.lower()
        url_lower = url.lower()
        
        if "producthunt" in url_lower or "product hunt" in name_lower:
            return DEMO_FORM_SCHEMAS["product_hunt"]
        elif "betalist" in url_lower:
            return DEMO_FORM_SCHEMAS["betalist"]
        elif "saashub" in url_lower or "saas" in name_lower:
            return DEMO_FORM_SCHEMAS["saas_hub"]
        else:
            return DEMO_FORM_SCHEMAS["generic"]
    
    async def simulate_navigation(self, url: str) -> Dict[str, Any]:
        """Simulate navigating to a directory page"""
        logger.info(f"[DEMO] Navigating to: {url}")
        await self._simulate_delay(1.0, 2.5)
        
        # Simulate occasional slow loading
        if random.random() < 0.1:
            logger.info(f"[DEMO] Page loading slowly...")
            await self._simulate_delay(1.0, 2.0)
        
        return {
            "success": True,
            "status_code": 200,
            "load_time_ms": random.randint(500, 2500)
        }
    
    async def simulate_form_detection(
        self, 
        directory_name: str, 
        url: str
    ) -> Dict[str, Any]:
        """Simulate AI-powered form detection"""
        logger.info(f"[DEMO] Detecting form fields on: {url}")
        await self._simulate_delay(1.5, 3.0)
        
        schema = self._get_form_schema_for_directory(directory_name, url)
        
        # Add detection metadata
        result = {
            "fields": schema["fields"],
            "form_selector": schema["form_selector"],
            "submit_button": schema["submit_button"],
            "confidence": random.uniform(0.85, 0.98),
            "detection_method": "LLM Vision Analysis (Demo)",
            "field_count": len(schema["fields"])
        }
        
        logger.info(f"[DEMO] Detected {len(schema['fields'])} form fields with {result['confidence']:.2%} confidence")
        return result
    
    async def simulate_form_filling(
        self, 
        saas_data: Dict[str, Any],
        detected_fields: list
    ) -> Dict[str, Any]:
        """Simulate filling form fields"""
        filled_fields = {}
        
        for field in detected_fields:
            field_name = field["name"]
            await self._simulate_delay(0.3, 0.8)
            
            # Map SaaS data to form fields
            value = self._map_saas_data_to_field(field_name, saas_data)
            filled_fields[field_name] = {
                "value": value,
                "success": True,
                "field_type": field["field_type"]
            }
            logger.info(f"[DEMO] Filled field '{field_name}': {value[:50] if len(str(value)) > 50 else value}...")
        
        return {
            "filled_count": len(filled_fields),
            "total_fields": len(detected_fields),
            "fields": filled_fields
        }
    
    def _map_saas_data_to_field(self, field_name: str, saas_data: Dict[str, Any]) -> str:
        """Map SaaS product data to form field names"""
        field_name_lower = field_name.lower()
        
        mappings = {
            "name": saas_data.get("name", ""),
            "product_name": saas_data.get("name", ""),
            "startup_name": saas_data.get("name", ""),
            "tool_name": saas_data.get("name", ""),
            "url": saas_data.get("website_url", ""),
            "website": saas_data.get("website_url", ""),
            "website_url": saas_data.get("website_url", ""),
            "tagline": saas_data.get("tagline", ""),
            "pitch": saas_data.get("tagline", ""),
            "description": saas_data.get("short_description", ""),
            "short_description": saas_data.get("short_description", ""),
            "long_description": saas_data.get("long_description", ""),
            "email": saas_data.get("contact_email", ""),
            "contact_email": saas_data.get("contact_email", ""),
            "category": saas_data.get("category", ""),
            "pricing": saas_data.get("pricing_model", ""),
        }
        
        # Try exact match first
        if field_name_lower in mappings:
            return str(mappings[field_name_lower])
        
        # Try partial match
        for key, value in mappings.items():
            if key in field_name_lower or field_name_lower in key:
                return str(value)
        
        return ""
    
    async def simulate_submission(
        self,
        directory_name: str,
        url: str
    ) -> Dict[str, Any]:
        """Simulate clicking submit and getting result"""
        logger.info(f"[DEMO] Submitting form on: {directory_name}")
        await self._simulate_delay(1.0, 2.0)
        
        # Simulate realistic success rate (90% success for demo)
        success = random.random() < 0.90
        
        if success:
            result = {
                "success": True,
                "status": "submitted",
                "message": random.choice(SUCCESS_MESSAGES),
                "confirmation_id": f"SUB-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
                "next_steps": "Check your email for confirmation and approval updates."
            }
            logger.info(f"[DEMO] ✅ Submission successful: {result['message'][:50]}...")
        else:
            # Simulate realistic failures
            failure_reasons = [
                "CAPTCHA detected - manual intervention required",
                "Rate limit reached - try again in 24 hours",
                "Account verification required",
            ]
            result = {
                "success": False,
                "status": "failed",
                "message": random.choice(failure_reasons),
                "retry_after": random.randint(3600, 86400)
            }
            logger.info(f"[DEMO] ❌ Submission failed: {result['message']}")
        
        return result
    
    async def execute_full_submission(
        self,
        directory_name: str,
        directory_url: str,
        submission_url: str,
        saas_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a complete simulated submission workflow.
        Returns results matching the real submission executor output.
        """
        logger.info(f"[DEMO] Starting simulated submission to: {directory_name}")
        start_time = datetime.now()
        
        try:
            # Step 1: Navigate to submission page
            nav_result = await self.simulate_navigation(submission_url)
            if not nav_result["success"]:
                return {
                    "success": False,
                    "status": "failed",
                    "error_message": "Failed to load submission page",
                    "screenshot_path": None
                }
            
            # Step 2: Detect form fields
            detection_result = await self.simulate_form_detection(directory_name, submission_url)
            
            # Step 3: Fill form
            fill_result = await self.simulate_form_filling(saas_data, detection_result["fields"])
            
            # Step 4: Submit
            submit_result = await self.simulate_submission(directory_name, submission_url)
            
            # Calculate timing
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # Generate demo screenshot path
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"screenshots/demo_{directory_name.lower().replace(' ', '_')}_{timestamp}.png"
            
            return {
                "success": submit_result["success"],
                "status": "submitted" if submit_result["success"] else "failed",
                "error_message": None if submit_result["success"] else submit_result.get("message"),
                "screenshot_path": screenshot_path,
                "detected_fields": detection_result,
                "filled_fields": fill_result["fields"],
                "submission_result": submit_result,
                "duration_seconds": duration,
                "demo_mode": True
            }
            
        except Exception as e:
            logger.error(f"[DEMO] Simulation error: {e}")
            return {
                "success": False,
                "status": "failed",
                "error_message": str(e),
                "screenshot_path": None,
                "demo_mode": True
            }


# Singleton instance
demo_simulator = DemoSubmissionSimulator()
