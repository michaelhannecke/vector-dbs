"""
Pytest configuration and fixtures for vector database tests.
"""

import pytest
import os
import sys
from pathlib import Path


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may require running services)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers", "docker: marks tests that require Docker"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names and paths."""
    for item in items:
        # Add integration marker to integration tests
        if "integration" in str(item.fspath).lower():
            item.add_marker(pytest.mark.integration)
            
        # Add docker marker to docker-related tests  
        if "docker" in str(item.fspath).lower() or "test_docker" in item.name:
            item.add_marker(pytest.mark.docker)


@pytest.fixture(scope="session")
def repo_root():
    """Get the repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session") 
def docker_dir(repo_root):
    """Get the docker configurations directory."""
    return repo_root / "docker"


@pytest.fixture(scope="session")
def examples_dir(repo_root):
    """Get the examples directory."""
    return repo_root / "examples"


@pytest.fixture(scope="function")
def temp_index_file(tmp_path):
    """Create a temporary index file for testing."""
    index_file = tmp_path / "test_index.idx"
    return str(index_file)


@pytest.fixture(scope="session")
def test_vectors():
    """Generate test vectors for use in tests."""
    import numpy as np
    
    # Generate consistent test vectors
    np.random.seed(42)
    vectors = np.random.random((100, 128)).astype(np.float32)
    return vectors


@pytest.fixture(scope="session")
def test_metadata():
    """Generate test metadata for use in tests."""
    return [
        {"category": "test", "id": i, "value": f"test_item_{i}"}
        for i in range(100)
    ]


@pytest.fixture(scope="function")
def mock_faiss_index():
    """Create a mock FAISS index for testing."""
    from unittest.mock import Mock
    
    mock_index = Mock()
    mock_index.ntotal = 0
    mock_index.d = 128
    mock_index.is_trained = True
    mock_index.add = Mock()
    mock_index.search = Mock(return_value=(
        [[0.1, 0.2, 0.3, 0.4, 0.5]],  # distances
        [[1, 2, 3, 4, 5]]              # indices
    ))
    
    return mock_index


@pytest.fixture(scope="function")
def api_client():
    """Create a test client for API testing."""
    try:
        # Try to import the FAISS API app
        sys.path.insert(0, str(Path(__file__).parent.parent / "docker" / "faiss-api"))
        from app import app
        
        app.config['TESTING'] = True
        return app.test_client()
        
    except ImportError:
        pytest.skip("FAISS API not available")


@pytest.fixture(scope="function")
def docker_client():
    """Create a Docker client for testing."""
    try:
        import docker
        client = docker.from_env()
        client.ping()  # Test connection
        return client
        
    except Exception:
        pytest.skip("Docker not available")


@pytest.fixture(scope="function")
def cleanup_containers():
    """Fixture to clean up test containers after tests."""
    containers_to_cleanup = []
    
    def add_container(container):
        containers_to_cleanup.append(container)
        return container
    
    yield add_container
    
    # Cleanup
    try:
        import docker
        client = docker.from_env()
        
        for container in containers_to_cleanup:
            try:
                if hasattr(container, 'stop'):
                    container.stop()
                    container.remove()
                elif isinstance(container, str):
                    c = client.containers.get(container)
                    c.stop()
                    c.remove()
            except Exception:
                pass  # Best effort cleanup
                
    except Exception:
        pass  # Docker not available


@pytest.fixture(scope="session")
def service_urls():
    """Default service URLs for testing."""
    return {
        "milvus": "localhost:19530",
        "qdrant": "http://localhost:6333", 
        "weaviate": "http://localhost:8080",
        "chroma": "http://localhost:8000",
        "faiss_api": "http://localhost:5000"
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment variables."""
    # Set test environment variables
    test_env = {
        "TESTING": "true",
        "VECTOR_DIMENSION": "128",
        "INDEX_TYPE": "Flat"
    }
    
    # Store original values
    original_env = {}
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    yield
    
    # Restore original values
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value