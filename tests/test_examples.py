"""
Example Scripts Tests

Validates Python example scripts for all vector databases:
- Syntax and import correctness verification
- Configuration consistency across examples
- Documentation completeness checking
- Error handling pattern validation
- Basic functionality testing with mocked dependencies

Ensures example scripts are working and educational for users.
"""

import pytest
import sys
import os
import importlib.util
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


class TestExampleScripts:
    """Test example scripts for basic functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.repo_root = Path(__file__).parent.parent
        self.examples_dir = self.repo_root / "examples"
        
    def test_examples_directory_exists(self):
        """Test that examples directory exists."""
        assert self.examples_dir.exists()
        assert self.examples_dir.is_dir()
        
    def test_example_files_exist(self):
        """Test that all expected example files exist."""
        expected_files = [
            "choma_example.py",
            "faiss_example.py",
            "milvus_example.py",
            "qdrant_example.py",
            "weaviate_example.py",
            "vector_db_benchmark.py"
        ]
        
        for filename in expected_files:
            file_path = self.examples_dir / filename
            assert file_path.exists(), f"Example file {filename} not found"
            assert file_path.is_file()
            
    def test_chroma_example_imports(self):
        """Test that Chroma example can be imported without errors."""
        chroma_file = self.examples_dir / "choma_example.py"
        
        # Test basic syntax by attempting to compile
        with open(chroma_file, 'r') as f:
            content = f.read()
            
        try:
            compile(content, str(chroma_file), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in chroma example: {e}")
            
    def test_faiss_example_imports(self):
        """Test that FAISS example can be imported without errors."""
        faiss_file = self.examples_dir / "faiss_example.py"
        
        # Test basic syntax by attempting to compile
        with open(faiss_file, 'r') as f:
            content = f.read()
            
        try:
            compile(content, str(faiss_file), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in FAISS example: {e}")
            
    def test_milvus_example_imports(self):
        """Test that Milvus example can be imported without errors."""
        milvus_file = self.examples_dir / "milvus_example.py"
        
        # Test basic syntax by attempting to compile
        with open(milvus_file, 'r') as f:
            content = f.read()
            
        try:
            compile(content, str(milvus_file), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in Milvus example: {e}")
            
    def test_qdrant_example_imports(self):
        """Test that Qdrant example can be imported without errors."""
        qdrant_file = self.examples_dir / "qdrant_example.py"
        
        # Test basic syntax by attempting to compile
        with open(qdrant_file, 'r') as f:
            content = f.read()
            
        try:
            compile(content, str(qdrant_file), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in Qdrant example: {e}")
            
    def test_weaviate_example_imports(self):
        """Test that Weaviate example can be imported without errors."""
        weaviate_file = self.examples_dir / "weaviate_example.py"
        
        # Test basic syntax by attempting to compile
        with open(weaviate_file, 'r') as f:
            content = f.read()
            
        try:
            compile(content, str(weaviate_file), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in Weaviate example: {e}")
            
    def test_vector_db_benchmark_imports(self):
        """Test that benchmark script can be imported without errors."""
        benchmark_file = self.examples_dir / "vector_db_benchmark.py"
        
        # Test basic syntax by attempting to compile
        with open(benchmark_file, 'r') as f:
            content = f.read()
            
        try:
            compile(content, str(benchmark_file), 'exec')
        except SyntaxError as e:
            pytest.fail(f"Syntax error in benchmark script: {e}")
            
    def test_all_examples_have_main_function(self):
        """Test that all examples have a main function."""
        example_files = [
            "choma_example.py",
            "faiss_example.py", 
            "milvus_example.py",
            "qdrant_example.py",
            "weaviate_example.py"
        ]
        
        for filename in example_files:
            file_path = self.examples_dir / filename
            with open(file_path, 'r') as f:
                content = f.read()
                
            assert 'def main(' in content, f"No main function found in {filename}"
            assert 'if __name__ == "__main__":' in content, f"No main guard found in {filename}"
            
    def test_examples_have_docstrings(self):
        """Test that all examples have proper docstrings."""
        example_files = [
            "choma_example.py",
            "faiss_example.py",
            "milvus_example.py", 
            "qdrant_example.py",
            "weaviate_example.py"
        ]
        
        for filename in example_files:
            file_path = self.examples_dir / filename
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for module docstring
            assert '"""' in content[:500], f"No docstring found in {filename}"
            
    def test_examples_have_requirements_comments(self):
        """Test that all examples document their requirements."""
        example_files = [
            "choma_example.py",
            "faiss_example.py",
            "milvus_example.py",
            "qdrant_example.py", 
            "weaviate_example.py"
        ]
        
        for filename in example_files:
            file_path = self.examples_dir / filename
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for requirements section
            assert 'Requirements:' in content or 'requirements:' in content, \
                f"No requirements section found in {filename}"
            assert 'pip install' in content, f"No pip install instructions in {filename}"
            
            
