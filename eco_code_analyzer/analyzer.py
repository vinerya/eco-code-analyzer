import ast
import os
import re
import json
from typing import Dict, List, Set, Tuple, Any
from .rules import Rule, RuleRegistry, AnalysisContext
import logging

logger = logging.getLogger(__name__)


def _get_suppressed_rules(code: str) -> Dict[int, Set[str]]:
    """Parse # noqa: eco-RULENAME comments from code.

    Returns a dict mapping line numbers to sets of suppressed rule names.
    A bare '# noqa: eco' suppresses all eco rules on that line.
    """
    suppressions: Dict[int, Set[str]] = {}
    for lineno, line in enumerate(code.splitlines(), 1):
        match = re.search(r'#\s*noqa:\s*eco(?:-(\S+))?', line)
        if match:
            rule_name = match.group(1)
            if rule_name:
                suppressions.setdefault(lineno, set()).add(rule_name)
            else:
                # bare "# noqa: eco" suppresses all rules
                suppressions[lineno] = {'__all__'}
    return suppressions


def _is_suppressed(node: ast.AST, rule_name: str, suppressions: Dict[int, Set[str]]) -> bool:
    """Check if a rule is suppressed for the given node via noqa comment."""
    if not suppressions:
        return False
    lineno = getattr(node, 'lineno', None)
    if lineno is None:
        return False
    suppressed = suppressions.get(lineno, set())
    return '__all__' in suppressed or rule_name in suppressed

def analyze_code(code: str, file_path: str = None, config: Dict[str, Any] = None) -> Dict[str, float]:
    """
    Analyze the given Python code for ecological impact.

    Args:
        code: The Python code to analyze
        file_path: Optional path to the file being analyzed
        config: Optional configuration dictionary

    Returns:
        Dictionary with category scores
    """
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        logger.error(f"Syntax error in code: {e}")
        return {
            'energy_efficiency': 0.0,
            'resource_usage': 0.0,
            'io_efficiency': 0.0,
            'algorithm_efficiency': 0.0,
            'custom_rules': 0.0,
        }

    # Create analysis context
    context = AnalysisContext()
    context.set_code_lines(code)
    if file_path:
        context.set_file_path(file_path)

    # Parse rule suppression comments
    suppressions = _get_suppressed_rules(code)

    # Get disabled rules from config
    disabled_rules = set()
    if config and 'disabled_rules' in config:
        disabled_rules = set(config['disabled_rules'])

    # Create rule instances
    rule_instances = RuleRegistry.create_rule_instances(config or {})

    # Analyze code with each category of rules
    result = {
        'energy_efficiency': analyze_category(tree, context, rule_instances.get('energy_efficiency', {}), suppressions, disabled_rules),
        'resource_usage': analyze_category(tree, context, rule_instances.get('memory_usage', {}), suppressions, disabled_rules),
        'io_efficiency': analyze_category(tree, context, rule_instances.get('io_efficiency', {}), suppressions, disabled_rules),
        'algorithm_efficiency': analyze_category(tree, context, rule_instances.get('algorithm_efficiency', {}), suppressions, disabled_rules),
        'custom_rules': analyze_custom_rules(tree, context, rule_instances, suppressions, disabled_rules),
    }

    return result

