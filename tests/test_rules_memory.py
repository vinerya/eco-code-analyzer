"""Tests for memory usage rules."""

import ast
import pytest
from eco_code_analyzer.rules.memory import (
    ContextManagerRule,
    GlobalVariableRule,
    MemoryEfficientDataStructureRule,
    MemoryLeakRule,
    LargeObjectLifetimeRule,
)
from eco_code_analyzer.rules.context import AnalysisContext


@pytest.fixture
def context():
    return AnalysisContext()


class TestContextManagerRule:
    def setup_method(self):
        self.rule = ContextManagerRule()

    def test_rewards_with_statement(self, context):
        code = '''
with open("file.txt") as f:
    data = f.read()
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                score = self.rule.check(node, context)
                assert score > 1.0
                break

    def test_rewards_multiple_context_managers(self, context):
        code = '''
with open("a.txt") as a, open("b.txt") as b:
    pass
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                score = self.rule.check(node, context)
                assert score == 1.3
                break


class TestGlobalVariableRule:
    def setup_method(self):
        self.rule = GlobalVariableRule()

    def test_penalizes_global(self, context):
        code = '''
def func():
    global x
    x = 1
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                score = self.rule.check(node, context)
                assert score < 1.0
                break

    def test_penalizes_nonlocal(self, context):
        code = '''
def outer():
    x = 1
    def inner():
        nonlocal x
        x = 2
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Nonlocal):
                score = self.rule.check(node, context)
                assert score == 0.8
                break


class TestMemoryEfficientDataStructureRule:
    def setup_method(self):
        self.rule = MemoryEfficientDataStructureRule()

    def test_rewards_set_usage(self, context):
        code = 'items = {1, 2, 3}'
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Set):
                score = self.rule.check(node, context)
                assert score > 1.0
                break


class TestLargeObjectLifetimeRule:
    def setup_method(self):
        self.rule = LargeObjectLifetimeRule()

    def test_penalizes_large_module_level_list(self, context):
        # scope_stack is empty = module level
        elements = ", ".join(str(i) for i in range(20))
        code = f'big_list = [{elements}]'
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                score = self.rule.check(node, context)
                assert score < 1.0
                break

    def test_no_penalty_inside_function(self, context):
        context.enter_scope(ast.FunctionDef())
        code = 'x = list(range(100))'
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                score = self.rule.check(node, context)
                assert score == 1.0
                break
