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

    def generate_report(self) -> Dict[str, Any]:
        report = {
            "metadata": self.metadata,
            "static_analysis": self.static_results,
            "dynamic_analysis": self.dynamic_results,
            "scores": self.scores,
        }
        return report

    def export_report(self, output_format: str = "json") -> str:
        report = self.generate_report()
        if output_format == "json":
            return json.dumps(report, indent=2)
        elif output_format == "markdown":
            return self._to_markdown(report)
        elif output_format == "html":
            return self._to_html(report)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    def _to_markdown(self, report: Dict[str, Any]) -> str:
        md = "# Audit Report\n"
        if report.get("metadata"):
            md += "## Metadata\n"
            for k, v in report["metadata"].items():
                md += f"- **{k}**: {v}\n"
        md += "\n## Static Analysis Findings\n"
        for finding in report["static_analysis"]:
            md += f"- {finding}\n"
        md += "\n## Dynamic Analysis Findings\n"
        for finding in report["dynamic_analysis"]:
            md += f"- {finding}\n"
        md += "\n## Scoring\n"
        for score in report["scores"]:
            md += f"- {score}\n"
        return md

    def _to_html(self, report: Dict[str, Any]) -> str:
        html = ["<html><head><title>Audit Report</title></head><body>"]
        html.append("<h1>Audit Report</h1>")
        if report.get("metadata"):
            html.append("<h2>Metadata</h2><ul>")
            for k, v in report["metadata"].items():
                html.append(f"<li><strong>{k}</strong>: {v}</li>")
            html.append("</ul>")
        html.append("<h2>Static Analysis Findings</h2><ul>")
        for finding in report["static_analysis"]:
            html.append(f"<li>{finding}</li>")
        html.append("</ul>")
        html.append("<h2>Dynamic Analysis Findings</h2><ul>")
        for finding in report["dynamic_analysis"]:
            html.append(f"<li>{finding}</li>")
        html.append("</ul>")
        html.append("<h2>Scoring</h2><ul>")
        for score in report["scores"]:
            html.append(f"<li>{score}</li>")
        html.append("</ul>")
        html.append("</body></html>")
        return "".join(html)