class TestFAISSExampleFunctionality:
    """Test FAISS example functionality with mocked dependencies."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.repo_root = Path(__file__).parent.parent
        self.examples_dir = self.repo_root / "examples"
        
    @patch('numpy.random.random')
    def test_faiss_generate_random_vectors(self, mock_random):
        """Test FAISS example vector generation."""
        mock_random.return_value = [[0.1, 0.2], [0.3, 0.4]]
        
        # Load and execute the function
        faiss_file = self.examples_dir / "faiss_example.py"
        spec = importlib.util.spec_from_file_location("faiss_example", faiss_file)
        
        try:
            module = importlib.util.module_from_spec(spec)
            # Mock the faiss import
            with patch.dict('sys.modules', {'faiss': Mock()}):
                spec.loader.exec_module(module)
                
            # Test the function
            vectors = module.generate_random_vectors(2, 2)
            assert len(vectors) == 2
            assert len(vectors[0]) == 2
            
        except ImportError:
            pytest.skip("FAISS not available for testing")
            
    def test_faiss_example_configuration(self):
        """Test FAISS example configuration constants."""
        faiss_file = self.examples_dir / "faiss_example.py"
        
        with open(faiss_file, 'r') as f:
            content = f.read()
            
        # Check for configuration constants
        assert 'DIMENSION = ' in content
        assert 'NUM_VECTORS = ' in content
        assert 'INDEX_FILE = ' in content
        
        # Extract dimension value
        lines = content.split('\n')
        dimension_line = next(line for line in lines if 'DIMENSION = ' in line)
        dimension = int(dimension_line.split('=')[1].strip())
        assert dimension > 0
        
        
class TestExampleErrorHandling:
    """Test error handling in example scripts."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.repo_root = Path(__file__).parent.parent
        self.examples_dir = self.repo_root / "examples"
        
    def test_examples_have_exception_handling(self):
        """Test that examples have proper exception handling."""
        example_files = [
            "choma_example.py",
            "faiss_example.py",
            "milvus_example.py",
            "qdrant_example.py",
            "weaviate_example.py"
        ]
        
        for filename in example_files:
            file_path = self.examples_dir / filename
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for exception handling
            assert 'try:' in content, f"No exception handling in {filename}"
            assert 'except' in content, f"No except clause in {filename}"
            
    def test_examples_have_cleanup_code(self):
        """Test that examples have proper cleanup code."""
        example_files = [
            "choma_example.py",
            "milvus_example.py",
            "qdrant_example.py",
            "weaviate_example.py"
        ]
        
        for filename in example_files:
            file_path = self.examples_dir / filename
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for cleanup operations
            has_cleanup = any(keyword in content.lower() for keyword in [
                'delete', 'drop', 'remove', 'cleanup', 'disconnect', 'close'
            ])
            assert has_cleanup, f"No cleanup code found in {filename}"


class TestConfigurationConsistency:
    """Test consistency of configuration across examples."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.repo_root = Path(__file__).parent.parent
        self.examples_dir = self.repo_root / "examples"
        
    def test_dimension_consistency(self):
        """Test that vector dimensions are consistent across examples."""
        example_files = [
            "choma_example.py",
            "faiss_example.py",
            "milvus_example.py",
            "qdrant_example.py",
            "weaviate_example.py"
        ]
        
        dimensions = []
        for filename in example_files:
            file_path = self.examples_dir / filename
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Extract dimension value
            lines = content.split('\n')
            dimension_lines = [line for line in lines if 'DIMENSION = ' in line]
            if dimension_lines:
                dimension = int(dimension_lines[0].split('=')[1].strip())
                dimensions.append(dimension)
                
        # Check that dimensions are consistent
        if len(dimensions) > 1:
            assert all(d == dimensions[0] for d in dimensions), \
                f"Inconsistent dimensions across examples: {dimensions}"
                
    def test_collection_name_patterns(self):
        """Test that collection names follow consistent patterns."""
        example_files = [
            "choma_example.py",
            "milvus_example.py", 
            "qdrant_example.py",
            "weaviate_example.py"
        ]
        
        for filename in example_files:
            file_path = self.examples_dir / filename
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for collection/class name constants
            has_collection_name = any(keyword in content for keyword in [
                'COLLECTION_NAME', 'CLASS_NAME', 'collection_name', 'class_name'
            ])
            assert has_collection_name, f"No collection name constant in {filename}"