import pytest
import os
import click
import ast
import requests
from unittest import mock
from astrix.features.dependency import generate_dependency_info


def sample_python_file(tmp_path):
    """Creates a temporary Python file to test dependencies."""
    test_file = tmp_path / "sample.py"
    test_file.write_text("""
import os
import requests
import numpy as np

def example_function():
    return os.listdir(), np.array([1, 2, 3]), requests.get('https://example.com')
    """)
    return test_file


def test_generate_dependency_info_io_error():
    with pytest.raises(click.exceptions.Abort):
        generate_dependency_info('non_existent_file.py')



def test_generate_dependency_info_syntax_error(tmp_path):
    # Create a temporary Python file with a syntax error
        syntax_error_file = tmp_path / "syntax_error.py"
        syntax_error_file.write_text("def foo()\n    pass\n")

        with pytest.raises(click.exceptions.Abort):
            generate_dependency_info(syntax_error_file)


def test_generate_dependency_info_no_imports(tmp_path):
    # Create a temporary Python file without any imports
        no_imports_file = tmp_path / "no_imports.py"
        no_imports_file.write_text("def foo():\n    pass\n")

        result = generate_dependency_info(no_imports_file)

        # Expected result should be an empty list since there are no imports
        assert len(result) == 0


def test_generate_dependency_info_stdlib_only(tmp_path):
    # Create a temporary Python file with standard library imports
        stdlib_imports_file = tmp_path / "stdlib_imports.py"
        stdlib_imports_file.write_text("import os\nimport sys\n")

        result = generate_dependency_info(stdlib_imports_file)

        # Ensure os and sys are recognized as standard libraries
        assert len(result) == 2
        assert result[0][0] == "os"
        assert result[1][0] == "sys"
        assert "Inbuilt module of python" in result[0][1]
        assert "Inbuilt module of python" in result[1][1]



def test_third_party_libraries(tmp_path):
    # Create a sample Python file with third-party libraries
    python_file = tmp_path / "third_party_imports.py"
    python_code = """
import requests
import numpy as np
"""
    python_file.write_text(python_code)

    result = generate_dependency_info(python_file)
    assert any("requests" in row[0] for row in result), "requests module should be present"
    assert any("numpy" in row[0] for row in result), "numpy module should be present"
    
    for row in result:
        if row[0] == "requests":
            assert "No summary available :(" not in row[1], "requests summary should be fetched"
            assert "No documentation available :(" not in row[2], "requests documentation should be available"




def test_mixed_imports(tmp_path):
    python_file = tmp_path / "mixed_imports.py"
    python_code = """
import os
import sys
import requests
"""
    python_file.write_text(python_code)

    result = generate_dependency_info(python_file)

    assert any("os" in row[0] for row in result), "os module should be present"
    assert any("sys" in row[0] for row in result), "sys module should be present"
    
    assert any("requests" in row[0] for row in result), "requests module should be present"

    for row in result:
        if row[0] == "requests":
            assert "No summary available :(" not in row[1], "requests summary should be fetched"
            assert "No documentation available :(" not in row[2], "requests documentation should be available"

