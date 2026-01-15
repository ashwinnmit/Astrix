# Astrix

<img alt="Astrix Logo" src="https://drive.google.com/thumbnail?id=1mKsoththfyIWg5l1gjKO0rRsGNrFpzeS" height="300" style="display: block;
    margin: 0 auto;"/>

[![PyPI version](https://badge.fury.io/py/astrix.svg)](https://badge.fury.io/py/astrix)
![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)
[![Downloads](https://static.pepy.tech/badge/astrix)](https://pepy.tech/project/astrix)

**Astrix: Your All-in-One Python Project Analyzer**

Astrix is a comprehensive tool designed to analyze and optimize Python projects by checking dependencies, code quality metrics, documentation, and much more.

---

## Features

Astrix comes with a set of powerful commands to help you analyze, manage, and optimize your Python projects.

- **analyze**: Analyze functions in a given Python file for various metrics like cyclomatic complexity.
  
  ```bash
  astrix analyze <filepath>

- **callgraph**: Generate a call graph of the specified Python file to visualize function dependencies.
  
  ```bash
  astrix callgraph <filepath>

- **class-info**: Analyze the specified Python file and generate a class hierarchy diagram.
  
  ```bash
  astrix class-info <filepath>

- **maintainability**: Analyze the maintainability index and Halstead metrics for the given Python file.
  
  ```bash
  astrix maintainability <filepath>

- **deps**: Analyze the specified Python file and return a list of dependencies, and return various information such as dependency name, its description, its documentation link and the github url
  
  ```bash
  astrix deps <filepath>

- **install**: Create a virtual environment for the current project and install dependencies from a specified file (e.g., requirements.txt), if the file is not provided, it simply creates a virtual environment.
  
  ```bash
  astrix install <filepath>
  
- **delete**: Delete the virtual environment associated with the current project.
  
  ```bash
  astrix delete <venv-name>

---

## Installation

You can install Astrix using:

```bash
pip install astrix
