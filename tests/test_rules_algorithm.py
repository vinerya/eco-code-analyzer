"""Tests for algorithm efficiency rules."""

import ast
import pytest
from eco_code_analyzer.rules.algorithm import (
    TimeComplexityRule,
    SpaceComplexityRule,
    AlgorithmSelectionRule,
    DataStructureSelectionRule,
    RecursionOptimizationRule,
)
from eco_code_analyzer.rules.context import AnalysisContext


@pytest.fixture
def context():
    return AnalysisContext()


class TestTimeComplexityRule:
    def setup_method(self):
        self.rule = TimeComplexityRule()

    def test_rewards_sorted_builtin(self, context):
        code = 'result = sorted(items)'
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == 'sorted':
                    score = self.rule.check(node, context)
                    assert score > 1.0
                    break

    def test_penalizes_nested_loops(self, context):
        code = '''
for i in range(n):
    for j in range(n):
        x = i + j
'''
        tree = ast.parse(code)
        # Check outer for loop
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                score = self.rule.check(node, context)
                assert score < 1.0
                break


class TestSpaceComplexityRule:
    def setup_method(self):
        self.rule = SpaceComplexityRule()

    def test_penalizes_multiple_copies(self, context):
        code = '''
def process(data):
    a = data.copy()
    b = data.copy()
    return a, b
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                score = self.rule.check(node, context)
                assert score < 1.0
                break

    def test_no_penalty_single_copy(self, context):
        code = '''
def process(data):
    a = data.copy()
    return a
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                score = self.rule.check(node, context)
                assert score == 1.0
                break


class TestAlgorithmSelectionRule:
    def setup_method(self):
        self.rule = AlgorithmSelectionRule()

    def test_rewards_builtin_max(self, context):
        code = 'largest = max(numbers)'
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == 'max':
                    score = self.rule.check(node, context)
                    assert score > 1.0
                    break

    def test_rewards_builtin_sum(self, context):
        code = 'total = sum(numbers)'
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == 'sum':
                    score = self.rule.check(node, context)
                    assert score > 1.0
                    break


class TestDataStructureSelectionRule:
    def setup_method(self):
        self.rule = DataStructureSelectionRule()

    def test_rewards_dict_usage(self, context):
        code = 'lookup = {"a": 1, "b": 2}'
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Dict):
                score = self.rule.check(node, context)
                assert score > 1.0
                break

    def test_rewards_specialized_structures(self, context):
        code = 'counts = Counter(items)'
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id == 'Counter':
                    score = self.rule.check(node, context)
                    assert score > 1.0
                    break


class TestRecursionOptimizationRule:
    def setup_method(self):
        self.rule = RecursionOptimizationRule()

    def test_penalizes_naive_recursion(self, context):
        code = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                score = self.rule.check(node, context)
                assert score < 1.0
                break

    def test_rewards_memoized_recursion(self, context):
        code = '''
def fibonacci(n):
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
    memo[n] = fibonacci(n-1) + fibonacci(n-2)
    return memo[n]
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                score = self.rule.check(node, context)
                assert score > 1.0
                break

    def test_no_penalty_for_non_recursive(self, context):
        code = '''
def add(a, b):
    return a + b
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                score = self.rule.check(node, context)
                assert score == 1.0
                break
