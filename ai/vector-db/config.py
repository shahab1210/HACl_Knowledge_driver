"""
Configuration settings for P8 Vector Database.
Centralizes paths, collection settings, distance metric, and service URLs with environment variable overrides.
"""

import os
from pathlib import Path

# Base directories
MODULE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_DIR.parent.parent

# ChromaDB persistence directory
DEFAULT_CHROMA_PATH = str(MODULE_DIR / "data" / "chroma")
CHROMA_PATH = os.getenv("CHROMA_PATH", DEFAULT_CHROMA_PATH)

# ChromaDB collection settings
DEFAULT_COLLECTION_NAME = "iot_fault_knowledge"
COLLECTION_NAME = os.getenv("COLLECTION_NAME", DEFAULT_COLLECTION_NAME)

# Source embeddings artifact from P7
DEFAULT_EMBEDDINGS_FILE = str(PROJECT_ROOT / "ai" / "embeddings" / "output" / "embeddings.json")
EMBEDDINGS_FILE = os.getenv("EMBEDDINGS_FILE", DEFAULT_EMBEDDINGS_FILE)

# Vector distance metric: "cosine", "l2", or "ip"
# In ChromaDB, hnsw:space can be 'cosine', 'l2', or 'ip'.
# Cosine distance = 1 - cosine_similarity (range: 0.0 to 2.0).
DEFAULT_DISTANCE_METRIC = "cosine"
DISTANCE_METRIC = os.getenv("DISTANCE_METRIC", DEFAULT_DISTANCE_METRIC)

# Ollama configuration for query embedding
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)

DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)

DEFAULT_TOP_K = 5
