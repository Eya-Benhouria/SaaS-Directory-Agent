"""
Browser Automation using Playwright
Handles navigation, form filling, and submission
"""
import asyncio
import base64
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from loguru import logger

from ..config import settings
from .form_detector import FormDetectionService, RuleBasedFormDetector
from ..schemas import FormField, FormDetectionResult


class BrowserAutomation:
    """Playwright-based browser automation for form submission"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.form_detector = FormDetectionService()
        self.rule_detector = RuleBasedFormDetector()
        self.screenshot_dir = os.path.join(settings.UPLOAD_DIR, "screenshots")
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    async def start(self):
        """Start the browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=settings.BROWSER_HEADLESS,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
            ]
        )
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        )
        logger.info("Browser started")
    
    async def stop(self):
        """Stop the browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info("Browser stopped")
    
    async def new_page(self) -> Page:
        """Create a new page"""
        if not self.context:
            await self.start()
        return await self.context.new_page()
    
    async def navigate_to_url(self, page: Page, url: str) -> bool:
        """Navigate to a URL"""
        try:
            logger.info(f"Navigating to: {url}")
            response = await page.goto(
                url, 
                wait_until='networkidle',
                timeout=settings.BROWSER_TIMEOUT
            )
            
            if response and response.ok:
                # Wait for page to stabilize
                await asyncio.sleep(2)
                return True
            
            logger.warning(f"Navigation returned status: {response.status if response else 'No response'}")
            return False
            
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return False
    
    async def take_screenshot(self, page: Page, name: str) -> str:
        """Take a screenshot and return the relative path for serving"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(self.screenshot_dir, filename)
        
        await page.screenshot(path=filepath, full_page=True)
        logger.info(f"Screenshot saved: {filepath}")
        # Return relative path from uploads directory (for URL serving as /uploads/screenshots/...)
        return f"screenshots/{filename}"
    
    async def get_screenshot_base64(self, page: Page) -> str:
        """Get screenshot as base64 string"""
        screenshot_bytes = await page.screenshot(full_page=True)
        return base64.b64encode(screenshot_bytes).decode('utf-8')
    
    async def get_page_html(self, page: Page) -> str:
        """Get the page HTML content"""
        return await page.content()
    
    async def detect_form(self, page: Page, url: str) -> FormDetectionResult:
        """Detect form on the current page"""
        try:
            # Get screenshot and HTML
            screenshot_base64 = await self.get_screenshot_base64(page)
            html = await self.get_page_html(page)
            
            # Use LLM-based detection
            result = await self.form_detector.detect_form(
                screenshot_base64=screenshot_base64,
                page_html=html,
                url=url
            )
            
            # If LLM detection failed, try rule-based fallback
            if not result.form_found or len(result.fields) == 0:
                logger.info("LLM detection failed, trying rule-based detection")
                fields = self.rule_detector.detect_fields_from_html(html)
                if fields:
                    result = FormDetectionResult(
                        url=url,
                        form_found=True,
                        fields=fields,
                        confidence=0.5
                    )
            
            return result
            
        except Exception as e:
            logger.error(f"Form detection failed: {e}")
            return FormDetectionResult(url=url, form_found=False, fields=[])
    
    async def fill_field(
        self, 
        page: Page, 
        selector: str, 
        value: str, 
        field_type: str = "text"
    ) -> bool:
        """Fill a single form field"""
        try:
            # Wait for the element
            element = await page.wait_for_selector(
                selector, 
                timeout=5000,
                state='visible'
            )
            
            if not element:
                logger.warning(f"Element not found: {selector}")
                return False
            
            if field_type == "select":
                await element.select_option(value)
            elif field_type == "checkbox":
                if value.lower() in ['true', '1', 'yes']:
                    await element.check()
            elif field_type == "radio":
                await element.check()
            elif field_type == "file":
                await element.set_input_files(value)
            else:
                # Clear existing value first
                await element.click()
                await element.fill("")
                await element.type(value, delay=50)  # Human-like typing
            
            logger.info(f"Filled field {selector} with value: {value[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Failed to fill field {selector}: {e}")
            return False
    
    async def fill_form(
        self,
        page: Page,
        field_mapping: Dict[str, Dict[str, Any]]
    ) -> Dict[str, bool]:
        """Fill multiple form fields"""
        results = {}
        
        for selector, field_info in field_mapping.items():
            value = field_info.get("value", "")
            field_type = field_info.get("field_type", "text")
            
            success = await self.fill_field(page, selector, str(value), field_type)
            results[selector] = success
            
            # Small delay between fields to appear human
            await asyncio.sleep(0.3)
        
        return results
    
    async def click_submit(self, page: Page, submit_selector: str) -> bool:
        """Click the submit button"""
        try:
            # Try to find and click the submit button
            button = await page.wait_for_selector(
                submit_selector,
                timeout=5000,
                state='visible'
            )
            
            if button:
                await button.click()
                logger.info(f"Clicked submit button: {submit_selector}")
                
                # Wait for navigation or response
                await asyncio.sleep(3)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to click submit: {e}")
            return False
    
    async def find_submit_button(self, page: Page) -> Optional[str]:
        """Find submit button if not detected"""
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Submit")',
            'button:has-text("Add")',
            'button:has-text("Create")',
            'button:has-text("Post")',
            'button:has-text("Send")',
            '.submit-btn',
            '.btn-submit',
            '#submit',
            '#submit-btn',
        ]
        
        for selector in submit_selectors:
            try:
                element = await page.query_selector(selector)
                if element and await element.is_visible():
                    return selector
            except:
                continue
        
        return None
    
    async def check_submission_success(self, page: Page) -> Dict[str, Any]:
        """Check if submission was successful"""
        # Get current URL and content
        current_url = page.url
        html = await page.content()
        html_lower = html.lower()
        
        # Success indicators
        success_phrases = [
            'thank you',
            'thanks for',
            'successfully submitted',
            'submission received',
            'we will review',
            'pending approval',
            'listing added',
            'product added',
            'successfully added',
        ]
        
        # Error indicators
        error_phrases = [
            'error',
            'failed',
            'invalid',
            'required field',
            'please fill',
            'already exists',
            'duplicate',
        ]
        
        # Check for success
        for phrase in success_phrases:
            if phrase in html_lower:
                return {
                    "success": True,
                    "message": f"Detected success phrase: {phrase}",
                    "url": current_url
                }
        
        # Check for errors
        for phrase in error_phrases:
            if phrase in html_lower:
                return {
                    "success": False,
                    "message": f"Detected error phrase: {phrase}",
                    "url": current_url
                }
        
        # URL change might indicate success
        return {
            "success": None,
            "message": "Could not determine submission result",
            "url": current_url
        }
    
    async def handle_captcha(self, page: Page) -> bool:
        """Detect and handle CAPTCHA (placeholder for future implementation)"""
        # Check for common CAPTCHA indicators
        captcha_indicators = [
            'iframe[src*="recaptcha"]',
            'iframe[src*="captcha"]',
            '.g-recaptcha',
            '#captcha',
            '[data-captcha]',
        ]
        
        for selector in captcha_indicators:
            try:
                element = await page.query_selector(selector)
                if element:
                    logger.warning(f"CAPTCHA detected: {selector}")
                    return True
            except:
                continue
        
        return False
    
    async def scroll_to_form(self, page: Page, form_selector: str):
        """Scroll to make form visible"""
        try:
            await page.evaluate(f'''
                document.querySelector("{form_selector}")?.scrollIntoView({{
                    behavior: 'smooth',
                    block: 'center'
                }});
            ''')
            await asyncio.sleep(1)
        except:
            pass


