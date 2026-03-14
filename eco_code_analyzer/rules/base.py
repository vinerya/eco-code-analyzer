"""
Base classes for the rule system.
"""

import ast
from typing import Dict, Any, List, Callable, Optional, Type
from dataclasses import dataclass, field


@dataclass
class RuleMetadata:
    """Metadata for a rule including description, impact, and references."""
    name: str
    description: str
    category: str
    impact: str  # "high", "medium", "low"
    references: List[str] = field(default_factory=list)  # Research papers or articles supporting this rule
    examples: Dict[str, str] = field(default_factory=dict)  # Good/bad examples


class Rule:
    """Base class for all eco-code rules."""
    metadata: RuleMetadata

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    def check(self, node: ast.AST, context: Dict[str, Any]) -> float:
        """
        Check if the rule applies to this node.
        Returns a score multiplier (< 1.0 for penalties, > 1.0 for rewards).
        """
        raise NotImplementedError("Rule subclasses must implement check method")

    def get_suggestion(self) -> Dict[str, str]:
        """Get improvement suggestion for this rule."""
        return {
            "category": self.metadata.category,
            "suggestion": self.metadata.description,
            "impact": self.metadata.impact,
            "example": next(iter(self.metadata.examples.values())) if self.metadata.examples else "",
            "environmental_impact": "Reduces energy consumption and carbon footprint.",
            "references": ", ".join(self.metadata.references) if self.metadata.references else ""
        }


class RuleRegistry:
    """Registry to manage all eco-code rules."""
    _rules: Dict[str, Dict[str, Type[Rule]]] = {}

    @classmethod
    def register(cls, rule_class: Type[Rule]):
        """Register a rule class."""
        category = rule_class.metadata.category
        if category not in cls._rules:
            cls._rules[category] = {}
        cls._rules[category][rule_class.metadata.name] = rule_class
        return rule_class

    @classmethod
    def get_rules(cls, category: Optional[str] = None) -> Dict[str, Type[Rule]]:
        """Get all rules or rules for a specific category."""
        if category:
            return cls._rules.get(category, {})
        return {name: rule for category in cls._rules.values() for name, rule in category.items()}

    @classmethod
    def create_rule_instances(cls, config: Dict[str, Any]) -> Dict[str, Dict[str, Rule]]:
        """Create instances of all registered rules with the given config."""
        instances = {}
        for category, rules in cls._rules.items():
            instances[category] = {name: rule_class(config) for name, rule_class in rules.items()}
        return instances

    @classmethod
    def get_categories(cls) -> List[str]:
        """Get all rule categories."""
        return list(cls._rules.keys())

    @classmethod
    def reset(cls):
        """Reset the registry. Useful for testing."""
        cls._rules = {}
