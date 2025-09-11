"""
Audit Report Generator
Aggregates results from static and dynamic analysis, scores vulnerabilities, and outputs a comprehensive report.
"""
import json
from typing import List, Dict, Any

class AuditReportGenerator:
    def _get_summary_statistics(self, report: Dict[str, Any]) -> Dict[str, Any]:
        summary = {}
        static_findings = report.get("static_analysis", [])
        dynamic_findings = report.get("dynamic_analysis", [])
        all_findings = static_findings + dynamic_findings
        summary["total_findings"] = len(all_findings)
        # Severity breakdown
        severity_count = {}
        for finding in all_findings:
            severity = finding.get("severity", "Unknown") if isinstance(finding, dict) else "Unknown"
            severity_count[severity] = severity_count.get(severity, 0) + 1
        summary["severity_breakdown"] = severity_count
        return summary
    import datetime

    def __init__(self, auditor_name: str = None, contract_name: str = None):
        self.static_results = []
        self.dynamic_results = []
        self.scores = []
        self.metadata = {}
        self.audit_timestamp = self._get_current_timestamp()
        self.auditor_name = auditor_name
        self.contract_name = contract_name

    def _get_current_timestamp(self):
        return self.datetime.datetime.now().isoformat()

    def add_static_results(self, results: List[Dict[str, Any]]):
        self.static_results.extend(results)

    def add_dynamic_results(self, results: List[Dict[str, Any]]):
        self.dynamic_results.extend(results)

    def add_scores(self, scores: List[Dict[str, Any]]):
        self.scores.extend(scores)

    def set_metadata(self, metadata: Dict[str, Any]):
        self.metadata = metadata
        # Optionally update auditor and contract name from metadata
        if 'auditor_name' in metadata:
            self.auditor_name = metadata['auditor_name']
        if 'contract_name' in metadata:
            self.contract_name = metadata['contract_name']

    def generate_report(self) -> Dict[str, Any]:
        report = {
            "metadata": self.metadata,
            "audit_timestamp": self.audit_timestamp,
            "auditor_name": self.auditor_name,
            "contract_name": self.contract_name,
            "static_analysis": self.static_results,
            "dynamic_analysis": self.dynamic_results,
            "scores": self.scores,
        }
        report["summary_statistics"] = self._get_summary_statistics(report)
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
        md += f"- **Timestamp**: {report.get('audit_timestamp', '')}\n"
        md += f"- **Auditor Name**: {report.get('auditor_name', '')}\n"
        md += f"- **Contract Name**: {report.get('contract_name', '')}\n"
        if report.get("metadata"):
            md += "## Metadata\n"
            for k, v in report["metadata"].items():
                md += f"- **{k}**: {v}\n"
        if report.get("summary_statistics"):
            md += "\n## Summary Statistics\n"
            md += f"- Total Findings: {report['summary_statistics'].get('total_findings', 0)}\n"
            md += "- Severity Breakdown:\n"
            for sev, count in report['summary_statistics'].get('severity_breakdown', {}).items():
                md += f"  - {sev}: {count}\n"
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
        html.append(f"<p><strong>Timestamp:</strong> {report.get('audit_timestamp', '')}</p>")
        html.append(f"<p><strong>Auditor Name:</strong> {report.get('auditor_name', '')}</p>")
        html.append(f"<p><strong>Contract Name:</strong> {report.get('contract_name', '')}</p>")
        if report.get("metadata"):
            html.append("<h2>Metadata</h2><ul>")
            for k, v in report["metadata"].items():
                html.append(f"<li><strong>{k}</strong>: {v}</li>")
            html.append("</ul>")
        if report.get("summary_statistics"):
            html.append("<h2>Summary Statistics</h2><ul>")
            html.append(f"<li>Total Findings: {report['summary_statistics'].get('total_findings', 0)}</li>")
            html.append("<li>Severity Breakdown:<ul>")
            for sev, count in report['summary_statistics'].get('severity_breakdown', {}).items():
                html.append(f"<li>{sev}: {count}</li>")
            html.append("</ul></li></ul>")
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
