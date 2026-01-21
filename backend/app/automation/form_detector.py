"""
LLM-based Form Detection Service
Uses Vision LLM to analyze web pages and detect form fields
"""
import base64
import json
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
import httpx
from loguru import logger

from ..config import settings
from ..schemas import FormField, FormDetectionResult


class BaseLLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    async def analyze_form(self, screenshot_base64: str, page_html: str) -> Dict[str, Any]:
        """Analyze a page screenshot and HTML to detect form fields"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT-4 Vision provider"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model = settings.LLM_MODEL or "gpt-4o"
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    async def analyze_form(self, screenshot_base64: str, page_html: str) -> Dict[str, Any]:
        """Analyze form using GPT-4 Vision"""
        
        # Truncate HTML to avoid token limits
        truncated_html = page_html[:15000] if len(page_html) > 15000 else page_html
        
        prompt = self._build_prompt(truncated_html)
        
        messages = [
            {
                "role": "system",
                "content": """You are an expert web form analyzer. Your task is to identify submission forms on directory websites where SaaS products can be listed.

Analyze both the screenshot and HTML to find:
1. The main submission form (for adding a new product/tool/website)
2. All form fields with their types, labels, and CSS selectors
3. The submit button

Return a JSON object with this exact structure:
{
    "form_found": boolean,
    "form_selector": "CSS selector for the form element",
    "fields": [
        {
            "name": "field name/id",
            "field_type": "text|email|url|textarea|select|file|checkbox|radio",
            "label": "field label text",
            "placeholder": "placeholder text if any",
            "required": boolean,
            "selector": "CSS selector to locate this field",
            "options": ["option1", "option2"] // for select fields only
        }
    ],
    "submit_button_selector": "CSS selector for submit button",
    "confidence": 0.0-1.0
}"""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{screenshot_base64}",
                            "detail": "high"
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "max_tokens": 4096,
                    "temperature": 0.1
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                logger.error(f"OpenAI API error: {response.text}")
                raise Exception(f"OpenAI API error: {response.status_code}")
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Extract JSON from response
            return self._parse_response(content)
    
    def _build_prompt(self, html: str) -> str:
        return f"""Analyze this webpage screenshot and HTML to detect the SaaS/product submission form.

Look for:
- Forms for submitting a new tool, product, startup, or website
- Input fields for: name, URL, description, email, category, logo upload
- Submit/Add/Create buttons

HTML Content:
```html
{html}
```

