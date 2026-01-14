# Parametric Flange Generator

**A demonstration project for script-based CAD automation using CadQuery.**

This project generates parametric 3D flange models with customizable dimensions. It serves as a practical example of how code can automate CAD design, a key skill for creating datasets for AI/ML in engineering.

## 🎯 Project Purpose

This repository was created as a learning project to demonstrate proficiency with CadQuery and understanding of parametric modeling principles for the **Python Developer (CAD Automation)** position.

**Key concepts demonstrated:**
- **Parametric Design**: All dimensions (diameter, hole count, thickness) are variables.
- **Algorithmic Geometry**: Hole positions are calculated mathematically, not placed manually.
- **CAD Automation**: Batch generation of model variations with different parameters.
- **Data Export**: Models are exported in standard CAD formats (STEP, STL) ready for use in AI training pipelines.

## 📁 Project Structure


```markdown
parametric-flange-generator/
│
├── .gitignore              # Specifies files and directories to exclude from version control
├── README.md               # Primary project documentation and user guide
├── requirements.txt        # Python package dependencies (PINNED VERSION - COMMIT THIS)
├── LICENSE                 # Software license (e.g., MIT, Apache 2.0) - RECOMMENDED
│
├── generator.py            # CORE MODULE: Parametric model generator and FlangeParams class
├── run_in_cq_editor.py     # ENTRY POINT: Script for model visualization in CQ-editor GUI
├── generate_dataset.py     # CLI TOOL: Command-line interface for batch dataset generation
│
├── examples/               # Example configurations and output demonstrations
│   ├── .gitkeep            # Keeps this directory in Git (empty placeholder)
│   ├── parameters.json     # Example parameter sets for different flange variants
│   └── basic_usage.ipynb   # (FUTURE) Jupyter notebook with interactive examples
│
├── tests/                  # Unit and integration tests
│   ├── .gitkeep            # Keeps this directory in Git
│   ├── test_generator.py   # Tests for the core generator module
│   └── test_parameters.py  # Tests for parameter validation and dataclasses
│
├── docs/                   # Project documentation
│   ├── .gitkeep            # Keeps this directory in Git
│   ├── api.md              # API reference for all public functions and classes
│   └── development.md      # Guidelines for contributors and developers
│
├── scripts/                # Utility and maintenance scripts (OPTIONAL)
│   ├── .gitkeep            # Keeps this directory in Git
│   ├── benchmark.py        # Performance testing and profiling
│   └── cleanup.py          # Utility for removing generated files
│
├── output/                 # GENERATED - Default directory for single model exports (IGNORED BY GIT)
├── ai_dataset_*/           # GENERATED - Timestamped directories for datasets (IGNORED BY GIT)
└── .venv/                  # GENERATED - Python virtual environment (IGNORED BY GIT)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- CadQuery (installed automatically via requirements.txt)

### Installation & Usage

1. **Clone the repository**
   ```bash
   git clone https://github.com/ZzAlexDev/parametric-flange-generator/parametric-flange-generator.git
   cd parametric-flange-generator
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the generator**
   ```bash
   python generator.py
   ```
   This will create two example models in the `examples/` directory.

### Basic Usage Example

```python
from generator import generate_flange, export_model

# Generate a custom flange
my_flange = generate_flange(
    flange_diameter=60.0,
    flange_thickness=10.0,
    hole_count=4,
    hole_diameter=6.0
)

# Export to STEP format
export_model(my_flange, "my_custom_flange", "STEP")
```

## 🔧 Key Parameters

All dimensions are in millimeters:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `flange_diameter` | Outer diameter of the flange | 50.0 mm |
| `flange_thickness` | Thickness | 8.0 mm |
| `hole_count` | Number of bolt holes | 6 |
| `hole_diameter` | Diameter of each bolt hole | 5.5 mm |
| `center_hole_diameter` | Diameter of center hole | 12.0 mm |

## 📊 Example Outputs

### Default Flange
![Default Flange](https://github.com/ZzAlexDev/parametric-flange-generator/examples/flange_default.png)
*Default parameters: 50mm diameter, 6 holes*

### Custom Flange
![Custom Flange](https://github.com/ZzAlexDev/parametric-flange-generator/examples/flange_custom.png)
*Custom parameters: 80mm diameter, 8 holes*

## 🔄 Extending the Project

This generator can be easily modified to:

1. **Add new features**: Chamfers, fillets, mounting slots, etc.
2. **Create variations**: Use loops to generate hundreds of variations for datasets.
3. **Integrate with pipelines**: Add hooks for automated quality checks or AI training.

Example: Generating a dataset of 100 variations:
```python
import random

for i in range(100):
    random_flange = generate_flange(
        flange_diameter=random.uniform(40, 80),
        hole_count=random.choice([4, 6, 8]),
        # ... other random parameters
    )
    export_model(random_flange, f"dataset/flange_{i:03d}", "STEP")
```

## 🛠️ Technologies Used

- **CadQuery 2.4+**: Parametric CAD scripting library
- **Python 3.8+**: Core programming language
- **STEP/STL Formats**: Industry-standard 3D model formats

## 🤝 Connect

**Created by:** [ZzAlexDev]  
**Purpose:** Demonstration project for CAD automation and parametric design  
**LinkedIn:** [ZzAlexDev]  
**Email:** [ZzAlexDev]

*This project is actively maintained as part of my professional development in CAD automation and AI/ML data pipeline engineering.*


### 4. Пример конфигурации (`examples/parameters.json`)

```json
{
    "flange_diameter": 70.0,
    "flange_thickness": 10.0,
    "hole_count": 4,
    "hole_diameter": 8.0,
    "center_hole_diameter": 15.0,
    "output_format": "STEP"
}
```
