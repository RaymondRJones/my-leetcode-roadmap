"""
Assessment service for loading quiz data.
"""
import json
import os
from typing import Dict, Optional


class AssessmentService:
    """Service class for loading assessment quiz data."""

    _python_assessment: Optional[Dict] = None
    _java_assessment: Optional[Dict] = None

    @classmethod
    def _load_json(cls, filename: str) -> Dict:
        """Load a JSON file from the data directory."""
        filepath = os.path.join('data', filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    @classmethod
    def get_python_assessment(cls) -> Dict:
        """Get Python assessment quiz data."""
        if cls._python_assessment is None:
            cls._python_assessment = cls._load_json('python_assessment.json')
        return cls._python_assessment

    @classmethod
    def get_java_assessment(cls) -> Dict:
        """Get Java assessment quiz data."""
        if cls._java_assessment is None:
            cls._java_assessment = cls._load_json('java_assessment.json')
        return cls._java_assessment

    @classmethod
    def get_assessment(cls, language: str) -> Dict:
        """Get assessment quiz data by language."""
        if language == 'python':
            return cls.get_python_assessment()
        elif language == 'java':
            return cls.get_java_assessment()
        return {}

    @classmethod
    def clear_cache(cls):
        """Clear cached assessment data."""
        cls._python_assessment = None
        cls._java_assessment = None
