"""Filesystem verification of artifact claims."""

from __future__ import annotations

from pathlib import Path


class ArtifactVerifier:
    """Checks claimed artifact paths against the real filesystem."""

    def __init__(self, root: str | Path = "."):
        self.root = Path(root).resolve()

    def verify(self, claimed: list[str]) -> tuple[list[str], list[str]]:
        """Return (verified, phantom) lists."""
        verified, phantom = [], []
        for rel in claimed:
            candidate = self.root / rel
            # also accept absolute paths that live inside root
            p = Path(rel)
            if p.is_absolute() and p.exists():
                verified.append(rel)
            elif candidate.exists():
                verified.append(rel)
            else:
                phantom.append(rel)
        return verified, phantom
