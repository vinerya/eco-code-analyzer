import argparse
import sys
import os
import json
from .analyzer import (
    analyze_code,
    analyze_project,
    get_eco_score,
    get_project_eco_score,
    get_improvement_suggestions,
    get_detailed_analysis,
    generate_report,
    load_config,
    analyze_with_git_history
)

def main():
    parser = argparse.ArgumentParser(description="Analyze Python code for ecological impact.")
    parser.add_argument("path", help="Python file or project directory to analyze")
    parser.add_argument("-v", "--verbose", action="store_true", help="Display detailed analysis")
    parser.add_argument("-c", "--config", help="Path to configuration file")
    parser.add_argument("-o", "--output", help="Output file for the report")
    parser.add_argument("-g", "--git", action="store_true", help="Analyze Git history")
    parser.add_argument("-n", "--num-commits", type=int, default=5, help="Number of commits to analyze (default: 5)")
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
                print(f"- {suggestion}")
    
    elif os.path.isdir(args.path):
        project_results = analyze_project(args.path)
        project_score = get_project_eco_score(project_results)
        print(f"Eco-Code Analysis Results for project at {args.path}:")
        print(f"Overall Project Eco-Score: {project_score}")
        
        if args.verbose:
            print("\nFile Scores:")
            for file, result in project_results.items():
                print(f"{file}: {get_eco_score(result):.2f}")
        
        if args.output:
            generate_report(project_results, args.output)
            print(f"\nDetailed report saved to {args.output}")
        
        if args.git:
            print("\nAnalyzing Git history:")
            history_scores = analyze_with_git_history(args.path, args.num_commits)
            for commit, score in history_scores:
                print(f"Commit {commit}: {score:.2f}")
    
    else:
        print(f"Error: {args.path} is not a valid file or directory")
        sys.exit(1)
    
    print("\nTo see a more detailed analysis, run the command with the -v or --verbose flag.")

if __name__ == "__main__":
    main()