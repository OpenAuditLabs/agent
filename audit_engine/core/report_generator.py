"""
Audit Report Generator
Aggregates results from static and dynamic analysis, scores vulnerabilities, and outputs a comprehensive report.
"""
import json
from typing import List, Dict, Any

class AuditReportGenerator:
    def __init__(self):
        self.static_results = []
        self.dynamic_results = []
        self.scores = []
        self.metadata = {}

    def add_static_results(self, results: List[Dict[str, Any]]):
        self.static_results.extend(results)

    def add_dynamic_results(self, results: List[Dict[str, Any]]):
        self.dynamic_results.extend(results)

    def add_scores(self, scores: List[Dict[str, Any]]):
        self.scores.extend(scores)

    def set_metadata(self, metadata: Dict[str, Any]):
        self.metadata = metadata


