"""Tests for the CLI module."""

import json
import sys
import pytest
from unittest.mock import patch
from eco_code_analyzer.cli import main, format_output_json, format_output_markdown


class TestFormatOutputJson:
    def test_returns_valid_json(self):
        data = {"score": 0.85, "categories": {"energy": 0.9}}
        result = format_output_json(data)
        parsed = json.loads(result)
        assert parsed == data


class TestFormatOutputMarkdown:
    def test_contains_header(self):
        result = format_output_markdown(
            0.85,
            {"energy_efficiency": 0.9, "resource_usage": 0.8},
            [],
            {"energy_kwh_per_year": 10, "co2_kg_per_year": 5, "trees_equivalent": 0.5},
            "test.py"
        )
        assert "# Eco-Code Analysis: test.py" in result
        assert "0.85" in result

    def test_includes_suggestions(self):
        suggestions = [{
            "category": "energy_efficiency",
            "suggestion": "Use list comprehensions",
            "impact": "medium",
            "example": "result = [x for x in items]"
        }]
        result = format_output_markdown(
            0.5, {"energy_efficiency": 0.5}, suggestions,
            {"energy_kwh_per_year": 50, "co2_kg_per_year": 25, "trees_equivalent": 1},
            "test.py"
        )
        assert "Use list comprehensions" in result
        assert "## Improvement Suggestions" in result


class TestCLIMain:
    def test_file_analysis(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text("x = [i for i in range(10)]")

        with patch('sys.argv', ['eco-code-analyzer', str(py_file)]):
            main()  # Should not raise

    def test_directory_analysis(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text("x = 1")

        with patch('sys.argv', ['eco-code-analyzer', str(tmp_path)]):
            main()

    def test_invalid_path_exits(self, tmp_path):
        with patch('sys.argv', ['eco-code-analyzer', str(tmp_path / 'nonexistent')]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2

    def test_json_format(self, tmp_path, capsys):
        py_file = tmp_path / "test.py"
        py_file.write_text("x = 1")

        with patch('sys.argv', ['eco-code-analyzer', str(py_file), '--format', 'json']):
            main()

        captured = capsys.readouterr()
        parsed = json.loads(captured.out)
        assert 'eco_score' in parsed

    def test_markdown_format(self, tmp_path, capsys):
        py_file = tmp_path / "test.py"
        py_file.write_text("x = 1")

        with patch('sys.argv', ['eco-code-analyzer', str(py_file), '--format', 'markdown']):
            main()

        captured = capsys.readouterr()
        assert "# Eco-Code Analysis" in captured.out

    def test_threshold_pass(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text("x = 1")

        with patch('sys.argv', ['eco-code-analyzer', str(py_file), '--threshold', '0.1']):
            main()  # Should not raise

    def test_threshold_fail(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text('''
result = []
for item in range(100):
    result.append(item)

for i in range(n):
    for j in range(n):
        for k in range(n):
            pass

global_data = {}

def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
''')
        with patch('sys.argv', ['eco-code-analyzer', str(py_file), '--threshold', '0.99']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1

    def test_verbose_mode(self, tmp_path, capsys):
        py_file = tmp_path / "test.py"
        py_file.write_text("x = 1")

        with patch('sys.argv', ['eco-code-analyzer', str(py_file), '-v']):
            main()

        captured = capsys.readouterr()
        assert "Detailed Analysis" in captured.out
