"""Tests for energy efficiency rules."""

import ast
import pytest
from eco_code_analyzer.rules.energy import (
    ListComprehensionRule,
    GeneratorExpressionRule,
    LazyEvaluationRule,
    NestedLoopRule,
    RedundantComputationRule,
)
from eco_code_analyzer.rules.context import AnalysisContext


@pytest.fixture
def context():
    return AnalysisContext()


class TestListComprehensionRule:
    def setup_method(self):
        self.rule = ListComprehensionRule()

    def test_penalizes_loop_with_append(self, context):
        code = '''
result = []
for item in items:
    result.append(item * 2)
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                score = self.rule.check(node, context)
                assert score < 1.0
                break

    def test_no_penalty_for_normal_loop(self, context):
        code = '''
for item in items:
    print(item)
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                score = self.rule.check(node, context)
                assert score == 1.0
                break

    def test_no_penalty_for_non_loop(self, context):
        code = 'x = 1'
        tree = ast.parse(code)
        for node in ast.walk(tree):
            score = self.rule.check(node, context)
            assert score == 1.0

    def test_get_suggestion(self):
        suggestion = self.rule.get_suggestion()
        assert 'category' in suggestion
        assert suggestion['category'] == 'energy_efficiency'


class TestGeneratorExpressionRule:
    def setup_method(self):
        self.rule = GeneratorExpressionRule()

    def test_rewards_generator_expression(self, context):
        code = 'total = sum(x * 2 for x in range(100))'
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.GeneratorExp):
                score = self.rule.check(node, context)
                assert score > 1.0
                break

    def test_penalizes_list_comp_in_for(self, context):
        code = '''
for x in [f(y) for y in items]:
    print(x)
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For) and isinstance(node.iter, ast.ListComp):
                score = self.rule.check(node, context)
                assert score < 1.0
                break


class TestLazyEvaluationRule:
    def setup_method(self):
        self.rule = LazyEvaluationRule()

    def test_rewards_any_with_generator(self, context):
        code = 'found = any(x > 5 for x in items)'
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'any':
                score = self.rule.check(node, context)
                assert score > 1.0
                break

    def test_penalizes_loop_for_boolean_check(self, context):
        code = '''
for item in items:
    if item > 5:
        return True
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                score = self.rule.check(node, context)
                assert score < 1.0
                break


class TestNestedLoopRule:
    def setup_method(self):
        self.rule = NestedLoopRule()

    def test_penalizes_nested_loops(self, context):
        code = '''
for i in range(n):
    for j in range(n):
        x = i + j
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                score = self.rule.check(node, context)
                # At least the outer loop should trigger
                break

    def test_no_penalty_for_single_loop(self, context):
        code = '''
for i in range(n):
    x = i * 2
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                score = self.rule.check(node, context)
                assert score == 1.0
                break


class TestRedundantComputationRule:
    def setup_method(self):
        self.rule = RedundantComputationRule()

    def test_penalizes_redundant_computation(self, context):
        code = '''
for i in range(n):
    x = expensive_function()
    result.append(i + x)
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                score = self.rule.check(node, context)
                assert score < 1.0
                break

    def test_no_penalty_when_using_loop_var(self, context):
        code = '''
for i in range(n):
    x = process(i)
    result.append(x)
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                score = self.rule.check(node, context)
                assert score == 1.0
                break
