
# 🌍 **Eco-Code Analyzer** ![Eco-Friendly Badge](https://img.shields.io/badge/Eco-Friendly-green) ![Python](https://img.shields.io/badge/Python-3.x-blue)

Eco-Code Analyzer is a Python library that analyzes code for its ecological impact, providing developers with insights and recommendations to write more environmentally friendly and efficient code. By optimizing code for energy efficiency and resource usage, we can collectively reduce the carbon footprint of our software.

---

## 🛠️ **Installation**

Install Eco-Code Analyzer via pip:

```bash
pip install eco-code-analyzer
```

For development:

```bash
pip install eco-code-analyzer[dev]
```

---

## ✨ **Features**

- ♻️ Analyzes Python code for ecological impact
- 📊 Provides an overall eco-score and a detailed breakdown
- 💡 Offers improvement suggestions with examples and environmental impact estimates
- 🔍 Analyzes entire projects or individual files
- 🌱 Estimates potential energy savings and CO2 reduction
- 🌍 Calculates project carbon footprint
- ⏳ Analyzes Git history to track eco-score over time
- 📈 Generates visualizations of eco-score trends
- ⚙️ Supports custom configuration and rules
- 🌳 Allows users to contribute to tree planting based on analysis results

---

## 🚀 **Usage**

### As a Library

```python
from eco_code_analyzer import analyze_code, get_eco_score, get_improvement_suggestions, estimate_energy_savings

code = """ 
def example_function():
    result = []
    for i in range(100):
        result.append(i * 2)
    return result
"""

analysis_result = analyze_code(code)
eco_score = get_eco_score(analysis_result)
suggestions = get_improvement_suggestions(analysis_result)
energy_savings = estimate_energy_savings({'overall_score': eco_score})

print(f"Eco-Score: {eco_score}")
print("Improvement Suggestions:")
for suggestion in suggestions:
    print(f"- {suggestion['category']}: {suggestion['suggestion']}")
    print(f"  Impact: {suggestion['impact']}")
    print(f"  Example: {suggestion['example']}")
    print(f"  Environmental Impact: {suggestion['environmental_impact']}")

print("
Estimated Environmental Impact if Optimized:")
print(f"Potential Energy Savings: {energy_savings['energy_kwh_per_year']:.2f} kWh/year")
print(f"Potential CO2 Reduction: {energy_savings['co2_kg_per_year']:.2f} kg CO2/year")
print(f"Equivalent to planting: {energy_savings['trees_equivalent']:.2f} trees")
```

### As a Command-Line Tool

Analyze a single file:

```bash
eco-code-analyzer path/to/your/python_file.py
```

Analyze a project directory:

```bash
eco-code-analyzer path/to/your/project/directory -v
```

Generate a detailed report:

```bash
eco-code-analyzer path/to/your/project/directory -o report.json
```

Analyze Git history and visualize eco-score trend:

```bash
eco-code-analyzer path/to/your/project/directory -g -n 10 --visualize
```

Use a custom configuration:

```bash
eco-code-analyzer path/to/your/project/directory -c config.json
```

Contribute to tree planting based on analysis results:

```bash
eco-code-analyzer path/to/your/project/directory --contribute
```

---

## 🌿 **Environmental Impact and Tree Planting**

The Eco-Code Analyzer helps developers understand the environmental impact of their code by:

1. Estimating energy consumption and CO2 emissions for different code constructs
2. Providing an overall eco-score that reflects the code's environmental friendliness
3. Offering specific suggestions to improve code efficiency and reduce energy consumption
4. Calculating potential energy savings and CO2 reduction if the code is optimized
5. Tracking the project's eco-score over time to encourage continuous improvement
6. Estimating the equivalent number of trees that need to be planted to offset the code's environmental impact

By using the Eco-Code Analyzer, developers can:

- Reduce the energy consumption of their applications
- Lower the carbon footprint of their software
- Improve code performance and efficiency
- Raise awareness about the environmental impact of code
- Actively contribute to reforestation efforts based on their code's impact

The new tree planting feature allows users to take immediate action to offset their code's environmental impact. When using the `--contribute` flag, the tool will:

1. Calculate the number of trees equivalent to the potential CO2 reduction
2. Provide an estimated cost for planting these trees
3. Offer the user an option to contribute to a tree planting organization directly from the command line

Remember, every small optimization and contribution counts. By collectively improving our code's eco-friendliness and supporting reforestation efforts, we can make a significant impact on reducing the IT industry's carbon footprint and promoting a healthier planet.

---

## ⚙️ **Configuration**

You can customize the behavior of the Eco-Code Analyzer by providing a JSON configuration file. This includes the ability to adjust weights for different aspects of the analysis and configure the coefficients used in the calculations.

Here's an example configuration file:

```json
{
  "weights": {
    "energy_efficiency": 0.4,
    "resource_usage": 0.3,
    "code_optimizations": 0.2,
    "custom_rules": 0.1
  },
  "thresholds": {
    "eco_score": 0.7,
    "category_score": 0.6
  },
  "custom_rules": [
    {
      "name": "check_api_call_efficiency",
      "weight": 0.05
    }
  ],
  "coefficients": {
    "energy_consumption_per_cpu_cycle": 1e-9,
    "co2_emissions_per_kwh": 0.5,
    "base_energy_consumption_per_year": 100,
    "base_co2_emissions_per_year": 50,
    "trees_equivalent_factor": 2
  }
}
```

In this configuration:

- `weights`: Adjust the importance of different categories in the overall eco-score.
- `thresholds`: Set the levels at which warnings or suggestions are triggered.
- `custom_rules`: Add your own rules or adjust the weight of existing ones.
- `coefficients`: Configure the key assumptions used in environmental impact calculations:
  - `energy_consumption_per_cpu_cycle`: Energy consumed per CPU cycle (in joules)
  - `co2_emissions_per_kwh`: CO2 emitted per kWh of energy (varies by region)
  - `base_energy_consumption_per_year`: Assumed baseline energy consumption for a typical project (in kWh)
  - `base_co2_emissions_per_year`: Assumed baseline CO2 emissions for a typical project (in kg)
  - `trees_equivalent_factor`: Factor used to convert CO2 reduction to equivalent number of trees planted

By adjusting these coefficients, you can tailor the analysis to better match your specific environment or to reflect more recent data on energy consumption and emissions.

---

## 🤝 **Contributing**

Contributions are welcome! Please feel free to submit a Pull Request. Here are some ways you can contribute:

1. Add new rules for detecting eco-unfriendly code patterns
2. Improve the accuracy of energy consumption and CO2 emission estimates
3. Enhance the visualization capabilities
4. Add support for more programming languages
5. Improve documentation and provide usage examples
6. Refine the assumptions and coefficients used in the analysis
7. Expand the tree planting contribution feature with more options and partnerships

---

## 📄 **License**

This project is licensed under the MIT License.

---

## 🌱 **Let's Build a Greener Future, One Line of Code at a Time!**

By using the Eco-Code Analyzer, you're not just improving your code – you're contributing to a more sustainable future for software development and our planet. Together, we can make a significant impact on reducing the environmental footprint of the IT industry and supporting global reforestation efforts. Happy eco-coding!
