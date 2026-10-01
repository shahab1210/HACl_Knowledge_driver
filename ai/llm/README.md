# P10 — Local LLM / Ollama Generation Layer

The **P10 Local LLM Generation Layer** provides a clean, modular, and local-first generation pipeline for the **Knowledge-Driven IoT Fault Diagnosis Assistant**. It consumes retrieved RAG context (produced by P9) and telemetry symptoms to produce grounded, natural-language fault explanations using local Ollama models.

---

## Architecture

```
                                  Telemetry Query / Symptoms
                                             ↓
+-----------------------+         +-----------------------+
|  P9 RAG Context       |  --->   |   P10 Prompt Builder  |
|  (Retrieved Chunks)   |         |   (Rules & Citation)  |
+-----------------------+         +-----------------------+
                                             ↓
                                  Controlled Unified Prompt
                                             ↓
                                  +-----------------------+
                                  |   LocalLLMClient      |
                                  |   (/api/generate)     |
                                  +-----------------------+
                                             ↓
                                  +-----------------------+
                                  |   Local Ollama Server |
                                  |   (e.g., llama3.2:3b) |
                                  +-----------------------+
                                             ↓
                                  +-----------------------+
                                  |  LLMPipelineOutput    |
                                  |  (Fault Explanation)  |
                                  +-----------------------+
```

---

## Key Features

1. **Local-Only AI Infrastructure**:
   - Zero reliance on cloud APIs (OpenAI, Gemini, Anthropic).
   - Direct HTTP communication with local Ollama (`/api/generate`, `/api/chat`, `/api/tags`, `/api/version`).
   - Automatic fallback between `requests` and Python standard library `urllib`.

2. **Strict Grounding & Anti-Hallucination Directives**:
   - **Grounding**: Diagnosis is strictly constrained to the retrieved Knowledge Base context.
   - **No Hallucination**: Model is explicitly forbidden from inventing unsupported technical facts or thresholds.
   - **Source Citation**: Model is instructed to cite specific Knowledge Sources and Document IDs (e.g., `FAULT-003: Motor Overheating`).
   - **Knowledge vs Hypotheses**: Differentiates verified knowledge base facts from assumptions.
   - **Insufficient Context Handling**: Explicitly declares when the retrieved context is insufficient and specifies what additional sensor telemetry or inspection procedures are needed.
   - **Calibrated Certainty**: Avoids claiming 100% certainty when symptoms overlap multiple fault modes.

3. **Robust Model Inspection & Safety Guards**:
   - Prevents using embedding models (e.g., `nomic-embed-text`) for text generation, raising a descriptive `OllamaModelTypeError`.
   - Validates model availability, raising an `OllamaModelNotFoundError` with the exact pull command if missing.
   - Comprehensive exception hierarchy (`OllamaConnectionError`, `OllamaModelNotFoundError`, `OllamaModelTypeError`, `OllamaResponseError`, `LLMValidationError`).

4. **Structured Pipeline & Extensibility**:
   - Accepts plain string contexts, structured result lists, or complete P9 RAG output dictionaries.
   - Returns structured `LLMPipelineOutput` containing the query, context, prompt, generated response, model name, and generation telemetry (token count, duration).

---

## Directory Structure

```
ai/llm/
├── src/
│   ├── __init__.py           # Package exports
│   ├── config.py             # Hyperparameters, endpoints, and default prompts
│   ├── models.py             # Data classes & exception hierarchy
│   ├── prompt_builder.py     # Prompt formatting & safety constraints
│   ├── client.py             # Ollama HTTP client & readiness checks
│   └── llm_pipeline.py       # Generation orchestrator
├── tests/
│   ├── test_prompt_builder.py
│   ├── test_client.py
│   ├── test_llm_pipeline.py
│   └── test_models.py
├── cli.py                    # Command-line interface
├── requirements.txt          # Python dependencies
└── README.md                 # Documentation
```

---

