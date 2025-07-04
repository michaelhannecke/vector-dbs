"""
Integration Tests

End-to-end integration tests for vector database deployments:
- Docker container build and runtime verification
- Service connectivity and health check validation
- Basic API workflow testing
- Cross-service compatibility verification

These tests require Docker and optionally running services.
Use pytest markers to run selectively:
- pytest -m integration: Run all integration tests
- pytest -m "not integration": Skip integration tests
"""

import pytest
import requests
import time
import docker
import yaml
import json
from pathlib import Path
from unittest.mock import patch
import subprocess


class TestDockerIntegration:
    """Integration tests for Docker containers."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.repo_root = Path(__file__).parent.parent
        self.docker_dir = self.repo_root / "docker"
        self.client = docker.from_env()
        
    def test_docker_client_available(self):
        """Test that Docker client is available."""
        try:
            self.client.ping()
        except Exception:
            pytest.skip("Docker not available")
            
    def test_faiss_api_container_builds(self):
        """Test that FAISS API container builds successfully."""
        faiss_dir = self.docker_dir / "faiss-api"
        dockerfile_path = faiss_dir / "Dockerfile"
        
        if not dockerfile_path.exists():
            pytest.skip("FAISS Dockerfile not found")
            
        try:
            # Build the image
            image, logs = self.client.images.build(
                path=str(faiss_dir),
                tag="test-faiss-api",
                rm=True
            )
            
            # Clean up
            self.client.images.remove(image.id, force=True)
            
        except docker.errors.BuildError as e:
            pytest.fail(f"Docker build failed: {e}")
            
    @pytest.mark.integration
    def test_faiss_api_container_runs(self):
        """Test that FAISS API container runs and responds to health checks."""
        faiss_dir = self.docker_dir / "faiss-api"
        
        if not (faiss_dir / "Dockerfile").exists():
            pytest.skip("FAISS Dockerfile not found")
            
        try:
            # Build the image
            image, logs = self.client.images.build(
                path=str(faiss_dir),
                tag="test-faiss-api",
                rm=True
            )
            
            # Run the container
            container = self.client.containers.run(
                image="test-faiss-api",
                ports={'5000/tcp': 5000},
                environment={
                    'VECTOR_DIMENSION': '128',
                    'INDEX_TYPE': 'Flat'
                },
                detach=True
            )
            
            # Wait for container to start
            time.sleep(10)
            
            # Check health endpoint
            try:
                response = requests.get("http://localhost:5000/health", timeout=5)
                assert response.status_code == 200
                
                data = response.json()
                assert data['status'] == 'healthy'
                
            except requests.RequestException:
                pytest.fail("FAISS API not responding to health check")
            
        except docker.errors.BuildError as e:
            pytest.skip(f"Docker build failed: {e}")
            
        finally:
            # Clean up
            try:
                container.stop()
                container.remove()
                self.client.images.remove("test-faiss-api", force=True)
            except:
                pass  # Best effort cleanup
                
    def test_docker_compose_files_valid(self):
        """Test that all docker-compose files are valid."""
        compose_files = [
            self.docker_dir / "milvus" / "docker-compose.yaml",
            self.docker_dir / "qdrant" / "docker-compose.yaml",
            self.docker_dir / "weaviate" / "docker-compose.yaml", 
            self.docker_dir / "chroma" / "docker-compose.yaml",
            self.docker_dir / "faiss-api" / "docker-compose.yaml"
        ]
        
        for compose_file in compose_files:
            if compose_file.exists():
                try:
                    result = subprocess.run(
                        ["docker-compose", "-f", str(compose_file), "config"],
                        capture_output=True,
                        text=True,
                        cwd=compose_file.parent
                    )
                    
                    if result.returncode != 0:
                        pytest.fail(f"Invalid docker-compose file {compose_file}: {result.stderr}")
                        
                except FileNotFoundError:
                    pytest.skip("docker-compose not available")


class TestAPIEndpoints:
    """Test API endpoints functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.faiss_base_url = "http://localhost:5000"
        
    def test_faiss_health_endpoint(self):
        """Test FAISS API health endpoint."""
        try:
            response = requests.get(f"{self.faiss_base_url}/health", timeout=5)
            
            if response.status_code != 200:
                pytest.skip("FAISS API not running")
                
            data = response.json()
            assert 'status' in data
            assert 'timestamp' in data
            
        except requests.RequestException:
            pytest.skip("FAISS API not available")
            
    def test_faiss_stats_endpoint(self):
        """Test FAISS API stats endpoint."""
        try:
            response = requests.get(f"{self.faiss_base_url}/stats", timeout=5)
            
            # Should return 401 without authentication
            assert response.status_code == 401
            
            # Test with authentication header
            headers = {"Authorization": "Bearer test-token"}
            response = requests.get(f"{self.faiss_base_url}/stats", 
                                    headers=headers, timeout=5)
            
            # Should return stats or still 401 depending on configuration
            assert response.status_code in [200, 401]
            
        except requests.RequestException:
            pytest.skip("FAISS API not available")
            
    def test_faiss_add_vectors_endpoint(self):
        """Test FAISS API add vectors endpoint."""
        try:
            test_vectors = [[0.1, 0.2, 0.3, 0.4] * 32]  # 128-dimensional vector
            
            response = requests.post(
                f"{self.faiss_base_url}/add",
                json={"vectors": test_vectors},
                timeout=5
            )
            
            # Should return 401 without authentication
            assert response.status_code == 401
            
        except requests.RequestException:
            pytest.skip("FAISS API not available")
            
    def test_faiss_search_vectors_endpoint(self):
        """Test FAISS API search vectors endpoint."""
        try:
            test_query = [[0.1, 0.2, 0.3, 0.4] * 32]  # 128-dimensional vector
            
            response = requests.post(
                f"{self.faiss_base_url}/search",
                json={"query_vectors": test_query, "k": 5},
                timeout=5
            )
            
            # Should return 401 without authentication
            assert response.status_code == 401
            
        except requests.RequestException:
            pytest.skip("FAISS API not available")


