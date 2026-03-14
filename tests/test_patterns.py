"""Tests for PatternDetector."""

import ast
import pytest
from eco_code_analyzer.rules.patterns import PatternDetector
from eco_code_analyzer.rules.context import AnalysisContext


@pytest.fixture
def context():
    return AnalysisContext()


class TestIsListAppendInLoop:
    def test_detects_append_in_loop(self, context):
        code = '''
for item in items:
    result.append(item)
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                assert PatternDetector.is_list_append_in_loop(node, context) is True
                break

    def test_no_detection_for_non_append(self, context):
        code = '''
for item in items:
    print(item)
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                assert PatternDetector.is_list_append_in_loop(node, context) is False
                break

    def test_no_detection_for_multi_statement_body(self, context):
        code = '''
for item in items:
    x = item * 2
    result.append(x)
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                assert PatternDetector.is_list_append_in_loop(node, context) is False
                break


class TestIsSimpleTransformation:
    def test_simple_binop(self, context):
        code = '''
for item in items:
    result.append(item * 2)
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                assert PatternDetector.is_simple_transformation(node, context) is True
                break

    def test_simple_name(self, context):
        code = '''
for item in items:
    result.append(item)
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                assert PatternDetector.is_simple_transformation(node, context) is True
                break


class TestIsStringConcatenationInLoop:
    def test_detects_string_concat(self, context):
        context.record_variable_type("result", "str")
        code = '''
for item in items:
    result += str(item)
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                assert PatternDetector.is_string_concatenation_in_loop(node, context) is True
                break

    def test_no_detection_for_numeric_add(self, context):
        context.record_variable_type("total", "int")
        code = '''
for item in items:
    total += item
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                assert PatternDetector.is_string_concatenation_in_loop(node, context) is False
                break


class TestIsNestedLoop:
    def test_detects_nested_for(self, context):
        code = '''
for i in range(n):
    for j in range(n):
        pass
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                assert PatternDetector.is_nested_loop(node, context) is True
                break

    def test_no_detection_single_loop(self, context):
        code = '''
for i in range(n):
    x = i * 2
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                assert PatternDetector.is_nested_loop(node, context) is False
                break


class TestHasRedundantComputation:
    def test_detects_redundant(self, context):
        code = '''
for i in range(n):
    x = expensive()
    result.append(i + x)
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                assert PatternDetector.has_redundant_computation(node, context) is True
                break

    def test_no_detection_when_using_loop_var(self, context):
        code = '''
for i in range(n):
    x = process(i)
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                assert PatternDetector.has_redundant_computation(node, context) is False
                break


class TestContainsName:
    def test_finds_name(self):
        code = 'x + y'
        tree = ast.parse(code, mode='eval')
        assert PatternDetector._contains_name(tree.body, 'x') is True

    def test_does_not_find_absent_name(self):
        code = 'x + y'
        tree = ast.parse(code, mode='eval')
        assert PatternDetector._contains_name(tree.body, 'z') is False

    def test_handles_none(self):
        assert PatternDetector._contains_name(None, 'x') is False


class TestIsSimpleExpression:
    def test_name_is_simple(self):
        node = ast.Name(id='x')
        assert PatternDetector._is_simple_expression(node) is True

    def test_constant_is_simple(self):
        node = ast.Constant(value=42)
        assert PatternDetector._is_simple_expression(node) is True

    def test_none_is_not_simple(self):
        assert PatternDetector._is_simple_expression(None) is False

    def test_call_is_not_simple(self):
        code = 'func(x)'
        tree = ast.parse(code, mode='eval')
        assert PatternDetector._is_simple_expression(tree.body) is False
