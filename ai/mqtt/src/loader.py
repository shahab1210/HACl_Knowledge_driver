"""
Component Loader and Context Isolation for P13 MQTT + AI Integration Layer.

Provides isolated import management to prevent namespace collisions across
generic module names (exceptions, config, models, client, validator, parser, engine, pipeline).
"""

import sys
from pathlib import Path
from typing import Optional, Any, List

# Locate project directories
SRC_DIR = Path(__file__).resolve().parent
MQTT_DIR = SRC_DIR.parent
AI_DIR = MQTT_DIR.parent

DIAGNOSIS_SRC_DIR = AI_DIR / "diagnosis" / "src"
INTEGRATION_SRC_DIR = AI_DIR / "integration" / "src"
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
        "parser",
        "retriever",
        "result_processor",
        "context_builder",
        "query_builder",
        "rag_pipeline",
        "prompt_builder",
        "llm_pipeline",
        "exceptions",
        "pipeline",
        "engine",
        "worker",
        "service"
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


def load_diagnosis_engine(**kwargs) -> Any:
    """
    Instantiate P12 DiagnosisEngine inside an isolated import context.
    """
    with IsolatedContext(
        DIAGNOSIS_SRC_DIR,
        [INTEGRATION_SRC_DIR, RAG_SRC_DIR, VECTOR_DB_DIR, EMBEDDINGS_DIR, LLM_SRC_DIR]
    ):
        import engine as diagnosis_engine_mod
        return diagnosis_engine_mod.DiagnosisEngine(**kwargs)