class TestServiceConnectivity:
    """Test connectivity to vector database services."""
    
    def test_milvus_connectivity(self):
        """Test connectivity to Milvus service."""
        try:
            import socket
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', 19530))
            sock.close()
            
            if result == 0:
                # Port is open, service likely running
                assert True
            else:
                pytest.skip("Milvus service not running")
                
        except Exception:
            pytest.skip("Cannot test Milvus connectivity")
            
    def test_qdrant_connectivity(self):
        """Test connectivity to Qdrant service."""
        try:
            response = requests.get("http://localhost:6333/health", timeout=5)
            
            if response.status_code == 200:
                assert True
            else:
                pytest.skip("Qdrant service not responding")
                
        except requests.RequestException:
            pytest.skip("Qdrant service not available")
            
    def test_weaviate_connectivity(self):
        """Test connectivity to Weaviate service."""
        try:
            response = requests.get("http://localhost:8080/v1/meta", timeout=5)
            
            if response.status_code == 200:
                assert True
            else:
                pytest.skip("Weaviate service not responding")
                
        except requests.RequestException:
            pytest.skip("Weaviate service not available")
            
    def test_chroma_connectivity(self):
        """Test connectivity to Chroma service."""
        try:
            response = requests.get("http://localhost:8000/api/v1/heartbeat", timeout=5)
            
            if response.status_code == 200:
                assert True
            else:
                pytest.skip("Chroma service not responding")
                
        except requests.RequestException:
            pytest.skip("Chroma service not available")


class TestBasicOperations:
    """Test basic operations on running services."""
    
    @pytest.mark.integration
    def test_faiss_basic_workflow(self):
        """Test basic FAISS API workflow."""
        base_url = "http://localhost:5000"
        
        try:
            # Check if service is running
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("FAISS API not running")
                
            # Try to add vectors (should fail without auth)
            test_vectors = [[0.1] * 128]  # 128-dimensional vector
            response = requests.post(
                f"{base_url}/add",
                json={"vectors": test_vectors},
                timeout=5
            )
            assert response.status_code == 401
            
            # Try to search vectors (should fail without auth)
            response = requests.post(
                f"{base_url}/search",
                json={"query_vectors": test_vectors, "k": 5},
                timeout=5
            )
            assert response.status_code == 401
            
        except requests.RequestException:
            pytest.skip("FAISS API not available")
            
    @pytest.mark.integration
    def test_qdrant_basic_workflow(self):
        """Test basic Qdrant workflow."""
        base_url = "http://localhost:6333"
        
        try:
            # Check if service is running
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("Qdrant service not running")
                
            # Try to list collections
            response = requests.get(f"{base_url}/collections", timeout=5)
            assert response.status_code == 200
            
        except requests.RequestException:
            pytest.skip("Qdrant service not available")
            
    @pytest.mark.integration  
    def test_weaviate_basic_workflow(self):
        """Test basic Weaviate workflow."""
        base_url = "http://localhost:8080"
        
        try:
            # Check if service is running
            response = requests.get(f"{base_url}/v1/meta", timeout=5)
            if response.status_code != 200:
                pytest.skip("Weaviate service not running")
                
            # Try to get schema
            response = requests.get(f"{base_url}/v1/schema", timeout=5)
            assert response.status_code == 200
            
        except requests.RequestException:
            pytest.skip("Weaviate service not available")
            
    @pytest.mark.integration
    def test_chroma_basic_workflow(self):
        """Test basic Chroma workflow."""
        base_url = "http://localhost:8000"
        
        try:
            # Check if service is running
            response = requests.get(f"{base_url}/api/v1/heartbeat", timeout=5)
            if response.status_code != 200:
                pytest.skip("Chroma service not running")
                
            # Try to list collections
            response = requests.get(f"{base_url}/api/v1/collections", timeout=5)
            # May require authentication, but should not return connection error
            assert response.status_code in [200, 401, 403]
            
        except requests.RequestException:
            pytest.skip("Chroma service not available")