def analyze_project(project_path: str, config: Dict[str, Any] = None) -> Dict[str, Dict[str, float]]:
    """
    Analyze all Python files in the given project directory.

    Args:
        project_path: Path to the project directory
        config: Optional configuration dictionary

    Returns:
        Dictionary with file paths as keys and analysis results as values
    """
    project_results = {}
    total_lines = 0
    total_score = 0

    logger.info(f"Analyzing project at {project_path}")

    for root, _, files in os.walk(project_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        code = f.read()

                    logger.info(f"Analyzing file: {file_path}")
                    file_results = analyze_code(code, file_path, config)
                    project_results[file_path] = file_results

                    lines = len(code.splitlines())
                    total_lines += lines
                    total_score += get_eco_score(file_results) * lines
                except Exception as e:
                    logger.error(f"Error analyzing {file_path}: {e}")

    if total_lines > 0:
        project_results['overall_score'] = total_score / total_lines
    else:
        project_results['overall_score'] = 0

    return project_results

def get_eco_score(analysis_result: Dict[str, float]) -> float:
    """
    Calculate an overall eco-score based on the analysis result.

    Args:
        analysis_result: Dictionary with category scores

    Returns:
        Overall eco-score between 0 and 1
    """
    weights = {
        'energy_efficiency': 0.25,
        'resource_usage': 0.25,
        'io_efficiency': 0.2,
        'algorithm_efficiency': 0.2,
        'custom_rules': 0.1,
    }

    score = sum(analysis_result.get(key, 1.0) * weights[key] for key in weights)
    return round(max(0.0, min(1.0, score)), 2)

def get_project_eco_score(project_results: Dict[str, Dict[str, float]]) -> float:
    """
    Calculate an overall eco-score for the entire project.
    """
    return project_results['overall_score']

def analyze_category(tree: ast.AST, context: AnalysisContext, rules: Dict[str, Rule],
                     suppressions: Dict[int, Set[str]] = None,
                     disabled_rules: Set[str] = None) -> float:
    """
    Analyze code with a specific category of rules.

    Args:
        tree: AST of the code
        context: Analysis context
        rules: Dictionary of rules to apply
        suppressions: Per-line rule suppressions from noqa comments
        disabled_rules: Globally disabled rule names from config

    Returns:
        Category score between 0 and 1
    """
    if not rules:
        return 1.0

    suppressions = suppressions or {}
    disabled_rules = disabled_rules or set()

    score = 1.0
    for node in ast.walk(tree):
        for rule in rules.values():
            if rule.metadata.name in disabled_rules:
                continue
            if _is_suppressed(node, rule.metadata.name, suppressions):
                continue
            try:
                score *= rule.check(node, context)
            except Exception as e:
                logger.error(f"Error applying rule {rule.metadata.name}: {e}")

    return round(max(0.0, min(1.0, score)), 2)

def analyze_custom_rules(tree: ast.AST, context: AnalysisContext, rule_instances: Dict[str, Dict[str, Rule]],
                         suppressions: Dict[int, Set[str]] = None,
                         disabled_rules: Set[str] = None) -> float:
    """
    Apply custom rules that don't fit into standard categories.

    Args:
        tree: AST of the code
        context: Analysis context
        rule_instances: Dictionary of rule instances by category
        suppressions: Per-line rule suppressions from noqa comments
        disabled_rules: Globally disabled rule names from config

    Returns:
        Custom rules score between 0 and 1
    """
    custom_rules = rule_instances.get('custom_rules', {})
    if not custom_rules:
        return 1.0

    suppressions = suppressions or {}
    disabled_rules = disabled_rules or set()

    score = 1.0
    for node in ast.walk(tree):
        for rule in custom_rules.values():
            if rule.metadata.name in disabled_rules:
                continue
            if _is_suppressed(node, rule.metadata.name, suppressions):
                continue
            try:
                score *= rule.check(node, context)
            except Exception as e:
                logger.error(f"Error applying custom rule {rule.metadata.name}: {e}")

    return round(max(0.0, min(1.0, score)), 2)

def get_improvement_suggestions(analysis_result: Dict[str, float], config: Dict[str, Any] = None) -> List[Dict[str, str]]:
    """
    Generate improvement suggestions based on the analysis result.

    Args:
        analysis_result: Dictionary with category scores
        config: Optional configuration dictionary

    Returns:
        List of suggestion dictionaries
    """
    suggestions = []
    threshold = 0.7  # Default threshold for suggestions

    if config and 'thresholds' in config:
        threshold = config['thresholds'].get('category_score', 0.7)

    # Create rule instances to get their suggestions
    rule_instances = RuleRegistry.create_rule_instances(config or {})

    # Map result category keys to rule registry category names
    category_to_rule_category = {
        'energy_efficiency': 'energy_efficiency',
        'resource_usage': 'memory_usage',
        'io_efficiency': 'io_efficiency',
        'algorithm_efficiency': 'algorithm_efficiency',
        'custom_rules': 'custom_rules',
    }

    for category_key, rule_category in category_to_rule_category.items():
        if category_key in analysis_result and analysis_result[category_key] < threshold:
            category_rules = rule_instances.get(rule_category, {})
            for rule in category_rules.values():
                suggestions.append(rule.get_suggestion())

    return suggestions

def get_detailed_analysis(analysis_result: Dict[str, float]) -> str:
    """
    Generate a detailed analysis report as a string.

    Args:
        analysis_result: Dictionary with category scores

    Returns:
        Formatted string with detailed analysis
    """
    categories = [
        ('energy_efficiency', 'Energy Efficiency', [
            "Evaluates the use of efficient loop constructs, list comprehensions, and generator expressions.",
            "Checks for lazy evaluation techniques and redundant computations.",
            "Analyzes loop nesting and complexity.",
        ]),
        ('resource_usage', 'Resource Usage', [
            "Analyzes memory usage and resource management practices.",
            "Evaluates the use of context managers and efficient data structures.",
            "Checks for potential memory leaks and global variable usage.",
        ]),
        ('io_efficiency', 'I/O Efficiency', [
            "Examines file, network, and database operations.",
            "Checks for efficient use of caching and bulk operations.",
            "Identifies potential N+1 query problems and repeated I/O operations.",
        ]),
        ('algorithm_efficiency', 'Algorithm Efficiency', [
            "Analyzes time and space complexity of algorithms.",
            "Evaluates data structure selection for operations.",
            "Checks for optimized recursive algorithms and appropriate algorithm selection.",
        ]),
        ('custom_rules', 'Custom Rules', [
            "Applies user-defined custom rules for project-specific optimizations.",
        ]),
    ]

    details = []
    for key, name, descriptions in categories:
        score = analysis_result.get(key, 0)
        if details:
            details.append("")
        details.append(f"{name}: {score:.2f}")
        for desc in descriptions:
            details.append(f"- {desc}")
        impact = 'High' if score >= 0.8 else 'Medium' if score >= 0.6 else 'Low'
        details.append(f"Environmental Impact: {impact}")

    return "\n".join(details)

def generate_report(project_results: Dict[str, Dict[str, float]], output_file: str):
    """
    Generate a detailed report of the project analysis.
    """
    # Aggregate category scores across all files for suggestions
    aggregated = {}
    file_count = 0
    for file, result in project_results.items():
        if file == 'overall_score' or not isinstance(result, dict):
            continue
        file_count += 1
        for key, value in result.items():
            aggregated[key] = aggregated.get(key, 0.0) + value
    if file_count > 0:
        aggregated = {k: v / file_count for k, v in aggregated.items()}

    report = {
        'project_score': get_project_eco_score(project_results),
        'file_scores': {file: get_eco_score(result) for file, result in project_results.items() if file != 'overall_score' and isinstance(result, dict)},
        'detailed_results': project_results,
        'improvement_suggestions': get_improvement_suggestions(aggregated),
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
    Uses git show to read files without checking out commits (non-destructive).
    """
    try:
        from git import Repo
    except ImportError:
        logger.error("GitPython is not installed. Please install it to use this feature.")
        return []

    repo = Repo(repo_path)

    # Detect the default branch
    try:
        default_branch = repo.active_branch.name
    except TypeError:
        default_branch = 'main'

    commits = list(repo.iter_commits(default_branch, max_count=num_commits))

    scores = []
    for commit in commits:
        try:
            # Read Python files from the commit tree without checkout
            commit_score = _analyze_commit_tree(commit.tree, repo_path)
            scores.append((commit.hexsha[:7], commit_score))
        except Exception as e:
            logger.error(f"Error analyzing commit {commit.hexsha[:7]}: {e}")

    return scores


def _analyze_commit_tree(tree, base_path: str) -> float:
    """Analyze all Python files in a git tree object without checkout."""
    total_lines = 0
    total_score = 0.0

    for blob in tree.traverse():
        if blob.type != 'blob' or not blob.path.endswith('.py'):
            continue
        try:
            code = blob.data_stream.read().decode('utf-8')
            file_results = analyze_code(code, blob.path)
            lines = len(code.splitlines())
            total_lines += lines
            total_score += get_eco_score(file_results) * lines
        except Exception:
            continue

    return round(total_score / total_lines, 2) if total_lines > 0 else 0.0

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
