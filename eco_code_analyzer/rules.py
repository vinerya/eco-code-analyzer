import ast

def check_loop_efficiency(node: ast.AST) -> float:
    """
    Check if loops are using efficient constructs like list comprehensions.
    """
    if isinstance(node, ast.For):
        # Penalize for loops that could be list comprehensions
        if isinstance(node.body[0], ast.Append):
            return 0.5
    return 1.0

def check_string_concatenation(node: ast.AST) -> float:
    """
    Check if string concatenation is done efficiently.
    """
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        if isinstance(node.left, ast.Str) and isinstance(node.right, ast.Str):
            return 0.5
    return 1.0

def check_memory_usage(node: ast.AST) -> float:
    """
    Check for potential memory leaks or inefficient memory usage.
    """
    if isinstance(node, ast.Global):
        # Penalize global variables as they can lead to higher memory usage
        return 0.7
    return 1.0

def check_list_comprehension(node: ast.AST) -> float:
    """
    Encourage the use of list comprehensions for simple loops.
    """
    if isinstance(node, ast.ListComp):
        return 1.2
    return 1.0

def check_generator_expression(node: ast.AST) -> float:
    """
    Encourage the use of generator expressions for large datasets.
    """
    if isinstance(node, ast.GeneratorExp):
        return 1.3
    return 1.0

def check_with_statement(node: ast.AST) -> float:
    """
    Encourage the use of 'with' statements for resource management.
    """
    if isinstance(node, ast.With):
        return 1.2
    return 1.0

def check_multiple_with_statements(node: ast.AST) -> float:
    """
    Encourage the use of multiple context managers in a single 'with' statement.
    """
    if isinstance(node, ast.With) and len(node.items) > 1:
        return 1.3
    return 1.0

def check_dict_get_method(node: ast.AST) -> float:
    """
    Encourage the use of dict.get() method instead of KeyError exception handling.
    """
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if node.func.attr == 'get' and isinstance(node.func.value, ast.Name):
            return 1.2
    return 1.0

def check_set_operations(node: ast.AST) -> float:
    """
    Encourage the use of set operations for efficient membership testing and deduplication.
    """
    if isinstance(node, (ast.Set, ast.SetComp)):
        return 1.2
    return 1.0

def check_lazy_evaluation(node: ast.AST) -> float:
    """
    Encourage the use of lazy evaluation techniques like short-circuit evaluation.
    """
    if isinstance(node, ast.BoolOp) and isinstance(node.op, (ast.And, ast.Or)):
        return 1.1
    return 1.0

# Plugin system for custom rules
custom_rules = []

def register_custom_rule(rule_func):
    custom_rules.append(rule_func)

def apply_custom_rules(node: ast.AST) -> float:
    score = 1.0
    for rule in custom_rules:
        score *= rule(node)
    return score