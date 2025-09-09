from pathlib import Path
from typing import Iterable, List


class ContractFileHandler:
    SUPPORTED_EXTENSIONS = {".sol"}

    def is_supported_contract(self, path: Path) -> bool:
        return path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    def collect_contracts(self, base: Path) -> List[str]:
        if base.is_file() and self.is_supported_contract(base):
            return [str(base.resolve())]
        results: List[str] = []
        for p in base.rglob("*"):
            if p.is_file() and self.is_supported_contract(p):
                results.append(str(p.resolve()))
        return results



