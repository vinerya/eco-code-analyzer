"""Tests for rule suppression mechanism."""

import pytest
from eco_code_analyzer.analyzer import analyze_code, _get_suppressed_rules, _is_suppressed
import ast


class TestGetSuppressedRules:
    def test_parses_specific_rule_suppression(self):
        code = "x = 1  # noqa: eco-use_list_comprehension"
        suppressions = _get_suppressed_rules(code)
        assert 1 in suppressions
        assert "use_list_comprehension" in suppressions[1]

    def test_parses_bare_eco_suppression(self):
        code = "x = 1  # noqa: eco"
        suppressions = _get_suppressed_rules(code)
        assert 1 in suppressions
        assert "__all__" in suppressions[1]

    def test_no_suppression(self):
        code = "x = 1"
        suppressions = _get_suppressed_rules(code)
        assert len(suppressions) == 0

    def test_multiple_lines(self):
        code = "x = 1\ny = 2  # noqa: eco-rule1\nz = 3  # noqa: eco"
        suppressions = _get_suppressed_rules(code)
        assert 1 not in suppressions
        assert "rule1" in suppressions[2]
        assert "__all__" in suppressions[3]


class TestIsSuppressed:
    def test_suppressed_specific_rule(self):
        node = ast.Name(id='x')
        node.lineno = 1
        suppressions = {1: {"my_rule"}}
        assert _is_suppressed(node, "my_rule", suppressions) is True
        assert _is_suppressed(node, "other_rule", suppressions) is False

    def test_suppressed_all_rules(self):
        node = ast.Name(id='x')
        node.lineno = 1
        suppressions = {1: {"__all__"}}
        assert _is_suppressed(node, "any_rule", suppressions) is True

    def test_not_suppressed(self):
        node = ast.Name(id='x')
        node.lineno = 2
        suppressions = {1: {"my_rule"}}
        assert _is_suppressed(node, "my_rule", suppressions) is False

    def test_no_lineno(self):
        node = ast.Name(id='x')
        suppressions = {1: {"my_rule"}}
        assert _is_suppressed(node, "my_rule", suppressions) is False

    def test_empty_suppressions(self):
        node = ast.Name(id='x')
        node.lineno = 1
        assert _is_suppressed(node, "my_rule", {}) is False


class TestDisabledRulesConfig:
    def test_disabled_rules_in_config(self):
        code = '''
result = []
for item in range(100):
    result.append(item * 2)
'''
        # Analyze without disabling
        result_normal = analyze_code(code)

        # Analyze with the list comprehension rule disabled
        config = {"disabled_rules": ["use_list_comprehension"]}
        result_disabled = analyze_code(code, config=config)

        # Energy efficiency should be higher with the rule disabled
        assert result_disabled['energy_efficiency'] >= result_normal['energy_efficiency']
