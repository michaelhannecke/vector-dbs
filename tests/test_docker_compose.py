"""
Docker Compose Configuration Tests

This module validates Docker Compose configurations for all vector databases:
- YAML syntax validation
- Service configuration verification  
- Port conflict detection
- Health check validation
- Resource limit verification

Tests ensure deployments are properly configured before runtime.
"""

import pytest
import yaml
import os
from pathlib import Path


class TestDockerComposeConfigurations:
    """Test Docker Compose configurations for all vector databases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.repo_root = Path(__file__).parent.parent
        self.docker_dir = self.repo_root / "docker"
        
    def test_milvus_docker_compose(self):
        """Test Milvus Docker Compose configuration."""
        compose_file = self.docker_dir / "milvus" / "docker-compose.yaml"
        assert compose_file.exists(), "Milvus docker-compose.yaml not found"
        
        with open(compose_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Test basic structure
        assert 'services' in config
        assert 'etcd' in config['services']
        assert 'minio' in config['services']
        assert 'standalone' in config['services']
        
        # Test port mappings
        milvus_ports = config['services']['standalone']['ports']
        assert "19530:19530" in milvus_ports
        assert "9091:9091" in milvus_ports
        
        # Test health checks
        assert 'healthcheck' in config['services']['standalone']
        assert 'healthcheck' in config['services']['etcd']
        assert 'healthcheck' in config['services']['minio']
        
        # Test resource limits
        assert 'deploy' in config['services']['standalone']
        assert 'resources' in config['services']['standalone']['deploy']
        
    def test_qdrant_docker_compose(self):
        """Test Qdrant Docker Compose configuration."""
        compose_file = self.docker_dir / "qdrant" / "docker-compose.yaml"
        assert compose_file.exists(), "Qdrant docker-compose.yaml not found"
        
        with open(compose_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Test basic structure
        assert 'services' in config
        assert 'qdrant' in config['services']
        
        # Test port mappings
        qdrant_ports = config['services']['qdrant']['ports']
        assert "6333:6333" in qdrant_ports
        assert "6334:6334" in qdrant_ports
        
        # Test health check
        assert 'healthcheck' in config['services']['qdrant']
        
        # Test volume mounts
        assert 'volumes' in config['services']['qdrant']
        volumes = config['services']['qdrant']['volumes']
        assert any('./qdrant_storage:/qdrant/storage' in v for v in volumes)
        
    def test_weaviate_docker_compose(self):
        """Test Weaviate Docker Compose configuration."""
        compose_file = self.docker_dir / "weaviate" / "docker-compose.yaml"
        assert compose_file.exists(), "Weaviate docker-compose.yaml not found"
        
        with open(compose_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Test basic structure
        assert 'services' in config
        assert 'weaviate' in config['services']
        assert 't2v-transformers' in config['services']
        assert 'img2vec-neural' in config['services']
        
        # Test port mapping
        weaviate_ports = config['services']['weaviate']['ports']
        assert "8080:8080" in weaviate_ports
        
        # Test dependencies
        assert 'depends_on' in config['services']['weaviate']
        deps = config['services']['weaviate']['depends_on']
        assert 't2v-transformers' in deps
        assert 'img2vec-neural' in deps
        
    def test_chroma_docker_compose(self):
        """Test Chroma Docker Compose configuration."""
        compose_file = self.docker_dir / "chroma" / "docker-compose.yaml"
        assert compose_file.exists(), "Chroma docker-compose.yaml not found"
        
        with open(compose_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Test basic structure
        assert 'services' in config
        assert 'chroma' in config['services']
        
        # Test port mapping
        chroma_ports = config['services']['chroma']['ports']
        assert 8000 in chroma_ports
        
        # Test environment variables
        assert 'environment' in config['services']['chroma']
        env = config['services']['chroma']['environment']
        assert any('CHROMA_SERVER_HTTP_PORT=8000' in str(v) for v in env)
        
    def test_faiss_docker_compose(self):
        """Test FAISS API Docker Compose configuration."""
        compose_file = self.docker_dir / "faiss-api" / "docker-compose.yaml"
        assert compose_file.exists(), "FAISS docker-compose.yaml not found"
        
        with open(compose_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Test basic structure
        assert 'services' in config
        assert 'faiss-api' in config['services']
        
        # Test build configuration
        assert 'build' in config['services']['faiss-api']
        assert 'context' in config['services']['faiss-api']['build']
        
        # Test port mapping
        faiss_ports = config['services']['faiss-api']['ports']
        assert "5000:5000" in faiss_ports
        
        # Test environment variables
        assert 'environment' in config['services']['faiss-api']
        env = config['services']['faiss-api']['environment']
        assert any('VECTOR_DIMENSION=384' in str(v) for v in env)
        
    def test_monitoring_docker_compose(self):
        """Test monitoring Docker Compose configuration."""
        compose_file = self.repo_root / "monitoring" / "docker-compose.yaml"
        assert compose_file.exists(), "Monitoring docker-compose.yaml not found"
        
        with open(compose_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # Test basic structure
        assert 'services' in config
        # Should contain prometheus and grafana services
        assert len(config['services']) >= 1
        
    def test_all_compose_files_valid_yaml(self):
        """Test that all Docker Compose files are valid YAML."""
        compose_files = [
            self.docker_dir / "milvus" / "docker-compose.yaml",
            self.docker_dir / "qdrant" / "docker-compose.yaml", 
            self.docker_dir / "weaviate" / "docker-compose.yaml",
            self.docker_dir / "chroma" / "docker-compose.yaml",
            self.docker_dir / "faiss-api" / "docker-compose.yaml",
            self.repo_root / "monitoring" / "docker-compose.yaml"
        ]
        
        for compose_file in compose_files:
            if compose_file.exists():
                with open(compose_file, 'r') as f:
                    try:
                        yaml.safe_load(f)
                    except yaml.YAMLError as e:
                        pytest.fail(f"Invalid YAML in {compose_file}: {e}")
                        
    def test_port_conflicts(self):
        """Test that services don't have conflicting port mappings."""
        used_ports = set()
        compose_files = [
            (self.docker_dir / "milvus" / "docker-compose.yaml", "milvus"),
            (self.docker_dir / "qdrant" / "docker-compose.yaml", "qdrant"),
            (self.docker_dir / "weaviate" / "docker-compose.yaml", "weaviate"),
            (self.docker_dir / "chroma" / "docker-compose.yaml", "chroma"),
            (self.docker_dir / "faiss-api" / "docker-compose.yaml", "faiss-api")
        ]
        
        for compose_file, service_name in compose_files:
            if compose_file.exists():
                with open(compose_file, 'r') as f:
                    config = yaml.safe_load(f)
                    
                for service in config.get('services', {}).values():
                    if 'ports' in service:
                        for port_mapping in service['ports']:
                            if isinstance(port_mapping, str):
                                host_port = port_mapping.split(':')[0]
                                assert host_port not in used_ports, f"Port {host_port} conflict in {service_name}"
                                used_ports.add(host_port)
                            elif isinstance(port_mapping, int):
                                assert str(port_mapping) not in used_ports, f"Port {port_mapping} conflict in {service_name}"
                                used_ports.add(str(port_mapping))