"""
Component Loader and Context Isolation for P11 Integration.

Provides isolated import management to prevent namespace collisions between
P8/P9 modules (vector-db/embeddings/rag) and P10 modules (llm), both of which
share generic names like config.py, models.py, and client.py.
"""

import sys
from pathlib import Path
from typing import Optional, Any, List

# Locate project directories
SRC_DIR = Path(__file__).resolve().parent
INTEGRATION_DIR = SRC_DIR.parent
AI_DIR = INTEGRATION_DIR.parent
PROJECT_ROOT = AI_DIR.parent

RAG_SRC_DIR = AI_DIR / "rag" / "src"
VECTOR_DB_DIR = AI_DIR / "vector-db"
EMBEDDINGS_DIR = AI_DIR / "embeddings"
LLM_SRC_DIR = AI_DIR / "llm" / "src"


class IsolatedContext:
    """
    Context manager that temporarily isolates sys.path and cleans conflicting
    generic module names from sys.modules during imports.
    """

    CONFLICTING_MODULES = [
        "config",
        "models",
        "client",
        "search",
        "database",
        "loader",
        "validator",
        "retriever",
        "result_processor",
        "context_builder",
        "query_builder",
        "rag_pipeline",
        "prompt_builder",
        "llm_pipeline",
    ]

    def __init__(self, target_dir: Path, related_dirs: Optional[List[Path]] = None):
        self.target_dir = Path(target_dir).resolve()
        self.related_dirs = [Path(d).resolve() for d in (related_dirs or [])]
        self.orig_path: List[str] = []
        self.orig_modules: dict = {}

    def __enter__(self):
        self.orig_path = list(sys.path)

        # Evict conflicting modules temporarily from sys.modules
        for mod_name in self.CONFLICTING_MODULES:
            if mod_name in sys.modules:
                self.orig_modules[mod_name] = sys.modules.pop(mod_name)

        # Prepend requested dirs to sys.path
        for d in reversed(self.related_dirs):
            sys.path.insert(0, str(d))
        sys.path.insert(0, str(self.target_dir))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Remove any modules imported during the isolated block
        for mod_name in self.CONFLICTING_MODULES:
            if mod_name in sys.modules:
                del sys.modules[mod_name]

        # Restore original modules
        for mod_name, mod in self.orig_modules.items():
            sys.modules[mod_name] = mod

        # Restore sys.path
        sys.path = self.orig_path


def load_rag_pipeline(
    top_k: int = 3,
    model: Optional[str] = None,
    base_url: Optional[str] = None
) -> Any:
    """
    Instantiate P9 RAGPipeline inside an isolated import context.
    """
    with IsolatedContext(RAG_SRC_DIR, [VECTOR_DB_DIR, EMBEDDINGS_DIR]):
        import rag_pipeline
        return rag_pipeline.RAGPipeline(
            top_k=top_k,
            model=model,
            base_url=base_url
        )


def load_llm_pipeline(
    model: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: Optional[float] = None,
    default_options: Optional[Any] = None
) -> Any:
    """
    Instantiate P10 LLMPipeline inside an isolated import context.
    """
    with IsolatedContext(LLM_SRC_DIR):
        import llm_pipeline
        return llm_pipeline.LLMPipeline(
            model=model,
            base_url=base_url,
            timeout=timeout,
            default_options=default_options
        )
