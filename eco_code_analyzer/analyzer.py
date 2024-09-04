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
    total_lines = 0
    total_score = 0
    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    code = f.read()
                file_results = analyze_code(code)
                project_results[file_path] = file_results
                lines = len(code.splitlines())
                total_lines += lines
                total_score += get_eco_score(file_results) * lines
    project_results['overall_score'] = total_score / total_lines if total_lines > 0 else 0
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
    return project_results['overall_score']

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

def get_improvement_suggestions(analysis_result: Dict[str, float]) -> List[Dict[str, str]]:
    suggestions = []
    if analysis_result['energy_efficiency'] < 0.7:
        suggestions.append({
            "category": "Energy Efficiency",
            "suggestion": "Consider using more efficient loop constructs, list comprehensions, and generator expressions.",
            "impact": "High",
            "example": "Replace 'for i in range(len(list)): ...' with 'for item in list: ...'",
            "environmental_impact": "Reduces CPU cycles and energy consumption."
        })
        suggestions.append({
            "category": "Energy Efficiency",
            "suggestion": "Look for opportunities to use lazy evaluation techniques.",
            "impact": "Medium",
            "example": "Use 'any()' or 'all()' functions instead of loops for boolean checks.",
            "environmental_impact": "Minimizes unnecessary computations, saving energy."
        })
    if analysis_result['resource_usage'] < 0.7:
        suggestions.append({
            "category": "Resource Usage",
            "suggestion": "Review your code for potential memory leaks and optimize resource usage.",
            "impact": "High",
            "example": "Use context managers (with statements) for file and network operations.",
            "environmental_impact": "Efficient resource management reduces overall system load and energy consumption."
        })
        suggestions.append({
            "category": "Resource Usage",
            "suggestion": "Use 'with' statements for better resource management, especially with multiple context managers.",
            "impact": "Medium",
            "example": "Use 'with open(file1) as f1, open(file2) as f2:' instead of nested with statements.",
            "environmental_impact": "Ensures proper resource cleanup, reducing system overhead."
        })
    if analysis_result['code_optimizations'] < 0.7:
        suggestions.append({
            "category": "Code Optimizations",
            "suggestion": "Look for opportunities to optimize string operations and use more efficient data structures.",
            "impact": "Medium",
            "example": "Use ''.join(list_of_strings) instead of string concatenation in loops.",
            "environmental_impact": "Reduces memory allocations and CPU usage, lowering energy consumption."
        })
        suggestions.append({
            "category": "Code Optimizations",
            "suggestion": "Use dict.get() method instead of KeyError exception handling for dictionary access.",
            "impact": "Low",
            "example": "Replace 'try: value = dict[key] except KeyError: value = default' with 'value = dict.get(key, default)'",
            "environmental_impact": "Improves code efficiency, slightly reducing CPU usage."
        })
    if analysis_result['custom_rules'] < 0.7:
        suggestions.append({
            "category": "Custom Rules",
            "suggestion": "Review custom rules and consider optimizing code based on their recommendations.",
            "impact": "Varies",
            "example": "Depends on the specific custom rules implemented.",
            "environmental_impact": "Custom rules can target specific optimizations relevant to your project's environmental impact."
        })
    return suggestions

def get_detailed_analysis(analysis_result: Dict[str, float]) -> str:
    details = []
    details.append(f"Energy Efficiency: {analysis_result['energy_efficiency']:.2f}")
    details.append("- Evaluates the use of efficient loop constructs, list comprehensions, and generator expressions.")
    details.append("- Checks for lazy evaluation techniques.")
    details.append(f"Environmental Impact: {'High' if analysis_result['energy_efficiency'] >= 0.8 else 'Medium' if analysis_result['energy_efficiency'] >= 0.6 else 'Low'}")
    
    details.append(f"\nResource Usage: {analysis_result['resource_usage']:.2f}")
    details.append("- Analyzes memory usage and resource management practices.")
    details.append("- Evaluates the use of 'with' statements and set operations.")
    details.append(f"Environmental Impact: {'High' if analysis_result['resource_usage'] >= 0.8 else 'Medium' if analysis_result['resource_usage'] >= 0.6 else 'Low'}")
    
    details.append(f"\nCode Optimizations: {analysis_result['code_optimizations']:.2f}")
    details.append("- Examines string operations and dictionary access methods.")
    details.append("- Looks for use of efficient data structures and operations.")
    details.append(f"Environmental Impact: {'High' if analysis_result['code_optimizations'] >= 0.8 else 'Medium' if analysis_result['code_optimizations'] >= 0.6 else 'Low'}")
    
    details.append(f"\nCustom Rules: {analysis_result['custom_rules']:.2f}")
    details.append("- Applies user-defined custom rules for project-specific optimizations.")
    details.append(f"Environmental Impact: {'High' if analysis_result['custom_rules'] >= 0.8 else 'Medium' if analysis_result['custom_rules'] >= 0.6 else 'Low'}")
    
    return "\n".join(details)

def generate_report(project_results: Dict[str, Dict[str, float]], output_file: str):
    """
    Generate a detailed report of the project analysis.
    """
    report = {
        'project_score': get_project_eco_score(project_results),
        'file_scores': {file: get_eco_score(result) for file, result in project_results.items() if file != 'overall_score'},
        'detailed_results': project_results,
        'improvement_suggestions': get_improvement_suggestions(project_results['overall_score']),
        'estimated_energy_savings': estimate_energy_savings(project_results),
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

def estimate_energy_savings(project_results: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Estimate potential energy savings based on the project's eco-score.
    """
    overall_score = project_results['overall_score']
    potential_improvement = 1 - overall_score
    
    # These are rough estimates and should be refined with more accurate data
    estimated_savings = {
        'energy_kwh_per_year': potential_improvement * 100,  # Assuming 100 kWh/year for a typical project
        'co2_kg_per_year': potential_improvement * 50,  # Assuming 50 kg CO2/year for a typical project
        'trees_equivalent': potential_improvement * 2,  # Assuming 2 trees can offset the CO2 of a typical project
    }
    
    return estimated_savings

def visualize_eco_score_trend(scores: List[Tuple[str, float]], output_file: str):
    """
    Generate a visualization of the eco-score trend over time.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed. Please install it to use this feature.")
        return

    commits, eco_scores = zip(*scores)
    plt.figure(figsize=(10, 6))
    plt.plot(commits, eco_scores, marker='o')
    plt.title('Eco-Score Trend Over Time')
    plt.xlabel('Commits')
    plt.ylabel('Eco-Score')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

def calculate_project_carbon_footprint(project_results: Dict[str, Dict[str, float]]) -> float:
    """
    Calculate an estimated carbon footprint for the project based on its eco-score.
    """
    overall_score = project_results['overall_score']
    # This is a simplified model and should be refined with more accurate data
    base_footprint = 100  # kg CO2 per year for a typical project
    return base_footprint * (1 - overall_score)