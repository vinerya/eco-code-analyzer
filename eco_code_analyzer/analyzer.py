import ast
import os
import json
from typing import Dict, List, Tuple
from .rules import (
    check_loop_efficiency,
    check_string_concatenation,
    check_memory_usage,
    check_list_comprehension,
    check_generator_expression,
    check_with_statement,
    check_multiple_with_statements,
    check_dict_get_method,
    check_set_operations,
    check_lazy_evaluation,
    apply_custom_rules
)

def analyze_code(code: str) -> Dict[str, float]:
    """
    Analyze the given Python code for ecological impact.
    """
    tree = ast.parse(code)
    result = {
        'energy_efficiency': analyze_energy_efficiency(tree),
        'resource_usage': analyze_resource_usage(tree),
        'code_optimizations': analyze_code_optimizations(tree),
        'custom_rules': analyze_custom_rules(tree),
    }
    return result

def analyze_project(project_path: str) -> Dict[str, Dict[str, float]]:
    """
    Analyze all Python files in the given project directory.
    """
    project_results = {}
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    code = f.read()
                project_results[file_path] = analyze_code(code)
    return project_results

def get_eco_score(analysis_result: Dict[str, float]) -> float:
    """
    Calculate an overall eco-score based on the analysis result.
    """
    weights = {
        'energy_efficiency': 0.3,
        'resource_usage': 0.3,
        'code_optimizations': 0.3,
        'custom_rules': 0.1,
    }
    
    score = sum(analysis_result[key] * weights[key] for key in weights)
    return round(score, 2)

def get_project_eco_score(project_results: Dict[str, Dict[str, float]]) -> float:
    """
    Calculate an overall eco-score for the entire project.
    """
    file_scores = [get_eco_score(result) for result in project_results.values()]
    return round(sum(file_scores) / len(file_scores), 2)

def analyze_energy_efficiency(tree: ast.AST) -> float:
    score = 1.0
    for node in ast.walk(tree):
        score *= check_loop_efficiency(node)
        score *= check_list_comprehension(node)
        score *= check_generator_expression(node)
        score *= check_lazy_evaluation(node)
    return round(score, 2)

def analyze_resource_usage(tree: ast.AST) -> float:
    score = 1.0
    for node in ast.walk(tree):
        score *= check_memory_usage(node)
        score *= check_with_statement(node)
        score *= check_multiple_with_statements(node)
        score *= check_set_operations(node)
    return round(score, 2)

def analyze_code_optimizations(tree: ast.AST) -> float:
    score = 1.0
    for node in ast.walk(tree):
        score *= check_string_concatenation(node)
        score *= check_dict_get_method(node)
    return round(score, 2)

def analyze_custom_rules(tree: ast.AST) -> float:
    score = 1.0
    for node in ast.walk(tree):
        score *= apply_custom_rules(node)
    return round(score, 2)

def get_improvement_suggestions(analysis_result: Dict[str, float]) -> List[str]:
    suggestions = []
    if analysis_result['energy_efficiency'] < 0.7:
        suggestions.append("Consider using more efficient loop constructs, list comprehensions, and generator expressions.")
        suggestions.append("Look for opportunities to use lazy evaluation techniques.")
    if analysis_result['resource_usage'] < 0.7:
        suggestions.append("Review your code for potential memory leaks and optimize resource usage.")
        suggestions.append("Use 'with' statements for better resource management, especially with multiple context managers.")
        suggestions.append("Consider using set operations for efficient membership testing and deduplication.")
    if analysis_result['code_optimizations'] < 0.7:
        suggestions.append("Look for opportunities to optimize string operations and use more efficient data structures.")
        suggestions.append("Use dict.get() method instead of KeyError exception handling for dictionary access.")
    if analysis_result['custom_rules'] < 0.7:
        suggestions.append("Review custom rules and consider optimizing code based on their recommendations.")
    return suggestions

def get_detailed_analysis(analysis_result: Dict[str, float]) -> str:
    details = []
    details.append(f"Energy Efficiency: {analysis_result['energy_efficiency']:.2f}")
    details.append("- Evaluates the use of efficient loop constructs, list comprehensions, and generator expressions.")
    details.append("- Checks for lazy evaluation techniques.")
    
    details.append(f"\nResource Usage: {analysis_result['resource_usage']:.2f}")
    details.append("- Analyzes memory usage and resource management practices.")
    details.append("- Evaluates the use of 'with' statements and set operations.")
    
    details.append(f"\nCode Optimizations: {analysis_result['code_optimizations']:.2f}")
    details.append("- Examines string operations and dictionary access methods.")
    details.append("- Looks for use of efficient data structures and operations.")
    
    details.append(f"\nCustom Rules: {analysis_result['custom_rules']:.2f}")
    details.append("- Applies user-defined custom rules for project-specific optimizations.")
    
    return "\n".join(details)

def generate_report(project_results: Dict[str, Dict[str, float]], output_file: str):
    """
    Generate a detailed report of the project analysis.
    """
    report = {
        'project_score': get_project_eco_score(project_results),
        'file_scores': {file: get_eco_score(result) for file, result in project_results.items()},
        'detailed_results': project_results,
    }
    
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

def load_config(config_file: str) -> Dict:
    """
    Load configuration from a JSON file.
    """
    with open(config_file, 'r') as f:
        return json.load(f)

def analyze_with_git_history(repo_path: str, num_commits: int = 5) -> List[Tuple[str, float]]:
    """
    Analyze the eco-score of the project over the last n commits.
    """
    try:
        from git import Repo
    except ImportError:
        print("GitPython is not installed. Please install it to use this feature.")
        return []

    repo = Repo(repo_path)
    commits = list(repo.iter_commits('master', max_count=num_commits))
    
    scores = []
    for commit in commits:
        repo.git.checkout(commit.hexsha)
        project_results = analyze_project(repo_path)
        score = get_project_eco_score(project_results)
        scores.append((commit.hexsha[:7], score))
    
    repo.git.checkout('master')
    return scores