# Memory Management

Jarvis AI stores long-term project and session memory in a local
[Chroma](https://www.trychroma.com/) vector database. Each combination of
project name and session identifier is maintained in a separate collection.
This prevents data leakage between unrelated workstreams while allowing fast
similarity search within a context.

## Usage

Memory is accessed through the `MemoryManager` interface:

- `add(project, session, text, metadata=None)` stores a text snippet with
  optional metadata.
- `query(project, session, text, top_k=5)` retrieves the most similar stored
  snippets for a given query text.

The default implementation (`ProjectMemory`) uses a lightweight hash-based
embedding function to avoid heavy model downloads. Embeddings and metadata are
persisted on disk under `data/project_memory`.

## Limits

- The memory store grows with each entry; periodically delete collections or
  clean the `data/project_memory` directory to reclaim space.
- Embeddings are deterministic but simplistic; they are intended for small
  projects and prototypes. For higher quality retrieval, replace the embedding
  function with a model-backed implementation.
- All data is kept locally; ensure the storage location is protected for
  sensitive projects.
