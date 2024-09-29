import pytest
import os
import click
from astrix.features.code_quality import analyze_code_quality


@pytest.fixture
def sample_python_file(tmp_path):
    """Fixture that provides a temporary Python file for testing."""
    content = '''
import requests
import json
import os
from pandas import DataFrame

def get_package_requirements(package_name):
    """Fetch the package metadata from PyPI and return required dependencies."""
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url)
    data = response.json()

    requirements = data.get('info', {}).get('requires_dist', [])
    
    return requirements

def parse_requirements(requirements):
    """Parse the requirements list into a dictionary."""
    parsed = {}
    for requirement in requirements:
        pkg_name, _, version_spec = requirement.partition(' ')
        parsed[pkg_name] = version_spec or 'Any'
    
    return parsed

# Example usage
package_name = 'pandas'
requirements = get_package_requirements(package_name)
parsed_requirements = parse_requirements(requirements)

print(f"Dependencies required by {package_name}:")
for pkg, version in parsed_requirements.items():
    print(f"{pkg}: {version}")
    '''
    # Create a temporary file and write the content
    file_path = tmp_path / "sample_python_file.py"
    file_path.write_text(content)
    
    return file_path


def test_analyze_code_quality_valid_file(capsys, sample_python_file):
    # Test with a valid Python file
    results = analyze_code_quality(sample_python_file)
    
    # Capture the stdout output
    assert isinstance(results, list), "Expected a list of code quality metrics."
    assert len(results) > 0, "Expected at least one code quality result."

    for result in results:
        assert result.complexity , "Expected complexity metric in results."
    


def test_analyze_code_quality_invalid_extension():
    # Test with a non-Python file
    with pytest.raises(click.exceptions.Abort):  # click.Abort() raises SystemExit
        analyze_code_quality("invalid_file.txt")

def test_analyze_code_quality_file_not_exist():
    # Test with a path that does not exist
    with pytest.raises(click.exceptions.Abort):
        analyze_code_quality("non_existent_file.py")

def test_analyze_code_quality_unreadable_file(tmp_path):
    # Create a temporary file and change permissions to make it unreadable
    unreadable_file = tmp_path / "unreadable.py"
    unreadable_file.write_text("print('Hello, World!')\n")
    
    os.remove(unreadable_file)
    with pytest.raises(click.exceptions.Abort):  # Expecting a SystemExit due to an unreadable file
        analyze_code_quality(unreadable_file)
