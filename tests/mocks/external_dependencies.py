# AdaptiveMind Framework
# Copyright (c) 2025 Jimmy De Jesus
# Licensed under CC-BY 4.0
#
# AdaptiveMind - Intelligent AI Routing & Context Engine
# More info: https://github.com/[username]/adaptivemind
# License: https://creativecommons.org/licenses/by/4.0/

"""Mock implementations for external dependencies.

This module provides comprehensive mock objects for external libraries
and services to enable isolated testing without real dependencies.
"""

import types
import sys
from unittest.mock import Mock


class MockNeo4jDriver:
    """Mock Neo4j driver for database testing."""
    
    def __init__(self, uri="bolt://localhost:7687", auth=None):
        self.uri = uri
        self.auth = auth
        self.session_count = 0
        
    def session(self):
        """Return a mock session."""
        self.session_count += 1
        return MockNeo4jSession()
        
    def close(self):
        """Mock close method."""
        pass


class MockNeo4jSession:
    """Mock Neo4j session for testing."""
    
    def run(self, query, parameters=None):
        """Mock query execution."""
        return MockNeo4jResult()
        
    def close(self):
        """Mock close method."""
        pass


class MockNeo4jResult:
    """Mock Neo4j query result."""
    
    def __init__(self):
        self.records = []
        self.consume_called = False
        
    def consume(self):
        """Mock result consumption."""
        self.consume_called = True
        return MockNeo4jSummary()
        
    def __iter__(self):
        return iter(self.records)


class MockNeo4jSummary:
    """Mock Neo4j query summary."""
    
    def __init__(self):
        self.counters = {"nodes_created": 0, "nodes_deleted": 0}


