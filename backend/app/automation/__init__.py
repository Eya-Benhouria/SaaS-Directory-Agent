# Automation package
from .browser import BrowserAutomation, SubmissionExecutor
from .form_detector import FormDetectionService, RuleBasedFormDetector

__all__ = [
    'BrowserAutomation',
    'SubmissionExecutor',
    'FormDetectionService',
    'RuleBasedFormDetector'
]
