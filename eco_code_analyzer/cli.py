import argparse
import sys
import os
import json
import webbrowser
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
        # You can replace this URL with a real tree-planting organization's donation page
        donation_url = f"https://onetreeplanted.org/products/plant-trees?quantity={trees_to_plant}"
        print(f"Opening donation page to plant {trees_to_plant} trees...")
        webbrowser.open(donation_url)
        print("Thank you for your contribution to a greener environment!")
    else:
        print("No problem. Remember, every small action counts towards a sustainable future!")

def main():
    parser = argparse.ArgumentParser(description="Analyze Python code for ecological impact.")
    parser.add_argument("path", help="Python file or project directory to analyze")
    parser.add_argument("-v", "--verbose", action="store_true", help="Display detailed analysis")
    parser.add_argument("-c", "--config", help="Path to configuration file")
    parser.add_argument("-o", "--output", help="Output file for the report")
    parser.add_argument("-g", "--git", action="store_true", help="Analyze Git history")
    parser.add_argument("-n", "--num-commits", type=int, default=5, help="Number of commits to analyze (default: 5)")
    parser.add_argument("--visualize", action="store_true", help="Generate visualization of eco-score trend")
    parser.add_argument("--contribute", action="store_true", help="Contribute to tree planting based on analysis results")
    args = parser.parse_args()

    if args.config:
        config = load_config(args.config)
    else:
        config = {}

    if os.path.isfile(args.path):
        with open(args.path, 'r') as file:
            code = file.read()
        analysis_result = analyze_code(code)
        eco_score = get_eco_score(analysis_result)
        print(f"Eco-Code Analysis Results for {args.path}:")
        print(f"Overall Eco-Score: {eco_score}")
        
        if args.verbose:
            print("\nDetailed Analysis:")
            print(get_detailed_analysis(analysis_result))
        else:
            print("\nCategory Scores:")
            for category, score in analysis_result.items():
                print(f"{category.replace('_', ' ').title()}: {score:.2f}")
        
        suggestions = get_improvement_suggestions(analysis_result)
        if suggestions:
            print("\nImprovement Suggestions:")
            for suggestion in suggestions:
                print(f"- {suggestion['category']}: {suggestion['suggestion']}")
                print(f"  Impact: {suggestion['impact']}")
                print(f"  Example: {suggestion['example']}")
                print(f"  Environmental Impact: {suggestion['environmental_impact']}")
        
        energy_savings = estimate_energy_savings({'overall_score': eco_score})
        print("\nEstimated Environmental Impact:")
        print(f"Potential Energy Savings: {energy_savings['energy_kwh_per_year']:.2f} kWh/year")
        print(f"Potential CO2 Reduction: {energy_savings['co2_kg_per_year']:.2f} kg CO2/year")
        print(f"Equivalent to planting: {energy_savings['trees_equivalent']:.2f} trees")
        
        if args.contribute:
            contribute_to_tree_planting(energy_savings['trees_equivalent'])
    
    elif os.path.isdir(args.path):
        project_results = analyze_project(args.path)
        project_score = get_project_eco_score(project_results)
        print(f"Eco-Code Analysis Results for project at {args.path}:")
        print(f"Overall Project Eco-Score: {project_score}")
        
        if args.verbose:
            print("\nFile Scores:")
            for file, result in project_results.items():
                if file != 'overall_score':
                    print(f"{file}: {get_eco_score(result):.2f}")
        
        carbon_footprint = calculate_project_carbon_footprint(project_results)
        print(f"\nEstimated Project Carbon Footprint: {carbon_footprint:.2f} kg CO2/year")
        
        energy_savings = estimate_energy_savings(project_results)
        print("\nEstimated Environmental Impact if Optimized:")
        print(f"Potential Energy Savings: {energy_savings['energy_kwh_per_year']:.2f} kWh/year")
        print(f"Potential CO2 Reduction: {energy_savings['co2_kg_per_year']:.2f} kg CO2/year")
        print(f"Equivalent to planting: {energy_savings['trees_equivalent']:.2f} trees")
        
        if args.contribute:
            contribute_to_tree_planting(energy_savings['trees_equivalent'])
        
        if args.output:
            generate_report(project_results, args.output)
            print(f"\nDetailed report saved to {args.output}")
        
        if args.git:
            print("\nAnalyzing Git history:")
            history_scores = analyze_with_git_history(args.path, args.num_commits)
            for commit, score in history_scores:
                print(f"Commit {commit}: {score:.2f}")
            
            if args.visualize:
                vis_output = f"{args.output.rsplit('.', 1)[0] if args.output else 'eco_score_trend'}.png"
                visualize_eco_score_trend(history_scores, vis_output)
                print(f"Eco-score trend visualization saved to {vis_output}")
    
    else:
        print(f"Error: {args.path} is not a valid file or directory")
        sys.exit(1)
    
    print("\nTo see a more detailed analysis, run the command with the -v or --verbose flag.")
    print("Remember, writing eco-friendly code not only improves performance but also reduces your carbon footprint!")
    print("You can contribute to tree planting based on the analysis results by using the --contribute flag.")

if __name__ == "__main__":
    main()