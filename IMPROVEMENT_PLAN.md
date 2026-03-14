# Eco-Code Analyzer - Comprehensive Improvement Plan

## Overview
After thorough review of the entire codebase (v0.4.0, ~1,600 LOC), this plan covers all identified bugs, code quality issues, missing features, and architectural improvements.

---

## 1. Critical Bugs (Must Fix)

### 1.1 `generate_report()` passes wrong type to `get_improvement_suggestions()`
- **File:** `analyzer.py:285`
- **Issue:** `get_improvement_suggestions(project_results['overall_score'])` passes a `float`, but the function expects a `Dict[str, float]`
- **Fix:** Pass the full analysis result dict, not the scalar score

### 1.2 Score not clamped to [0, 1] range
- **File:** `analyzer.py:121-122`, `analyzer.py:145-153`
- **Issue:** Reward multipliers (>1.0) can push scores above 1.0; compounding penalties can drive scores to near-zero unrealistically
- **Fix:** Clamp final scores: `max(0.0, min(1.0, score))`

### 1.3 `get_eco_score()` mutates input dict
- **File:** `analyzer.py:117-119`
- **Issue:** Adds missing keys directly to the caller's dict, causing side effects
- **Fix:** Work on a copy of the dict or use `.get()` with defaults

### 1.4 `analyze_with_git_history()` is destructive
- **File:** `analyzer.py:310-320`
- **Issue:** Does `git checkout` on actual working tree without stashing changes, hardcodes 'master' branch, no error recovery
- **Fix:** Use `git stash`, detect default branch, use try/finally for cleanup, or use `git show` to read files without checkout

### 1.5 Legacy `rules.py` uses deprecated `ast.Str`
- **File:** `rules.py:14`
- **Issue:** `ast.Str` removed in Python 3.12+; will crash on modern Python
- **Fix:** Use `ast.Constant` with `isinstance(node.value, str)` check

### 1.6 `get_improvement_suggestions()` broken category matching
- **File:** `analyzer.py:215`
- **Issue:** Category matching uses `cat.lower().replace('_', '')` which maps `memory_usage` to `memoryusage` but tries to match `resource_usage` -> `resourceusage`. These will never match.
- **Fix:** Use a proper mapping dict between result keys and rule category names

---

## 2. Code Quality Issues

### 2.1 Remove or integrate legacy `rules.py`
- **Issue:** Legacy `rules.py` (139 lines) duplicates functionality from the new `rules/` package. The legacy module's functions are never called by `analyzer.py`.
- **Fix:** Either remove `rules.py` entirely or extract any unique logic into the new rules system

### 2.2 `logging.basicConfig()` at module level in library code
- **File:** `analyzer.py:9`
- **Issue:** Libraries should never call `logging.basicConfig()` - it interferes with the application's logging configuration
- **Fix:** Remove `basicConfig()` call; let the CLI or consumer configure logging

### 2.3 `setup.py` file handle leak
- **File:** `setup.py:24`
- **Issue:** `open("README.md").read()` never closes the file
- **Fix:** Use a context manager, or better, migrate to `pyproject.toml`

### 2.4 Unused `astroid` dependency
- **File:** `setup.py:13`
- **Issue:** `astroid` is listed as a dependency but never imported anywhere in the codebase
- **Fix:** Remove from dependencies, or add functionality that uses it

### 2.5 `RuleRegistry._rules` shared mutable class variable
- **File:** `rules/base.py:49`
- **Issue:** Dict is shared across all instances and persists between test runs; can cause test pollution
- **Fix:** Add a `reset()` classmethod for testing, or document the singleton behavior

### 2.6 Repetitive code in `get_detailed_analysis()`
- **File:** `analyzer.py:225-275`
- **Issue:** Same pattern repeated 5 times with minor variations
- **Fix:** Refactor into a loop over category definitions

---

## 3. Test Suite (Currently Missing)