## Configuration & Environment Variables

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama HTTP server endpoint |
| `LLM_MODEL` | `llama3.2:3b` | Default generative model |
| `LLM_TIMEOUT` | `120.0` | Inference request timeout (seconds) |
| `LLM_TEMPERATURE` | `0.2` | Sampling temperature (low for factual diagnosis) |
| `LLM_MAX_TOKENS` | `1024` | Maximum response tokens (`num_predict`) |
| `LLM_TOP_P` | `0.9` | Top-p nucleus sampling |
| `LLM_TOP_K` | `40` | Top-k sampling limit |

---

## Ollama Generative Model Setup

P10 requires a **generative LLM** installed in Ollama. 

> [!NOTE]
> `nomic-embed-text` is the embedding model used in P7/P8 and **cannot** be used for text generation.

### Recommended Generative Models for macOS:
- **Llama 3.2 3B** (Recommended for balanced speed & reasoning):
  ```bash
  ollama pull llama3.2:3b
  ```
- **Llama 3.2 1B** (Ultra-lightweight / fast):
  ```bash
  ollama pull llama3.2:1b
  ```
- **Qwen 2.5 3B / 7B** (Excellent technical instruction following):
  ```bash
  ollama pull qwen2.5:3b
  ```
- **Mistral 7B**:
  ```bash
  ollama pull mistral:7b
  ```

---

## CLI Usage

The P10 CLI provides commands to inspect Ollama status, preview constructed prompts, and run inference.

### 1. Check Ollama Status & Model Readiness
```bash
python3 ai/llm/cli.py status
```
*Example output:*
```text
========================================
P10 Local LLM: Service & Model Status
========================================
Ollama Endpoint: http://localhost:11434
Target LLM Model: llama3.2:3b
----------------------------------------
✅ Server Status: RUNNING & REACHABLE

Installed Models (1):
  📦 nomic-embed-text:latest   [  261.6 MB] -> Embedding Model (P7/P8)
----------------------------------------
Model Readiness Check for P10:
⚠️ Model Not Found: Generative model 'llama3.2:3b' is not installed in local Ollama.
   To install, run: ollama pull llama3.2:3b
========================================
```

### 2. Preview Constructed Prompt
```bash
python3 ai/llm/cli.py prompt \
  --query "Motor temperature is 95C and vibration is 7.2 mm/s." \
  --context "Knowledge Source 1\nTitle: Motor Overheating\nDocument ID: FAULT-003"
```

### 3. Generate Fault Explanation
```bash
python3 ai/llm/cli.py generate \
  --query "The motor temperature is very high and the vibration is excessive." \
  --context "Knowledge Source 1: Motor Overheating (FAULT-003)..." \
  --model llama3.2:3b
```

### 4. End-to-End Generation with P9 RAG Integration
```bash
python3 ai/llm/cli.py generate \
  --query "The motor temperature is very high and the vibration is excessive." \
  --use-rag \
  --top-k 3 \
  --model llama3.2:3b
```

---

## Python API Usage

```python
from llm.src import LLMPipeline, LocalLLMClient, PromptBuilder, GenerationOptions

# 1. Initialize client and pipeline
client = LocalLLMClient(model="llama3.2:3b", base_url="http://localhost:11434")
pipeline = LLMPipeline(client=client)

# 2. Generate diagnosis from query and context
rag_context = (
    "Knowledge Source 1\n"
    "Title: Motor Overheating\n"
    "Document ID: FAULT-003\n"
    "Source: faults/motor-overheating.md\n"
    "Similarity: 0.8920\n\n"
    "Motor overheating occurs when winding temperatures exceed 80C."
)

output = pipeline.generate(
    query="The motor temperature is 95C and vibration is high.",
    context=rag_context,
    options=GenerationOptions(temperature=0.2, num_predict=512)
)

print("Diagnosis:", output.response)
print("Model:", output.model)
```

---

## Running Unit Tests

All P10 unit tests are isolated and mock network interactions, meaning they pass 100% offline without requiring a running Ollama server or downloaded model:

```bash
pytest ai/llm/tests/ -v
```

*Test Results:*
```text
============================== 47 passed in 0.38s ==============================
```
