"""
Parametric Flange Generator for CAD/AI Datasets
Author: Your Name
Description: Generates a parametric 3D flange model with customizable holes.
Demonstrates CadQuery skills for CAD automation and synthetic data generation.
"""

import cadquery as cq
import json
import math
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple


def generate_flange(
    flange_diameter: float = 50.0,
    flange_thickness: float = 8.0,
    hole_count: int = 6,
    hole_diameter: float = 5.5,
    center_hole_diameter: float = 12.0,
    bolt_circle_percentage: float = 0.65
) -> cq.Workplane:
    """
    Generates a parametric flange model with center hole and bolt circle.

    Args:
        flange_diameter: Outer diameter of the flange in mm.
        flange_thickness: Thickness of the flange in mm.
        hole_count: Number of bolt holes (must be ≥ 1).
        hole_diameter: Diameter of each bolt hole in mm.
        center_hole_diameter: Diameter of the center hole in mm.
        bolt_circle_percentage: Where holes are placed (0.0-1.0 of radius).

    Returns:
        CadQuery Workplane object with the generated 3D model.

    Raises:
        ValueError: If any parameter is invalid.
    """
    # === PARAMETER VALIDATION ===
    if flange_diameter <= 0 or flange_thickness <= 0:
        raise ValueError("Flange diameter and thickness must be positive")
    if hole_count < 1:
        raise ValueError("Must have at least 1 hole")
    if hole_diameter <= 0 or center_hole_diameter <= 0:
        raise ValueError("Hole diameters must be positive")
    if center_hole_diameter >= flange_diameter:
        raise ValueError("Center hole cannot be larger than flange")
    if not 0.1 <= bolt_circle_percentage <= 0.9:
        raise ValueError("Bolt circle percentage must be between 0.1 and 0.9")

    # === 1. CREATE BASE CYLINDER ===
    # Start with XY plane, draw circle, extrude to create solid cylinder
    model = (
        cq.Workplane("XY")
        .circle(flange_diameter / 2)
        .extrude(flange_thickness)
    )

    # === 2. ADD CENTER HOLE ===
    # Select top face, create workplane at its center, cut center hole
    model = (
        model.faces(">Z")
        .workplane(centerOption="CenterOfMass")
        .circle(center_hole_diameter / 2)
        .cutThruAll()
    )

    # === 3. CREATE BOLT HOLE CIRCLE ===
    # Calculate positions using trigonometry for even distribution
    bolt_circle_radius = (flange_diameter * bolt_circle_percentage) / 2

    # Generate (x, y) coordinates for each hole
    hole_positions = []
    for i in range(hole_count):
        angle = 2 * math.pi * i / hole_count  # Equal angles between holes
        x = bolt_circle_radius * math.cos(angle)
        y = bolt_circle_radius * math.sin(angle)
        hole_positions.append((x, y))

    # Create holes at calculated positions
    model = (
        model.faces(">Z")
        .workplane(centerOption="CenterOfMass")
        .pushPoints(hole_positions)
        .circle(hole_diameter / 2)
        .cutThruAll()
    )

    return model


def export_model(
    model: cq.Workplane,
    base_filename: str = "flange_output",
    export_dir: str = "examples",
    formats: List[str] = None
) -> Dict[str, str]:
    """
    Exports model to multiple file formats.

    Args:
        model: CadQuery model to export.
        base_filename: Name without extension.
        export_dir: Directory to save files.
        formats: List of formats to export (default: ['step', 'stl']).

    Returns:
        Dictionary mapping format to file path.
    """
    if formats is None:
        formats = ['step', 'stl']

    # Create export directory if it doesn't exist
    Path(export_dir).mkdir(exist_ok=True)

    exported_files = {}
    for fmt in formats:
        filename = f"{export_dir}/{base_filename}.{fmt.lower()}"
        if fmt.lower() == 'step':
            cq.exporters.export(model, filename)
            exported_files['step'] = filename
        elif fmt.lower() == 'stl':
            cq.exporters.export(model, filename, tolerance=0.01, angularTolerance=0.1)
            exported_files['stl'] = filename
        else:
            print(f"Warning: Unsupported format '{fmt}', skipping")

    return exported_files


def generate_dataset(
    variations: List[Dict[str, Any]],
    base_dir: str = "examples/dataset"
) -> None:
    """
    Generates multiple flange variations for AI training datasets.

    Args:
        variations: List of parameter dictionaries for each variation.
        base_dir: Directory to save the dataset.
    """
    Path(base_dir).mkdir(parents=True, exist_ok=True)

    print(f"Generating {len(variations)} flange variations...")
    for i, params in enumerate(variations):
        try:
            model = generate_flange(**params)
            filename = f"flange_{i:03d}"
            export_model(model, filename, base_dir, ['step'])
            print(f"  Created {filename}.step")
        except Exception as e:
            print(f"  Error generating variation {i}: {e}")


def main() -> None:
    """Main function to demonstrate the generator capabilities."""
    print("=== Parametric Flange Generator ===")

    # === EXAMPLE 1: Default flange ===
    print("\n1. Generating default flange...")
    default_flange = generate_flange()
    export_model(default_flange, "flange_default", "examples")
    print("   ✓ Default flange created")

    # === EXAMPLE 2: Custom flange ===
    print("\n2. Generating custom flange (80mm, 8 holes)...")
    custom_flange = generate_flange(
        flange_diameter=80.0,
        hole_count=8,
        hole_diameter=7.0,
        bolt_circle_percentage=0.7
    )
    export_model(custom_flange, "flange_custom", "examples")
    print("   ✓ Custom flange created")

    # === EXAMPLE 3: Dataset generation ===
    print("\n3. Generating small dataset...")
    dataset_variations = [
        {"flange_diameter": 40, "hole_count": 4},
        {"flange_diameter": 60, "hole_count": 6, "bolt_circle_percentage": 0.6},
        {"flange_diameter": 100, "hole_count": 12, "flange_thickness": 12},
    ]
    generate_dataset(dataset_variations)
    print("   ✓ Dataset generated in 'examples/dataset/'")

    # === EXAMPLE 4: From JSON config ===
    print("\n4. Loading from JSON configuration...")
    try:
        config_path = "examples/parameters.json"
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            json_flange = generate_flange(**config)
            export_model(json_flange, "flange_from_json", "examples")
            print("   ✓ Flange from JSON created")
    except Exception as e:
        print(f"   ✗ Error loading JSON: {e}")

    print("\n=== All operations completed successfully ===")
    print("Check the 'examples/' directory for generated files.")


if __name__ == "__main__":
    main()