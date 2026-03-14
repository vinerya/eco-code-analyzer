from .analyzer import (
    analyze_code,
    analyze_project,
    get_eco_score,
    get_project_eco_score,
    get_improvement_suggestions,
    get_detailed_analysis,
    generate_report,
    estimate_energy_savings,
    calculate_project_carbon_footprint
)

# Export the rule system
from .rules import (
    Rule,
    RuleMetadata,
    RuleRegistry,
    AnalysisContext,
    PatternDetector
)

__version__ = "0.5.0"
