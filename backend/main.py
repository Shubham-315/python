from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from collections import defaultdict

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PipelineData(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]


def is_dag(nodes: List[Dict], edges: List[Dict]) -> bool:
    """
    Check if the graph is a Directed Acyclic Graph (DAG) using DFS.
    Uses three-color marking: WHITE (0), GRAY (1), BLACK (2)
    - WHITE: unvisited
    - GRAY: currently in DFS path (visiting)
    - BLACK: fully processed
    A cycle exists if we encounter a GRAY node during traversal.
    """
    # Build adjacency list
    graph = defaultdict(list)
    node_ids = set()

    for node in nodes:
        node_ids.add(node["id"])

    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source and target:
            graph[source].append(target)
            node_ids.add(source)
            node_ids.add(target)

    # Color states
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node_id: WHITE for node_id in node_ids}

    def dfs(node: str) -> bool:
        """Returns True if cycle detected, False otherwise"""
        color[node] = GRAY

        for neighbor in graph[node]:
            if neighbor not in color:
                continue
            if color[neighbor] == GRAY:
                # Found a back edge - cycle detected
                return True
            if color[neighbor] == WHITE:
                if dfs(neighbor):
                    return True

        color[node] = BLACK
        return False

    # Check all nodes (handles disconnected components)
    for node_id in node_ids:
        if color[node_id] == WHITE:
            if dfs(node_id):
                return False  # Cycle found, not a DAG

    return True  # No cycles, is a DAG


@app.get('/')
def read_root():
    return {'Ping': 'Pong'}


@app.post('/pipelines/parse')
def parse_pipeline(pipeline: PipelineData):
    """
    Parse pipeline data and return analysis:
    - num_nodes: count of nodes
    - num_edges: count of edges
    - is_dag: whether the graph is a Directed Acyclic Graph
    """
    nodes = pipeline.nodes
    edges = pipeline.edges

    num_nodes = len(nodes)
    num_edges = len(edges)
    dag_status = is_dag(nodes, edges)

    return {
        "num_nodes": num_nodes,
        "num_edges": num_edges,
        "is_dag": dag_status
    }
