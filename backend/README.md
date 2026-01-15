# Pipeline Parser Backend

A FastAPI-based backend service that analyzes pipeline graph structures, determining node/edge counts and validating whether the pipeline forms a Directed Acyclic Graph (DAG).

## Overview

This backend provides an API for parsing and analyzing pipeline data structures commonly used in workflow systems, data pipelines, and node-based editors. It accepts graph data (nodes and edges) and returns structural analysis.

## Dependencies

- **FastAPI**: Modern, high-performance web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **uvicorn**: ASGI server (for running the application)

## Installation

```bash
pip install fastapi pydantic uvicorn
```

## Running the Server

```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

---

## API Endpoints

### 1. Health Check

**Endpoint:** `GET /`

**Description:** Simple ping endpoint to verify the server is running.

**Response:**
```json
{
  "Ping": "Pong"
}
```

---

### 2. Parse Pipeline

**Endpoint:** `POST /pipelines/parse`

**Description:** Analyzes pipeline graph data and returns structural information.

**Request Body:**
```json
{
  "nodes": [
    { "id": "node1", ... },
    { "id": "node2", ... }
  ],
  "edges": [
    { "source": "node1", "target": "node2" },
    ...
  ]
}
```

**Response:**
```json
{
  "num_nodes": 2,
  "num_edges": 1,
  "is_dag": true
}
```

---

## Code Structure

### Data Model

```python
class PipelineData(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
```

- **nodes**: List of node objects, each must have an `id` field
- **edges**: List of edge objects with `source` and `target` fields

---

## DAG Detection Algorithm

The `is_dag()` function determines whether the pipeline graph is a **Directed Acyclic Graph** using Depth-First Search (DFS) with the **three-color marking** technique.

### Three-Color States

| Color | Value | Meaning |
|-------|-------|---------|
| WHITE | 0 | Node has not been visited |
| GRAY | 1 | Node is currently being processed (in current DFS path) |
| BLACK | 2 | Node and all its descendants have been fully processed |

### Algorithm Flow

```
1. Build adjacency list from edges
2. Initialize all nodes as WHITE (unvisited)
3. For each unvisited node:
   a. Mark node as GRAY (currently visiting)
   b. Recursively visit all neighbors
   c. If a GRAY neighbor is encountered → CYCLE DETECTED (not a DAG)
   d. If a WHITE neighbor is encountered → continue DFS
   e. Mark node as BLACK when all neighbors processed
4. If no cycles found → Graph is a DAG
```

### Why Three Colors?

- **Detecting Back Edges**: A back edge (edge to an ancestor in the DFS tree) indicates a cycle. When we encounter a GRAY node, it means we've found a path back to a node we're currently processing.
- **Avoiding Redundant Work**: BLACK nodes are fully processed, so we don't need to revisit them.
- **Handling Disconnected Components**: By iterating through all WHITE nodes, the algorithm correctly handles graphs with multiple disconnected components.

### Visual Example

```
Valid DAG:          Invalid (has cycle):
A → B → C           A → B → C
    ↓                   ↓   ↓
    D                   D → E
                            ↓
                        (back to B)
```

---

## CORS Configuration

The middleware allows cross-origin requests from the frontend:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This enables the React frontend (running on port 3000) to communicate with this backend.

---

## Example Usage

### Using cURL

```bash
# Health check
curl http://localhost:8000/

# Parse a simple pipeline
curl -X POST http://localhost:8000/pipelines/parse \
  -H "Content-Type: application/json" \
  -d '{
    "nodes": [
      {"id": "input1"},
      {"id": "process1"},
      {"id": "output1"}
    ],
    "edges": [
      {"source": "input1", "target": "process1"},
      {"source": "process1", "target": "output1"}
    ]
  }'
```

### Expected Response

```json
{
  "num_nodes": 3,
  "num_edges": 2,
  "is_dag": true
}
```

---

## API Documentation

FastAPI auto-generates interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