class SubmissionExecutor:
    """Execute the full submission workflow"""
    
    def __init__(self):
        self.browser = BrowserAutomation()
        self.form_detector = FormDetectionService()
    
    async def execute_submission(
        self,
        directory_url: str,
        saas_data: Dict[str, Any],
        logo_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a complete submission workflow"""
        result = {
            "success": False,
            "url": directory_url,
            "detected_fields": {},
            "filled_fields": {},
            "screenshot_path": None,
            "error": None,
            "logs": []
        }
        
        page = None
        
        try:
            await self.browser.start()
            page = await self.browser.new_page()
            
            # Step 1: Navigate to directory
            result["logs"].append({"step": "navigate", "status": "started"})
            nav_success = await self.browser.navigate_to_url(page, directory_url)
            
            if not nav_success:
                result["error"] = "Failed to load page"
                result["logs"].append({"step": "navigate", "status": "failed"})
                return result
            
            result["logs"].append({"step": "navigate", "status": "success"})
            
            # Step 2: Take initial screenshot
            result["screenshot_path"] = await self.browser.take_screenshot(
                page, 
                f"submission_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            
            # Step 3: Detect form
            result["logs"].append({"step": "detect_form", "status": "started"})
            form_result = await self.browser.detect_form(page, directory_url)
            
            if not form_result.form_found:
                result["error"] = "No submission form found"
                result["logs"].append({"step": "detect_form", "status": "failed"})
                return result
            
            result["detected_fields"] = {
                "fields": [f.model_dump() for f in form_result.fields],
                "form_selector": form_result.form_selector,
                "submit_button": form_result.submit_button_selector,
                "confidence": form_result.confidence
            }
            result["logs"].append({"step": "detect_form", "status": "success"})
            
            # Step 4: Map SaaS data to form fields
            field_mapping = self.form_detector.map_saas_data_to_fields(
                form_result.fields,
                saas_data
            )
            
            # Add logo if provided and there's a file field
            if logo_path:
                for field in form_result.fields:
                    if field.field_type == "file":
                        field_mapping[field.selector] = {
                            "field_name": field.name,
                            "field_type": "file",
                            "value": logo_path
                        }
                        break
            
            # Step 5: Fill form
            result["logs"].append({"step": "fill_form", "status": "started"})
            
            if form_result.form_selector:
                await self.browser.scroll_to_form(page, form_result.form_selector)
            
            fill_results = await self.browser.fill_form(page, field_mapping)
            result["filled_fields"] = field_mapping
            result["logs"].append({
                "step": "fill_form", 
                "status": "success",
                "filled": sum(1 for v in fill_results.values() if v),
                "failed": sum(1 for v in fill_results.values() if not v)
            })
            
            # Check for CAPTCHA
            has_captcha = await self.browser.handle_captcha(page)
            if has_captcha:
                result["error"] = "CAPTCHA detected - requires manual intervention"
                result["logs"].append({"step": "captcha_check", "status": "blocked"})
                return result
            
            # Step 6: Submit form
            result["logs"].append({"step": "submit", "status": "started"})
            
            submit_selector = form_result.submit_button_selector
            if not submit_selector:
                submit_selector = await self.browser.find_submit_button(page)
            
            if not submit_selector:
                result["error"] = "Could not find submit button"
                result["logs"].append({"step": "submit", "status": "failed"})
                return result
            
            submit_success = await self.browser.click_submit(page, submit_selector)
            
            if not submit_success:
                result["error"] = "Failed to click submit button"
                result["logs"].append({"step": "submit", "status": "failed"})
                return result
            
            # Step 7: Check result
            await asyncio.sleep(3)
            submission_check = await self.browser.check_submission_success(page)
            
            # Take final screenshot
            final_screenshot = await self.browser.take_screenshot(
                page,
                f"result_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            )
            result["screenshot_path"] = final_screenshot
            
            if submission_check["success"] is True:
                result["success"] = True
                result["logs"].append({"step": "submit", "status": "success"})
            elif submission_check["success"] is False:
                result["error"] = submission_check["message"]
                result["logs"].append({"step": "submit", "status": "failed"})
            else:
                result["success"] = True  # Assume success if no errors
                result["logs"].append({
                    "step": "submit", 
                    "status": "unknown",
                    "note": "Could not confirm, assuming success"
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Submission failed: {e}")
            result["error"] = str(e)
            result["logs"].append({"step": "error", "message": str(e)})
            
            if page:
                try:
                    result["screenshot_path"] = await self.browser.take_screenshot(
                        page,
                        f"error_{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    )
                except:
                    pass
            
            return result
            
        finally:
            await self.browser.stop()
