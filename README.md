# Eco-Code Analyzer

Eco-Code Analyzer is a Python library that analyzes code for its ecological impact and provides a score based on various factors such as energy efficiency, resource usage, and code optimizations.

## Installation

You can install Eco-Code Analyzer using pip:

```
pip install eco-code-analyzer
```

For development, you can install additional dependencies:

```
pip install eco-code-analyzer[dev]
```

## Features

- Analyzes Python code for ecological impact
- Provides an overall eco-score
- Breaks down the analysis into categories:
  - Energy Efficiency
  - Resource Usage
  - Code Optimizations
  - Custom Rules
- Analyzes entire projects or directories
- Generates detailed reports
- Integrates with Git to analyze code history
- Supports custom configuration
- Extensible rule system for adding new ecological impact checks

## Usage

### As a library

```python
from eco_code_analyzer import analyze_code, get_eco_score, get_improvement_suggestions

code = """
def example_function():
    result = []
    for i in range(100):
        result.append(i * 2)
    return result
"""

analysis_result = analyze_code(code)
eco_score = get_eco_score(analysis_result)
suggestions = get_improvement_suggestions(analysis_result)

print(f"Eco-Score: {eco_score}")
print("Improvement Suggestions:")
for suggestion in suggestions:
    print(f"- {suggestion}")
```

### As a command-line tool

Analyze a single file:

```
eco-code-analyzer path/to/your/python_file.py
```

Analyze a project directory:

```
eco-code-analyzer path/to/your/project/directory -v
```

Generate a detailed report:

```
eco-code-analyzer path/to/your/project/directory -o report.json
```

Analyze Git history:

```
eco-code-analyzer path/to/your/project/directory -g -n 10
```

Use a custom configuration:

```
eco-code-analyzer path/to/your/project/directory -c config.json
```

## Configuration

You can customize the behavior of the Eco-Code Analyzer by providing a JSON configuration file. Here's an example:

```json
{
  "weights": {
    "energy_efficiency": 0.4,
    "resource_usage": 0.3,
    "code_optimizations": 0.2,
    "custom_rules": 0.1
  },
  "thresholds": {
    "eco_score": 0.7,
    "category_score": 0.6
  }
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.