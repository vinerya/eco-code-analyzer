"""Tests for I/O efficiency rules."""

import ast
import pytest
from eco_code_analyzer.rules.io import (
    FileOperationRule,
    NetworkOperationRule,
    DatabaseOperationRule,
    CachingRule,
    BulkOperationRule,
)
from eco_code_analyzer.rules.context import AnalysisContext


@pytest.fixture
def context():
    return AnalysisContext()


class TestFileOperationRule:
    def setup_method(self):
        self.rule = FileOperationRule()

    def test_penalizes_file_open_in_loop(self, context):
        code = '''
for i in range(100):
    with open("file.txt") as f:
        line = f.readlines()[i]
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                score = self.rule.check(node, context)
                assert score < 1.0
                break

    def test_no_penalty_for_single_open(self, context):
        code = 'x = 1 + 2'
        tree = ast.parse(code)
        for node in ast.walk(tree):
            score = self.rule.check(node, context)
            assert score == 1.0


class TestNetworkOperationRule:
    def setup_method(self):
        self.rule = NetworkOperationRule()

    def test_penalizes_requests_in_loop(self, context):
        code = '''
for user_id in user_ids:
    response = requests.get(f"/api/users/{user_id}")
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                score = self.rule.check(node, context)
                assert score < 1.0
                break

    def test_no_penalty_without_loop(self, context):
        code = 'response = requests.get("/api/users")'
        tree = ast.parse(code)
        for node in ast.walk(tree):
            score = self.rule.check(node, context)
            assert score == 1.0


class TestDatabaseOperationRule:
    def setup_method(self):
        self.rule = DatabaseOperationRule()

    def test_penalizes_n_plus_1_query(self, context):
        code = '''
for user in users:
    orders = db.query(user.id)
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.For):
                score = self.rule.check(node, context)
                assert score < 1.0
                break


class TestCachingRule:
    def setup_method(self):
        self.rule = CachingRule()

    def test_rewards_lru_cache_decorator(self, context):
        code = '''
@lru_cache
def expensive(n):
    return n * 2
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                score = self.rule.check(node, context)
                assert score > 1.0
                break

    def test_rewards_cache_call_decorator(self, context):
        code = '''
@lru_cache(maxsize=128)
def expensive(n):
    return n * 2
'''
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                score = self.rule.check(node, context)
                assert score > 1.0
                break


class TestBulkOperationRule:
    def setup_method(self):
        self.rule = BulkOperationRule()

    def test_rewards_executemany(self, context):
        code = 'db.executemany("INSERT INTO t VALUES (?)", items)'
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == 'executemany':
                    score = self.rule.check(node, context)
                    assert score > 1.0
                    break

    def test_rewards_bulk_create(self, context):
        code = 'Model.bulk_create(objects)'
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr == 'bulk_create':
                    score = self.rule.check(node, context)
                    assert score > 1.0
                    break
