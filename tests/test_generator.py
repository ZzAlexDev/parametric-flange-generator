"""
Unit tests for parametric flange generator.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from generator import FlangeParams, generate_flange, export_model
from pathlib import Path

def test_01_default_parameters():
    """Test 1: Model generation with default parameters."""
    params = FlangeParams()
    model = generate_flange(params)
    assert model is not None, "Model should be generated"
    print("✅ Test 1 passed: Default parameters work")

def test_02_parameter_validation():
    """Test 2: Invalid parameters should raise ValueError."""
    try:
        params = FlangeParams(center_hole_diameter=60.0, flange_diameter=50.0)
        generate_flange(params)
        print("❌ Test 2 failed: Should have raised ValueError")
        return False
    except ValueError:
        print("✅ Test 2 passed: Parameter validation works")
        return True

def test_03_varied_hole_counts():
    """Test 3: Test different hole counts (4, 6, 8, 12)."""
    for hole_count in [4, 6, 8, 12]:
        params = FlangeParams(hole_count=hole_count)
        model = generate_flange(params)
        assert model is not None, f"Failed with hole_count={hole_count}"
    print("✅ Test 3 passed: All hole counts work")

def test_04_export_functionality():
    """Test 4: Test model export to STEP/STL."""
    params = FlangeParams()
    model = generate_flange(params)
    
    # Create temp directory for test exports
    test_dir = Path("test_output")
    test_dir.mkdir(exist_ok=True)
    
    # Test export
    try:
        from generator import export_model
        files = export_model(model, "test_flange", test_dir)
        assert files.get('step') is not None
        assert files.get('stl') is not None
        print("✅ Test 4 passed: Export functionality works")
        
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
        return True
    except Exception as e:
        print(f"❌ Test 4 failed: {e}")
        return False

def run_all_tests():
    """Run all tests and report results."""
    print("=" * 50)
    print("Running Parametric Flange Generator Tests")
    print("=" * 50)
    
    results = []
    results.append(test_01_default_parameters())
    results.append(test_02_parameter_validation())
    results.append(test_03_varied_hole_counts())
    results.append(test_04_export_functionality())
    
    print("=" * 50)
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Project is ready.")
    else:
        print("⚠️  Some tests failed. Please check above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)