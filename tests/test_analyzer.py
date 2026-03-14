"""Tests for the core analyzer module."""

import json
import os
import tempfile
import pytest
from eco_code_analyzer.analyzer import (
    analyze_code,
    analyze_project,
    get_eco_score,
    get_project_eco_score,
    get_improvement_suggestions,
    get_detailed_analysis,
    generate_report,
    estimate_energy_savings,
    calculate_project_carbon_footprint,
    load_config,
)


class TestAnalyzeCode:
    def test_returns_all_categories(self, sample_efficient_code):
        result = analyze_code(sample_efficient_code)
        expected_keys = {'energy_efficiency', 'resource_usage', 'io_efficiency',
                         'algorithm_efficiency', 'custom_rules'}
        assert set(result.keys()) == expected_keys

    def test_scores_between_0_and_1(self, sample_efficient_code):
        result = analyze_code(sample_efficient_code)
        for key, score in result.items():
            assert 0.0 <= score <= 1.0, f"{key} score {score} out of range"

    def test_efficient_code_scores_higher(self, sample_efficient_code, sample_inefficient_code):
        efficient = analyze_code(sample_efficient_code)
        inefficient = analyze_code(sample_inefficient_code)
        assert get_eco_score(efficient) >= get_eco_score(inefficient)

    def test_syntax_error_returns_zeros(self, sample_syntax_error):
        result = analyze_code(sample_syntax_error)
        for score in result.values():
            assert score == 0.0

    def test_empty_code(self, sample_empty_code):
        result = analyze_code(sample_empty_code)
        for score in result.values():
            assert 0.0 <= score <= 1.0

    def test_with_file_path(self, sample_efficient_code):
        result = analyze_code(sample_efficient_code, file_path="test.py")
        assert isinstance(result, dict)

    def test_with_config(self, sample_efficient_code):
        config = {"thresholds": {"category_score": 0.5}}
        result = analyze_code(sample_efficient_code, config=config)
        assert isinstance(result, dict)


class TestGetEcoScore:
    def test_perfect_scores(self):
        result = {
            'energy_efficiency': 1.0,
            'resource_usage': 1.0,
            'io_efficiency': 1.0,
            'algorithm_efficiency': 1.0,
            'custom_rules': 1.0,
        }
        assert get_eco_score(result) == 1.0

    def test_zero_scores(self):
        result = {
            'energy_efficiency': 0.0,
            'resource_usage': 0.0,
            'io_efficiency': 0.0,
            'algorithm_efficiency': 0.0,
            'custom_rules': 0.0,
        }
        assert get_eco_score(result) == 0.0

    def test_missing_categories_default_to_1(self):
        result = {'energy_efficiency': 0.5}
        score = get_eco_score(result)
        assert 0.0 < score < 1.0

    def test_does_not_mutate_input(self):
        result = {'energy_efficiency': 0.5}
        original = result.copy()
        get_eco_score(result)
        assert result == original

    def test_score_clamped_to_range(self):
        # Even with extreme values, should stay in [0, 1]
        result = {
            'energy_efficiency': 2.0,
            'resource_usage': 2.0,
            'io_efficiency': 2.0,
            'algorithm_efficiency': 2.0,
            'custom_rules': 2.0,
        }
        score = get_eco_score(result)
        assert score <= 1.0


class TestAnalyzeProject:
    def test_analyze_project_directory(self, tmp_path):
        # Create a simple Python file
        py_file = tmp_path / "example.py"
        py_file.write_text("x = [i * 2 for i in range(10)]")

        result = analyze_project(str(tmp_path))
        assert 'overall_score' in result
        assert isinstance(result['overall_score'], (int, float))

    def test_analyze_empty_directory(self, tmp_path):
        result = analyze_project(str(tmp_path))
        assert result['overall_score'] == 0

    def test_skips_non_python_files(self, tmp_path):
        (tmp_path / "readme.md").write_text("# Hello")
        (tmp_path / "data.json").write_text("{}")
        result = analyze_project(str(tmp_path))
        assert result['overall_score'] == 0


