"""Tests for AnalysisContext."""

import ast
import pytest
from eco_code_analyzer.rules.context import AnalysisContext


class TestAnalysisContext:
    def setup_method(self):
        self.ctx = AnalysisContext()

    def test_scope_management(self):
        node = ast.FunctionDef()
        self.ctx.enter_scope(node)
        assert self.ctx.current_scope() is node
        self.ctx.exit_scope()
        assert self.ctx.current_scope() is None

    def test_exit_scope_empty(self):
        self.ctx.exit_scope()  # Should not raise

    def test_variable_types(self):
        self.ctx.record_variable_type("x", "int")
        assert self.ctx.get_variable_type("x") == "int"
        assert self.ctx.get_variable_type("y") is None

    def test_imports(self):
        self.ctx.record_import("os")
        assert self.ctx.has_import("os")
        assert not self.ctx.has_import("sys")

    def test_function_calls(self):
        self.ctx.record_function_call("print")
        self.ctx.record_function_call("print")
        assert self.ctx.get_call_count("print") == 2
        assert self.ctx.get_call_count("len") == 0

    def test_loop_depth(self):
        outer = ast.For()
        self.ctx.enter_loop(outer)
        assert self.ctx.get_loop_depth(outer) == 1

    def test_node_energy_cache(self):
        node = ast.Name()
        self.ctx.cache_node_energy(node, 0.5)
        assert self.ctx.get_cached_energy(node) == 0.5
        assert self.ctx.get_cached_energy(ast.Name()) is None

    def test_set_file_path(self):
        self.ctx.set_file_path("test.py")
        assert self.ctx.file_path == "test.py"

    def test_set_code_lines(self):
        self.ctx.set_code_lines("line1\nline2\nline3")
        assert len(self.ctx.code_lines) == 3

    def test_get_node_source(self):
        code = "x = 1\ny = 2\nz = 3"
        self.ctx.set_code_lines(code)
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and hasattr(node, 'lineno'):
                source = self.ctx.get_node_source(node)
                assert len(source) > 0
                break

    def test_get_node_source_no_lines(self):
        node = ast.Name()
        node.lineno = 1
        node.end_lineno = 1
        assert self.ctx.get_node_source(node) == ""

    def test_reset(self):
        self.ctx.record_import("os")
        self.ctx.record_variable_type("x", "int")
        self.ctx.reset()
        assert not self.ctx.has_import("os")
        assert self.ctx.get_variable_type("x") is None
