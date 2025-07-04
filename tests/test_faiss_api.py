"""
FAISS API Tests

Comprehensive test suite for the FAISS REST API implementation:
- API endpoint functionality testing
- Authentication and authorization validation
- Error handling and edge case verification
- Index initialization and configuration testing
- Mock-based testing to avoid external dependencies

Tests use mocking to isolate API logic from FAISS library dependencies.
"""

import pytest
import json
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the faiss-api directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'docker', 'faiss-api'))

try:
    from app import app, init_index, authenticate, get_index_stats, IndexStats
    import faiss
except ImportError as e:
    pytest.skip(f"FAISS API dependencies not available: {e}", allow_module_level=True)


class TestFAISSAPI:
    """Test FAISS API endpoints and functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert data['status'] == 'healthy'
        assert 'timestamp' in data
        
    @patch('app.authenticate')
    def test_stats_endpoint_unauthorized(self, mock_auth):
        """Test stats endpoint with unauthorized access."""
        mock_auth.return_value = False
        
        response = self.client.get('/stats')
        assert response.status_code == 401
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Unauthorized'
        
    @patch('app.authenticate')
    @patch('app.get_index_stats')
    def test_stats_endpoint_authorized(self, mock_stats, mock_auth):
        """Test stats endpoint with authorized access."""
        mock_auth.return_value = True
        mock_stats.return_value = IndexStats(
            index_type="Flat",
            dimension=384,
            total_vectors=100,
            is_trained=True
        )
        
        response = self.client.get('/stats')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['index_type'] == 'Flat'
        assert data['dimension'] == 384
        assert data['total_vectors'] == 100
        assert data['is_trained'] is True
        
    @patch('app.authenticate')
    @patch('app.index')
    @patch('app.faiss')
    def test_add_vectors_success(self, mock_faiss, mock_index, mock_auth):
        """Test successful vector addition."""
        mock_auth.return_value = True
        mock_index.ntotal = 0
        mock_index.add = Mock()
        mock_faiss.write_index = Mock()
        
        # Mock environment variables
        with patch.dict(os.environ, {'VECTOR_DIMENSION': '384'}):
            test_vectors = np.random.random((5, 384)).tolist()
            
            response = self.client.post('/add', 
                json={'vectors': test_vectors},
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
            assert data['vectors_added'] == 5
            
    @patch('app.authenticate')
    def test_add_vectors_dimension_mismatch(self, mock_auth):
        """Test vector addition with dimension mismatch."""
        mock_auth.return_value = True
        
        # Mock environment variables
        with patch.dict(os.environ, {'VECTOR_DIMENSION': '384'}):
            test_vectors = np.random.random((5, 128)).tolist()  # Wrong dimension
            
            response = self.client.post('/add',
                json={'vectors': test_vectors},
                content_type='application/json'
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'dimension mismatch' in data['error'].lower()
            
    @patch('app.authenticate')
    @patch('app.index')
    def test_search_vectors_success(self, mock_index, mock_auth):
        """Test successful vector search."""
        mock_auth.return_value = True
        mock_index.search = Mock(return_value=(
            np.array([[0.1, 0.2, 0.3]]),  # distances
            np.array([[1, 2, 3]])         # indices
        ))
        
        # Mock environment variables
        with patch.dict(os.environ, {'VECTOR_DIMENSION': '384'}):
            test_query = np.random.random((1, 384)).tolist()
            
            response = self.client.post('/search',
                json={'query_vectors': test_query, 'k': 3},
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
            assert 'results' in data
            assert len(data['results']) == 1
            assert len(data['results'][0]['distances']) == 3
            assert len(data['results'][0]['indices']) == 3
            
    @patch('app.authenticate')
    @patch('app.index')
    @patch('app.faiss')
    def test_reset_index(self, mock_faiss, mock_index, mock_auth):
        """Test index reset functionality."""
        mock_auth.return_value = True
        mock_faiss.IndexFlatL2 = Mock()
        mock_faiss.write_index = Mock()
        
        # Mock environment variables
        with patch.dict(os.environ, {'INDEX_TYPE': 'Flat', 'VECTOR_DIMENSION': '384'}):
            response = self.client.post('/reset')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
            assert 'reset successfully' in data['message']
            
    def test_authentication_no_token(self):
        """Test authentication when no token is required."""
        with patch.dict(os.environ, {'API_TOKEN': ''}, clear=True):
            with app.test_request_context():
                result = authenticate()
                assert result is True
                
    def test_authentication_with_valid_token(self):
        """Test authentication with valid bearer token."""
        with patch.dict(os.environ, {'API_TOKEN': 'test-token'}):
            with app.test_request_context(headers={'Authorization': 'Bearer test-token'}):
                result = authenticate()
                assert result is True
                
    def test_authentication_with_invalid_token(self):
        """Test authentication with invalid bearer token."""
        with patch.dict(os.environ, {'API_TOKEN': 'test-token'}):
            with app.test_request_context(headers={'Authorization': 'Bearer wrong-token'}):
                result = authenticate()
                assert result is False
                
    def test_authentication_malformed_header(self):
        """Test authentication with malformed authorization header."""
        with patch.dict(os.environ, {'API_TOKEN': 'test-token'}):
            with app.test_request_context(headers={'Authorization': 'InvalidFormat'}):
                result = authenticate()
                assert result is False
                
    @patch('app.faiss')
    def test_index_stats_flat_index(self, mock_faiss):
        """Test getting stats for a flat index."""
        mock_index = Mock()
        mock_index.ntotal = 100
        
        with patch('app.index', mock_index):
            with patch.dict(os.environ, {'INDEX_TYPE': 'Flat', 'VECTOR_DIMENSION': '384'}):
                stats = get_index_stats()
                
                assert stats.index_type == 'Flat'
                assert stats.dimension == 384
                assert stats.total_vectors == 100
                assert stats.is_trained is True
                
    @patch('app.faiss')
    def test_index_stats_ivf_index(self, mock_faiss):
        """Test getting stats for an IVF index."""
        mock_index = Mock()
        mock_index.ntotal = 100
        mock_index.is_trained = True
        mock_index.nlist = 50
        mock_index.nprobe = 10
        
        mock_faiss.IndexIVF = Mock()
        
        with patch('app.index', mock_index):
            with patch('app.isinstance', return_value=True):
                with patch.dict(os.environ, {'INDEX_TYPE': 'IVF', 'VECTOR_DIMENSION': '384'}):
                    stats = get_index_stats()
                    
                    assert stats.index_type == 'IVF'
                    assert stats.dimension == 384
                    assert stats.total_vectors == 100
                    assert stats.is_trained is True
                    assert stats.nlist == 50
                    assert stats.nprobe == 10


class TestFAISSIndexInitialization:
    """Test FAISS index initialization and configuration."""
    
    @patch('app.faiss')
    @patch('app.os.path.exists')
    def test_init_index_create_new_flat(self, mock_exists, mock_faiss):
        """Test creating a new flat index."""
        mock_exists.return_value = False
        mock_index = Mock()
        mock_faiss.IndexFlatL2.return_value = mock_index
        mock_faiss.write_index = Mock()
        
        with patch.dict(os.environ, {'INDEX_TYPE': 'Flat', 'VECTOR_DIMENSION': '384'}):
            with patch('app.logger'):
                result = init_index()
                
                assert result is True
                mock_faiss.IndexFlatL2.assert_called_once_with(384)
                mock_faiss.write_index.assert_called_once()
                
    @patch('app.faiss')
    @patch('app.os.path.exists')
    def test_init_index_create_new_ivf(self, mock_exists, mock_faiss):
        """Test creating a new IVF index."""
        mock_exists.return_value = False
        mock_quantizer = Mock()
        mock_index = Mock()
        mock_faiss.IndexFlatL2.return_value = mock_quantizer
        mock_faiss.IndexIVFFlat.return_value = mock_index
        mock_faiss.write_index = Mock()
        
        with patch.dict(os.environ, {'INDEX_TYPE': 'IVF', 'VECTOR_DIMENSION': '384', 'NLIST': '100'}):
            with patch('app.logger'):
                result = init_index()
                
                assert result is True
                mock_faiss.IndexFlatL2.assert_called_once_with(384)
                mock_faiss.IndexIVFFlat.assert_called_once_with(
                    mock_quantizer, 384, 100, mock_faiss.METRIC_L2
                )
                mock_faiss.write_index.assert_called_once()
                
    @patch('app.faiss')
    @patch('app.os.path.exists')
    def test_init_index_load_existing(self, mock_exists, mock_faiss):
        """Test loading an existing index."""
        mock_exists.return_value = True
        mock_index = Mock()
        mock_index.ntotal = 100
        mock_faiss.read_index.return_value = mock_index
        mock_faiss.IndexIVF = Mock()
        
        with patch('app.logger'):
            with patch('app.isinstance', return_value=False):
                result = init_index()
                
                assert result is True
                mock_faiss.read_index.assert_called_once()
                
    @patch('app.faiss')
    @patch('app.os.path.exists')
    def test_init_index_error_handling(self, mock_exists, mock_faiss):
        """Test error handling during index initialization."""
        mock_exists.return_value = False
        mock_faiss.IndexFlatL2.side_effect = Exception("Test error")
        
        with patch('app.logger'):
            result = init_index()
            
            assert result is False