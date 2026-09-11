"""TrustLeash — forensic audits for AI coding agents."""

__version__ = "0.1.0"

from .analyzer import audit_session, AuditResult, RegisterSniff
from .verifier import ArtifactVerifier
from .report import render_markdown

try:
    from .gemini_adapter import audit_gemini
    _HAS_GEMINI = True
except ImportError:  # pragma: no cover
    _HAS_GEMINI = False

__all__ = [
    "audit_session",
    "AuditResult",
    "RegisterSniff",
    "ArtifactVerifier",
    "render_markdown",
]

if _HAS_GEMINI:
    __all__.append("audit_gemini")