class MockPydanticModel:
    """Mock Pydantic BaseModel for testing."""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def dict(self):
        """Return model as dictionary."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}
    
    def json(self):
        """Return model as JSON string."""
        import json
        return json.dumps(self.dict())
    
    @classmethod
    def parse_obj(cls, obj):
        """Parse object into model."""
        return cls(**obj)
    
    @classmethod
    def parse_raw(cls, json_str):
        """Parse JSON string into model."""
        import json
        return cls(**json.loads(json_str))


class MockNetworkX:
    """Mock NetworkX graph functionality."""
    
    def __init__(self):
        self._nodes = {}
        self._edges = {}
    
    def add_node(self, node, **attrs):
        """Add a node to the graph."""
        self._nodes[node] = attrs
    
    def add_edge(self, source, target, **attrs):
        """Add an edge to the graph."""
        if source not in self._edges:
            self._edges[source] = []
        self._edges[source].append((target, attrs))
    
    def nodes(self, data=False):
        """Return graph nodes."""
        if data:
            return list(self._nodes.items())
        return list(self._nodes.keys())
    
    def edges(self, data=False):
        """Return graph edges."""
        edges = []
        for source, targets in self._edges.items():
            for target, attrs in targets:
                if data:
                    edges.append((source, target, attrs))
                else:
                    edges.append((source, target))
        return edges
    
    def out_edges(self, node, data=False):
        """Return outgoing edges for a node."""
        targets = self._edges.get(node, [])
        if data:
            return [(node, target, attrs) for target, attrs in targets]
        return [(node, target) for target, attrs in targets]


class MockChromaDB:
    """Mock ChromaDB vector store functionality."""
    
    def __init__(self):
        self.collections = {}
        self.embeddings = {}
    
    def create_collection(self, name, embedding_function=None):
        """Create a new collection."""
        self.collections[name] = MockChromaCollection(name, embedding_function)
        return self.collections[name]
    
    def get_collection(self, name):
        """Get an existing collection."""
        return self.collections.get(name)
    
    def delete_collection(self, name):
        """Delete a collection."""
        if name in self.collections:
            del self.collections[name]


class MockChromaCollection:
    """Mock ChromaDB collection."""
    
    def __init__(self, name, embedding_function=None):
        self.name = name
        self.embedding_function = embedding_function
        self.documents = {}
        self.metadatas = {}
        self.ids = []
    
    def add(self, ids, documents=None, metadatas=None, embeddings=None):
        """Add documents to collection."""
        if ids:
            self.ids.extend(ids if isinstance(ids, list) else [ids])
        
        if documents:
            doc_list = documents if isinstance(documents, list) else [documents]
            for i, doc_id in enumerate(self.ids[-len(doc_list):]):
                self.documents[doc_id] = doc_list[i]
        
        if metadatas:
            meta_list = metadatas if isinstance(metadatas, list) else [metadatas]
            for i, doc_id in enumerate(self.ids[-len(meta_list):]):
                self.metadatas[doc_id] = meta_list[i]
    
    def query(self, query_texts=None, query_embeddings=None, n_results=10):
        """Query collection for similar documents."""
        return {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }
    
    def count(self):
        """Return number of documents in collection."""
        return len(self.ids)


class MockKeyring:
    """Mock keyring for secure credential storage."""
    
    @staticmethod
    def set_password(service, username, password):
        """Store password in keyring."""
        if not hasattr(MockKeyring, '_storage'):
            MockKeyring._storage = {}
        MockKeyring._storage[f"{service}:{username}"] = password
    
    @staticmethod
    def get_password(service, username):
        """Retrieve password from keyring."""
        if not hasattr(MockKeyring, '_storage'):
            return None
        return MockKeyring._storage.get(f"{service}:{username}")
    
    @staticmethod
    def delete_password(service, username):
        """Delete password from keyring."""
        if hasattr(MockKeyring, '_storage'):
            key = f"{service}:{username}"
            if key in MockKeyring._storage:
                del MockKeyring._storage[key]


class MockAIOHTTP:
    """Mock aiohttp web framework."""
    
    class Application:
        """Mock aiohttp Application."""
        pass
    
    class Response:
        """Mock aiohttp Response."""
        
        def __init__(self, data=None, status=200, content_type='application/json'):
            self.data = data
            self.status = status
            self.content_type = content_type
        
        def text(self):
            return str(self.data)
        
        def json(self):
            return self.data
        
        async def __aenter__(self):
            return self
        
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass


# Setup module-level stubs to prevent import errors
def setup_external_dependency_stubs():
    """Setup external dependency stubs to prevent import errors."""
    
    # Neo4j stubs
    neo4j_module = types.ModuleType("neo4j")
    neo4j_module.Driver = MockNeo4jDriver
    
    exceptions_submodule = types.ModuleType("neo4j.exceptions")
    exceptions_submodule.ServiceUnavailable = type('ServiceUnavailable', (Exception,), {})
    exceptions_submodule.TransientError = type('TransientError', (Exception,), {})
    neo4j_module.exceptions = exceptions_submodule
    
    sys.modules.setdefault("neo4j", neo4j_module)
    sys.modules.setdefault("neo4j.exceptions", exceptions_submodule)
    
    # Pydantic stubs  
    pydantic_module = types.ModuleType("pydantic")
    pydantic_module.BaseModel = MockPydanticModel
    
    def mock_field(*args, **kwargs):
        return None
    
    def mock_create_model(name, **fields):
        return type(name, (MockPydanticModel,), fields)
    
    pydantic_module.Field = mock_field
    pydantic_module.create_model = mock_create_model
    sys.modules.setdefault("pydantic", pydantic_module)
    
    # NetworkX stubs
    nx_module = types.ModuleType("networkx")
    nx_module.DiGraph = MockNetworkX
    sys.modules.setdefault("networkx", nx_module)
    
    # ChromaDB stubs
    chromadb_module = types.ModuleType("chromadb")
    chromadb_utils = types.ModuleType("chromadb.utils")
    chromadb_embedding = types.ModuleType("chromadb.utils.embedding_functions")
    
    class MockEmbeddingFunction:
        pass
    
    chromadb_embedding.EmbeddingFunction = MockEmbeddingFunction
    chromadb_utils.embedding_functions = chromadb_embedding
    sys.modules.setdefault("chromadb", chromadb_module)
    sys.modules.setdefault("chromadb.utils", chromadb_utils)
    sys.modules.setdefault("chromadb.utils.embedding_functions", chromadb_embedding)
    
    # Keyring stubs
    keyring_module = types.ModuleType("keyring")
    keyring_module.get_password = MockKeyring.get_password
    keyring_module.set_password = MockKeyring.set_password
    sys.modules.setdefault("keyring", keyring_module)
    
    # aiohttp stubs
    aiohttp_module = types.ModuleType("aiohttp")
    web_submodule = types.ModuleType("aiohttp.web")
    web_submodule.Application = MockAIOHTTP.Application
    web_submodule.Response = MockAIOHTTP.Response
    aiohttp_module.web = web_submodule
    sys.modules.setdefault("aiohttp", aiohttp_module)
    sys.modules.setdefault("aiohttp.web", web_submodule)


# Initialize stubs on import
setup_external_dependency_stubs()

__all__ = [
    "MockNeo4jDriver",
    "MockPydanticModel", 
    "MockNetworkX",
    "MockChromaDB",
    "MockKeyring",
    "MockAIOHTTP",
    "setup_external_dependency_stubs"
]
