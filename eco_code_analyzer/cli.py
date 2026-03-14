import argparse
import sys
import os
import json
import webbrowser
import logging
from .analyzer import (
    analyze_code,
    analyze_project,
    get_eco_score,
    get_project_eco_score,
    get_improvement_suggestions,
    get_detailed_analysis,
    generate_report,
    load_config,
    analyze_with_git_history,
    visualize_eco_score_trend,
    calculate_project_carbon_footprint,
    estimate_energy_savings
)


def contribute_to_tree_planting(trees_equivalent):
    """
    Open a web page for the user to contribute to tree planting based on the analysis results.
    """
    trees_to_plant = round(trees_equivalent)
    donation_amount = trees_to_plant * 1  # Assuming $1 per tree

    print(f"\nBased on the analysis, you can offset your code's environmental impact by planting {trees_to_plant} trees.")
    print(f"This would cost approximately ${donation_amount}.")

    contribute = input("Would you like to contribute to planting these trees? (yes/no): ").lower()

    if contribute == 'yes':
        donation_url = f"https://onetreeplanted.org/products/plant-trees?quantity={trees_to_plant}"
        print(f"Opening donation page to plant {trees_to_plant} trees...")
        webbrowser.open(donation_url)
        print("Thank you for your contribution to a greener environment!")
    else:
        print("No problem. Remember, every small action counts towards a sustainable future!")


def format_output_json(data: dict) -> str:
    """Format analysis results as JSON."""
    return json.dumps(data, indent=2)