class TestGetImprovementSuggestions:
    def test_low_scores_generate_suggestions(self):
        result = {
            'energy_efficiency': 0.3,
            'resource_usage': 0.3,
            'io_efficiency': 0.3,
            'algorithm_efficiency': 0.3,
            'custom_rules': 1.0,
        }
        suggestions = get_improvement_suggestions(result)
        assert len(suggestions) > 0

    def test_high_scores_no_suggestions(self):
        result = {
            'energy_efficiency': 1.0,
            'resource_usage': 1.0,
            'io_efficiency': 1.0,
            'algorithm_efficiency': 1.0,
            'custom_rules': 1.0,
        }
        suggestions = get_improvement_suggestions(result)
        assert len(suggestions) == 0

    def test_suggestion_structure(self):
        result = {'energy_efficiency': 0.3, 'resource_usage': 1.0,
                  'io_efficiency': 1.0, 'algorithm_efficiency': 1.0, 'custom_rules': 1.0}
        suggestions = get_improvement_suggestions(result)
        for s in suggestions:
            assert 'category' in s
            assert 'suggestion' in s
            assert 'impact' in s

    def test_custom_threshold(self):
        result = {'energy_efficiency': 0.6, 'resource_usage': 1.0,
                  'io_efficiency': 1.0, 'algorithm_efficiency': 1.0, 'custom_rules': 1.0}
        config = {'thresholds': {'category_score': 0.8}}
        suggestions = get_improvement_suggestions(result, config)
        assert len(suggestions) > 0


class TestGetDetailedAnalysis:
    def test_returns_string(self, sample_efficient_code):
        result = analyze_code(sample_efficient_code)
        analysis = get_detailed_analysis(result)
        assert isinstance(analysis, str)
        assert len(analysis) > 0

    def test_contains_all_categories(self, sample_efficient_code):
        result = analyze_code(sample_efficient_code)
        analysis = get_detailed_analysis(result)
        assert "Energy Efficiency" in analysis
        assert "Resource Usage" in analysis
        assert "I/O Efficiency" in analysis
        assert "Algorithm Efficiency" in analysis
        assert "Custom Rules" in analysis


class TestGenerateReport:
    def test_generates_valid_json(self, tmp_path):
        py_file = tmp_path / "test.py"
        py_file.write_text("x = 1")
        project_results = analyze_project(str(tmp_path))

        output_file = str(tmp_path / "report.json")
        generate_report(project_results, output_file)

        with open(output_file) as f:
            report = json.load(f)

        assert 'project_score' in report
        assert 'file_scores' in report
        assert 'improvement_suggestions' in report
        assert 'estimated_energy_savings' in report


class TestEstimateEnergySavings:
    def test_perfect_score_no_savings(self):
        result = {'overall_score': 1.0}
        savings = estimate_energy_savings(result)
        assert savings['energy_kwh_per_year'] == 0.0
        assert savings['co2_kg_per_year'] == 0.0

    def test_zero_score_max_savings(self):
        result = {'overall_score': 0.0}
        savings = estimate_energy_savings(result)
        assert savings['energy_kwh_per_year'] == 100.0
        assert savings['co2_kg_per_year'] == 50.0
        assert savings['trees_equivalent'] == 2.0


class TestLoadConfig:
    def test_load_valid_config(self, tmp_path):
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps({"weights": {"energy_efficiency": 0.5}}))
        config = load_config(str(config_file))
        assert config['weights']['energy_efficiency'] == 0.5

    def test_load_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/config.json")


class TestCalculateProjectCarbonFootprint:
    def test_perfect_score_zero_footprint(self):
        result = {'overall_score': 1.0}
        assert calculate_project_carbon_footprint(result) == 0.0

    def test_zero_score_max_footprint(self):
        result = {'overall_score': 0.0}
        assert calculate_project_carbon_footprint(result) == 100.0