Provide your analysis as a JSON object. Focus on finding the most relevant submission form, not login or search forms."""
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse the LLM response to extract JSON"""
        try:
            # Try to find JSON in the response
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0]
            else:
                json_str = content
            
            return json.loads(json_str.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return {
                "form_found": False,
                "fields": [],
                "confidence": 0.0,
                "error": "Failed to parse LLM response"
            }


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude Vision provider"""
    
    def __init__(self):
        self.api_key = settings.ANTHROPIC_API_KEY
        self.model = "claude-3-5-sonnet-20241022"
        self.base_url = "https://api.anthropic.com/v1/messages"
    
    async def analyze_form(self, screenshot_base64: str, page_html: str) -> Dict[str, Any]:
        """Analyze form using Claude Vision"""
        
        truncated_html = page_html[:15000] if len(page_html) > 15000 else page_html
        
        prompt = f"""Analyze this webpage screenshot and HTML to detect the SaaS/product submission form.

Look for:
- Forms for submitting a new tool, product, startup, or website
- Input fields for: name, URL, description, email, category, logo upload
- Submit/Add/Create buttons

HTML Content:
```html
{truncated_html}
```

Return a JSON object with this structure:
{{
    "form_found": boolean,
    "form_selector": "CSS selector for the form element",
    "fields": [
        {{
            "name": "field name/id",
            "field_type": "text|email|url|textarea|select|file|checkbox|radio",
            "label": "field label text",
            "placeholder": "placeholder text if any",
            "required": boolean,
            "selector": "CSS selector to locate this field",
            "options": ["option1", "option2"]
        }}
    ],
    "submit_button_selector": "CSS selector for submit button",
    "confidence": 0.0-1.0
}}

Focus on finding the most relevant submission form, not login or search forms."""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": self.model,
                    "max_tokens": 4096,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": "image/png",
                                        "data": screenshot_base64
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": prompt
                                }
                            ]
                        }
                    ]
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                logger.error(f"Anthropic API error: {response.text}")
                raise Exception(f"Anthropic API error: {response.status_code}")
            
            result = response.json()
            content = result["content"][0]["text"]
            
            return self._parse_response(content)
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse the LLM response to extract JSON"""
        try:
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0]
            else:
                json_str = content
            
            return json.loads(json_str.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return {
                "form_found": False,
                "fields": [],
                "confidence": 0.0,
                "error": "Failed to parse LLM response"
            }


class GeminiProvider(BaseLLMProvider):
    """Google Gemini Vision provider - FREE tier available!"""
    
    def __init__(self):
        self.api_key = settings.GOOGLE_API_KEY
        # Use settings.LLM_MODEL if specified, otherwise default to gemini-2.0-flash
        self.model = settings.LLM_MODEL if settings.LLM_MODEL and settings.LLM_MODEL.startswith("gemini") else "gemini-2.0-flash"
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
    
    async def analyze_form(self, screenshot_base64: str, page_html: str) -> Dict[str, Any]:
        """Analyze form using Gemini Vision"""
        
        truncated_html = page_html[:15000] if len(page_html) > 15000 else page_html
        
        prompt = f"""Analyze this webpage screenshot and HTML to detect the SaaS/product submission form.

Look for:
- Forms for submitting a new tool, product, startup, or website
- Input fields for: name, URL, description, email, category, logo upload
- Submit/Add/Create buttons

HTML Content:
```html
{truncated_html}
```

Return ONLY a valid JSON object with this exact structure (no markdown, no explanation):
{{
    "form_found": true or false,
    "form_selector": "CSS selector for the form element",
    "fields": [
        {{
            "name": "field name/id",
            "field_type": "text|email|url|textarea|select|file|checkbox|radio",
            "label": "field label text",
            "placeholder": "placeholder text if any",
            "required": true or false,
            "selector": "CSS selector to locate this field",
            "options": null
        }}
    ],
    "submit_button_selector": "CSS selector for submit button",
    "confidence": 0.0 to 1.0
}}

Focus on finding the most relevant submission form, not login or search forms."""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}?key={self.api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [
                        {
                            "parts": [
                                {
                                    "inline_data": {
                                        "mime_type": "image/png",
                                        "data": screenshot_base64
                                    }
                                },
                                {"text": prompt}
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.1,
                        "maxOutputTokens": 4096
                    }
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                logger.error(f"Gemini API error: {response.text}")
                raise Exception(f"Gemini API error: {response.status_code}")
            
            result = response.json()
            content = result["candidates"][0]["content"]["parts"][0]["text"]
            
            return self._parse_response(content)
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse the LLM response to extract JSON"""
        try:
            # Clean the response
            content = content.strip()
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0]
            else:
                json_str = content
            
            return json.loads(json_str.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response: {e}")
            return {
                "form_found": False,
                "fields": [],
                "confidence": 0.0,
                "error": "Failed to parse LLM response"
            }


class GroqProvider(BaseLLMProvider):
    """Groq provider - FREE tier with fast inference!"""
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = "llama-3.2-90b-vision-preview"  # Vision model
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    async def analyze_form(self, screenshot_base64: str, page_html: str) -> Dict[str, Any]:
        """Analyze form using Groq's vision model"""
        
        truncated_html = page_html[:10000] if len(page_html) > 10000 else page_html
        
        prompt = f"""Analyze this webpage to detect the SaaS/product submission form.

HTML Content:
```html
{truncated_html}
```

Return ONLY a valid JSON object with this structure:
{{
    "form_found": true or false,
    "form_selector": "CSS selector for the form",
    "fields": [
        {{
            "name": "field name",
            "field_type": "text|email|url|textarea|select|file",
            "label": "label text",
            "placeholder": "placeholder",
            "required": true or false,
            "selector": "CSS selector",
            "options": null
        }}
    ],
    "submit_button_selector": "CSS selector for submit",
    "confidence": 0.0 to 1.0
}}"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{screenshot_base64}"
                                    }
                                },
                                {"type": "text", "text": prompt}
                            ]
                        }
                    ],
                    "max_tokens": 4096,
                    "temperature": 0.1
                },
                timeout=60.0
            )
            
            if response.status_code != 200:
                logger.error(f"Groq API error: {response.text}")
                raise Exception(f"Groq API error: {response.status_code}")
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            return self._parse_response(content)
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse the LLM response to extract JSON"""
        try:
            content = content.strip()
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0]
            else:
                json_str = content
            
            return json.loads(json_str.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Groq response: {e}")
            return {
                "form_found": False,
                "fields": [],
                "confidence": 0.0,
                "error": "Failed to parse LLM response"
            }


class FormDetectionService:
    """Service for detecting forms on web pages using LLM"""
    
    def __init__(self):
        # Priority: Gemini (free) > Groq (free) > Anthropic > OpenAI
        if settings.LLM_PROVIDER == "gemini" and settings.GOOGLE_API_KEY:
            self.provider = GeminiProvider()
        elif settings.LLM_PROVIDER == "groq" and settings.GROQ_API_KEY:
            self.provider = GroqProvider()
        elif settings.LLM_PROVIDER == "anthropic" and settings.ANTHROPIC_API_KEY:
            self.provider = AnthropicProvider()
        elif settings.OPENAI_API_KEY:
            self.provider = OpenAIProvider()
        elif settings.GOOGLE_API_KEY:
            # Fallback to Gemini if available
            self.provider = GeminiProvider()
        elif settings.GROQ_API_KEY:
            # Fallback to Groq if available
            self.provider = GroqProvider()
        else:
            self.provider = OpenAIProvider()
    
    async def detect_form(
        self,
        screenshot_base64: str,
        page_html: str,
        url: str
    ) -> FormDetectionResult:
        """Detect form fields on a web page"""
        try:
            logger.info(f"Analyzing form on: {url}")
            
            result = await self.provider.analyze_form(screenshot_base64, page_html)
            
            # Parse fields
            fields = []
            for field_data in result.get("fields", []):
                fields.append(FormField(
                    name=field_data.get("name", ""),
                    field_type=field_data.get("field_type", "text"),
                    label=field_data.get("label"),
                    placeholder=field_data.get("placeholder"),
                    required=field_data.get("required", False),
                    selector=field_data.get("selector", ""),
                    options=field_data.get("options")
                ))
            
            return FormDetectionResult(
                url=url,
                form_found=result.get("form_found", False),
                form_selector=result.get("form_selector"),
                fields=fields,
                submit_button_selector=result.get("submit_button_selector"),
                confidence=result.get("confidence", 0.0)
            )
            
        except Exception as e:
            logger.error(f"Form detection failed for {url}: {e}")
            return FormDetectionResult(
                url=url,
                form_found=False,
                fields=[],
                confidence=0.0
            )
    
    def map_saas_data_to_fields(
        self,
        fields: List[FormField],
        saas_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Map SaaS product data to detected form fields"""
        
        # Field type to SaaS data mapping
        field_mapping = {
            # Name fields
            "name": ["name", "saas_name", "product_name", "title", "tool_name", "startup_name"],
            "product_name": ["name", "saas_name"],
            "tool_name": ["name"],
            "startup_name": ["name"],
            "title": ["name", "tagline"],
            
            # URL fields  
            "url": ["website_url", "url", "website", "link", "homepage"],
            "website": ["website_url"],
            "website_url": ["website_url"],
            "link": ["website_url"],
            "homepage": ["website_url"],
            
            # Description fields
            "description": ["short_description", "long_description", "tagline"],
            "short_description": ["short_description", "tagline"],
            "long_description": ["long_description", "short_description"],
            "tagline": ["tagline", "short_description"],
            "summary": ["short_description"],
            "about": ["long_description", "short_description"],
            
            # Email fields
            "email": ["contact_email"],
            "contact_email": ["contact_email"],
            "contact": ["contact_email"],
            
            # Category fields
            "category": ["category"],
            "categories": ["category"],
            "type": ["category"],
            
            # Pricing fields
            "pricing": ["pricing_model", "pricing_details"],
            "price": ["pricing_model"],
            "pricing_model": ["pricing_model"],
            
            # Social fields
            "twitter": ["twitter_url"],
            "twitter_url": ["twitter_url"],
            "linkedin": ["linkedin_url"],
            "github": ["github_url"],
        }
        
        filled_fields = {}
        
        for field in fields:
            field_name_lower = field.name.lower().replace("-", "_").replace(" ", "_")
            label_lower = (field.label or "").lower().replace("-", "_").replace(" ", "_")
            
            # Try to match field by name or label
            matched_value = None
            
            for key, saas_keys in field_mapping.items():
                if key in field_name_lower or key in label_lower:
                    for saas_key in saas_keys:
                        if saas_key in saas_data and saas_data[saas_key]:
                            matched_value = saas_data[saas_key]
                            break
                    if matched_value:
                        break
            
            if matched_value:
                filled_fields[field.selector] = {
                    "field_name": field.name,
                    "field_type": field.field_type,
                    "value": matched_value
                }
        
        return filled_fields


# Fallback rule-based form detection for simple cases
class RuleBasedFormDetector:
    """Simple rule-based form detector as fallback"""
    
    COMMON_FORM_SELECTORS = [
        "form[action*='submit']",
        "form[action*='add']",
        "form[action*='create']",
        "form[id*='submit']",
        "form[class*='submit']",
        "form[class*='listing']",
        ".submit-form",
        ".submission-form",
        "#submit-form",
        "#listing-form",
    ]
    
    FIELD_PATTERNS = {
        "name": ["name", "title", "product", "tool", "startup"],
        "url": ["url", "website", "link", "homepage", "site"],
        "email": ["email", "mail", "contact"],
        "description": ["description", "about", "summary", "intro", "details"],
        "category": ["category", "categories", "type", "industry"],
        "logo": ["logo", "image", "icon", "avatar", "picture"],
        "tags": ["tags", "keywords", "labels"],
    }
    
    def detect_fields_from_html(self, html: str) -> List[FormField]:
        """Detect form fields from HTML using pattern matching"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'lxml')
        fields = []
        
        # Find all input, textarea, and select elements
        for element in soup.find_all(['input', 'textarea', 'select']):
            field_type = element.get('type', 'text')
            if element.name == 'textarea':
                field_type = 'textarea'
            elif element.name == 'select':
                field_type = 'select'
            
            name = element.get('name', '') or element.get('id', '')
            placeholder = element.get('placeholder', '')
            
            # Find label
            label = None
            if element.get('id'):
                label_elem = soup.find('label', {'for': element.get('id')})
                if label_elem:
                    label = label_elem.get_text(strip=True)
            
            # Build selector
            if element.get('id'):
                selector = f"#{element.get('id')}"
            elif element.get('name'):
                selector = f"[name='{element.get('name')}']"
            else:
                continue
            
            # Determine if required
            required = element.get('required') is not None
            
            fields.append(FormField(
                name=name,
                field_type=field_type,
                label=label,
                placeholder=placeholder,
                required=required,
                selector=selector
            ))
        
        return fields