def format_output_markdown(eco_score: float, analysis_result: dict, suggestions: list, energy_savings: dict, file_path: str) -> str:
    """Format analysis results as Markdown."""
    lines = [
        f"# Eco-Code Analysis: {file_path}",
        "",
        f"**Overall Eco-Score: {eco_score}**",
        "",
        "## Category Scores",
        "",
        "| Category | Score | Rating |",
        "|----------|-------|--------|",
    ]
    for category, score in analysis_result.items():
        rating = "Good" if score >= 0.8 else "Fair" if score >= 0.6 else "Needs Improvement"
        lines.append(f"| {category.replace('_', ' ').title()} | {score:.2f} | {rating} |")

    if suggestions:
        lines.append("")
        lines.append("## Improvement Suggestions")
        lines.append("")
        for s in suggestions:
            lines.append(f"### {s['category']}")
            lines.append(f"- **Suggestion:** {s['suggestion']}")
            lines.append(f"- **Impact:** {s['impact']}")
            if s.get('example'):
                lines.append(f"- **Example:**")
                lines.append(f"  ```python")
                lines.append(f"  {s['example'].strip()}")
                lines.append(f"  ```")
            lines.append("")

    lines.extend([
        "## Environmental Impact",
        "",
        f"- Potential Energy Savings: {energy_savings['energy_kwh_per_year']:.2f} kWh/year",
        f"- Potential CO2 Reduction: {energy_savings['co2_kg_per_year']:.2f} kg CO2/year",
        f"- Equivalent to planting: {energy_savings['trees_equivalent']:.2f} trees",
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze Python code for ecological impact.")
    parser.add_argument("path", help="Python file or project directory to analyze")
    parser.add_argument("-v", "--verbose", action="store_true", help="Display detailed analysis")
    parser.add_argument("-c", "--config", help="Path to configuration file")
    parser.add_argument("-o", "--output", help="Output file for the report")
    parser.add_argument("-f", "--format", choices=["text", "json", "markdown"], default="text",
                        help="Output format (default: text)")
    parser.add_argument("-g", "--git", action="store_true", help="Analyze Git history")
    parser.add_argument("-n", "--num-commits", type=int, default=5, help="Number of commits to analyze (default: 5)")
    parser.add_argument("--visualize", action="store_true", help="Generate visualization of eco-score trend")
    parser.add_argument("--contribute", action="store_true", help="Contribute to tree planting based on analysis results")
    parser.add_argument("--threshold", type=float, default=0.0,
                        help="Minimum eco-score threshold; exit with code 1 if below (useful for CI)")
    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Load configuration
    config = {}
    if args.config:
        try:
            config = load_config(args.config)
            logger.info(f"Loaded configuration from {args.config}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            print(f"Error loading configuration: {e}", file=sys.stderr)

    eco_score = 0.0

    if os.path.isfile(args.path):
        try:
            with open(args.path, 'r', encoding='utf-8') as file:
                code = file.read()
            logger.info(f"Analyzing file: {args.path}")
            analysis_result = analyze_code(code, args.path, config)
        except Exception as e:
            logger.error(f"Error analyzing file: {e}")
            print(f"Error analyzing file: {e}", file=sys.stderr)
            sys.exit(2)

        eco_score = get_eco_score(analysis_result)
        suggestions = get_improvement_suggestions(analysis_result, config)
        energy_savings = estimate_energy_savings({'overall_score': eco_score})

        if args.format == "json":
            output = format_output_json({
                "file": args.path,
                "eco_score": eco_score,
                "category_scores": analysis_result,
                "suggestions": suggestions,
                "energy_savings": energy_savings,
            })
            print(output)
        elif args.format == "markdown":
            output = format_output_markdown(eco_score, analysis_result, suggestions, energy_savings, args.path)
            print(output)
        else:
            print(f"Eco-Code Analysis Results for {args.path}:")
            print(f"Overall Eco-Score: {eco_score}")

            if args.verbose:
                print("\nDetailed Analysis:")
                print(get_detailed_analysis(analysis_result))
            else:
                print("\nCategory Scores:")
                for category, score in analysis_result.items():
                    print(f"  {category.replace('_', ' ').title()}: {score:.2f}")

            if suggestions:
                print("\nImprovement Suggestions:")
                for suggestion in suggestions:
                    print(f"- {suggestion['category']}: {suggestion['suggestion']}")
                    print(f"  Impact: {suggestion['impact']}")
                    if suggestion.get('example'):
                        print(f"  Example: {suggestion['example']}")
                    if suggestion.get('environmental_impact'):
                        print(f"  Environmental Impact: {suggestion['environmental_impact']}")

            print("\nEstimated Environmental Impact:")
            print(f"  Potential Energy Savings: {energy_savings['energy_kwh_per_year']:.2f} kWh/year")
            print(f"  Potential CO2 Reduction: {energy_savings['co2_kg_per_year']:.2f} kg CO2/year")
            print(f"  Equivalent to planting: {energy_savings['trees_equivalent']:.2f} trees")

        if args.contribute:
            contribute_to_tree_planting(energy_savings['trees_equivalent'])

    elif os.path.isdir(args.path):
        logger.info(f"Analyzing project directory: {args.path}")
        project_results = analyze_project(args.path, config)
        eco_score = get_project_eco_score(project_results)

        if args.format == "json":
            output = format_output_json({
                "project": args.path,
                "eco_score": eco_score,
                "file_scores": {f: get_eco_score(r) for f, r in project_results.items() if f != 'overall_score' and isinstance(r, dict)},
                "energy_savings": estimate_energy_savings(project_results),
                "carbon_footprint": calculate_project_carbon_footprint(project_results),
            })
            print(output)
        else:
            print(f"Eco-Code Analysis Results for project at {args.path}:")
            print(f"Overall Project Eco-Score: {eco_score}")

            if args.verbose:
                print("\nFile Scores:")
                for file, result in project_results.items():
                    if file != 'overall_score' and isinstance(result, dict):
                        print(f"  {file}: {get_eco_score(result):.2f}")

            carbon_footprint = calculate_project_carbon_footprint(project_results)
            print(f"\nEstimated Project Carbon Footprint: {carbon_footprint:.2f} kg CO2/year")

            energy_savings = estimate_energy_savings(project_results)
            print("\nEstimated Environmental Impact if Optimized:")
            print(f"  Potential Energy Savings: {energy_savings['energy_kwh_per_year']:.2f} kWh/year")
            print(f"  Potential CO2 Reduction: {energy_savings['co2_kg_per_year']:.2f} kg CO2/year")
            print(f"  Equivalent to planting: {energy_savings['trees_equivalent']:.2f} trees")

        if args.contribute:
            energy_savings = estimate_energy_savings(project_results)
            contribute_to_tree_planting(energy_savings['trees_equivalent'])

        if args.output:
            generate_report(project_results, args.output)
            print(f"\nDetailed report saved to {args.output}")

        if args.git:
            print("\nAnalyzing Git history:")
            history_scores = analyze_with_git_history(args.path, args.num_commits)
            for commit, score in history_scores:
                print(f"  Commit {commit}: {score:.2f}")

            if args.visualize and history_scores:
                vis_output = f"{args.output.rsplit('.', 1)[0] if args.output else 'eco_score_trend'}.png"
                visualize_eco_score_trend(history_scores, vis_output)
                print(f"Eco-score trend visualization saved to {vis_output}")

    else:
        print(f"Error: {args.path} is not a valid file or directory", file=sys.stderr)
        sys.exit(2)

    # Threshold check for CI/CD integration
    if args.threshold > 0 and eco_score < args.threshold:
        print(f"\nEco-score {eco_score} is below threshold {args.threshold}", file=sys.stderr)
        sys.exit(1)

    if args.format == "text":
        print("\nTo see a more detailed analysis, run with the -v or --verbose flag.")
        print("Use --format json or --format markdown for alternative output formats.")


if __name__ == "__main__":
    main()