### 3.1 Create proper pytest test suite
- **Current state:** `test_code.py` is sample code for manual testing, not actual tests
- **Tests needed:**
  - `tests/test_analyzer.py` - Unit tests for `analyze_code()`, `get_eco_score()`, `analyze_project()`, `generate_report()`, `estimate_energy_savings()`
  - `tests/test_rules_energy.py` - Tests for each energy efficiency rule
  - `tests/test_rules_memory.py` - Tests for each memory usage rule
  - `tests/test_rules_io.py` - Tests for each I/O efficiency rule
  - `tests/test_rules_algorithm.py` - Tests for each algorithm efficiency rule
  - `tests/test_context.py` - Tests for AnalysisContext
  - `tests/test_patterns.py` - Tests for PatternDetector
  - `tests/test_cli.py` - CLI integration tests
  - `tests/conftest.py` - Shared fixtures

### 3.2 Add CI/CD with GitHub Actions
- Workflow for running tests on push/PR
- Matrix testing across Python 3.8-3.12
- Coverage reporting

---

## 4. Feature Improvements

### 4.1 Add rule suppression mechanism
- Allow `# noqa: eco-E001` style inline comments to suppress specific rules
- Config-level rule enable/disable

### 4.2 Add output format options
- Support `--format json|text|html|markdown` in CLI
- HTML report with charts and color-coded scores
- Markdown report for GitHub integration

### 4.3 Add GitHub Actions integration
- Provide a reusable GitHub Action
- PR comment with eco-score diff
- Badge generation for README

### 4.4 Add pre-commit hook support
- `.pre-commit-hooks.yaml` for pre-commit framework integration
- Block commits below a configurable eco-score threshold

### 4.5 Add baseline/comparison mode
- Save baseline scores to a file
- Compare current analysis against baseline
- Show score regressions/improvements

### 4.6 Add `--fix` auto-fix mode
- Automatically apply safe transformations (e.g., loop-to-comprehension)
- Use `--fix --dry-run` to preview changes

### 4.7 Multi-language support groundwork
- Abstract the AST parsing interface
- Add JavaScript/TypeScript analyzer skeleton
- Language detection by file extension

---

## 5. Architecture Improvements

### 5.1 Migrate to `pyproject.toml`
- Replace `setup.py` with modern `pyproject.toml`
- Add proper build system configuration
- Pin dependency version ranges

### 5.2 Add proper CLI exit codes
- Exit 0 for passing score
- Exit 1 for score below threshold
- Useful for CI/CD integration

### 5.3 Improve scoring model
- Current multiplicative model is fragile (compounding drives scores to 0 quickly)
- Consider additive weighted model or logarithmic scaling
- Add per-rule weight configuration

### 5.4 Add caching layer
- Cache analysis results by file hash
- Skip re-analysis of unchanged files in project mode
- Significant speedup for large projects

### 5.5 Make `analyze_with_git_history()` non-destructive
- Use `git show commit:path` to read file contents without checkout
- Or use temporary worktrees (`git worktree add`)

### 5.6 Consolidate energy estimation
- Legacy `rules.py` and `analyzer.py` both have energy estimation
- Unify into a single, well-documented energy model
- Use configurable coefficients from `eco_config.json`

---

## 6. Documentation Improvements

### 6.1 Add inline API documentation
- Ensure all public functions have complete docstrings
- Add type hints to all function signatures

### 6.2 Add CHANGELOG.md
- Track changes per version
- Follow Keep a Changelog format

### 6.3 Improve README
- Add badges (PyPI version, tests, coverage)
- Add architecture diagram
- Add comparison table with similar tools

---

## Priority Order

| Priority | Items | Rationale |
|----------|-------|-----------|
| **P0 - Critical** | 1.1, 1.2, 1.3, 1.5, 1.6 | Bugs that cause crashes or wrong results |
| **P1 - High** | 1.4, 2.1, 2.2, 2.4, 3.1 | Destructive behavior, dead code, no tests |
| **P2 - Medium** | 2.3, 2.5, 2.6, 3.2, 4.1, 4.2, 5.1, 5.2, 5.3 | Quality, CI/CD, usability |
| **P3 - Low** | 4.3-4.7, 5.4-5.6, 6.1-6.3 | Nice-to-have features and polish |

---

## Estimated Scope
- **P0 fixes:** ~200 lines changed
- **P1 fixes + tests:** ~800 lines added/changed
- **P2 improvements:** ~500 lines added/changed
- **P3 features:** ~1500+ lines (significant new functionality)
