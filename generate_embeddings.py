import json
import requests
from pathlib import Path

vault_path = Path(r"C:/the force")
index_path = vault_path / "05_Skills" / "search-index.json"

with open(index_path, "r", encoding="utf-8") as f:
    index = json.load(f)

# Try to use Ollama for embeddings
ollama_url = "http://localhost:11434/api/embeddings"
# Try common embedding models
embedding_models = ["nomic-embed-text", "mxbai-embed-large", "all-minilm", "qwen3:14b", "mistral-nemo:12B"]

working_model = None
for model in embedding_models:
    try:
        resp = requests.post(ollama_url, json={"model": model, "prompt": "test"}, timeout=10)
        if resp.status_code == 200:
            working_model = model
            print(f"Using embedding model: {model}")
            break
    except:
        continue

if not working_model:
    print("No embedding model available. Skipping vector embeddings.")
    # Add empty embeddings field
    for f in index["files"]:
        f["embedding"] = None
else:
    print(f"Generating embeddings with {working_model}...")
    for i, f in enumerate(index["files"]):
        # Read file content for embedding
        file_path = vault_path / f["path"]
        try:
            content = file_path.read_text(encoding="utf-8")
            # Use first 2000 chars for embedding
            text = content[:2000]
            resp = requests.post(ollama_url, json={"model": working_model, "prompt": text}, timeout=30)
            if resp.status_code == 200:
                f["embedding"] = resp.json()["embedding"]
            else:
                f["embedding"] = None
        except Exception as e:
            print(f"Error embedding {f['path']}: {e}")
            f["embedding"] = None
        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(index['files'])} files")

    index["embedding_model"] = working_model
    index["embedding_dim"] = len(index["files"][0]["embedding"]) if index["files"][0]["embedding"] else 0

# Write updated index
index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
print(f"Updated index with embeddings: {index_path}")