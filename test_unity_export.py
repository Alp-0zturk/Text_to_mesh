#!/usr/bin/env python3
"""
Test script for Unity-ready mesh generation with materials and physics.
This script demonstrates the complete Unity export pipeline.
"""

from src.mesh_generator import MeshGenerator
import os

def test_unity_export():
    """Test Unity-ready mesh generation with various object types."""
    
    print("=== Unity-Ready Mesh Generation Test ===")
    print("Testing complete Unity export pipeline with materials and physics")
    print()
    
    # Initialize the mesh generator
    generator = MeshGenerator()
    
    # Test cases with different object types
    test_cases = [
        {
            'description': 'tall mountain peak',
            'expected_type': 'mountain_peak',
            'expected_material': 'rock',
            'expected_physics': 'rock'
        },
        {
            'description': 'dense forest with trees',
            'expected_type': 'environment',
            'expected_material': 'forest',
            'expected_physics': 'grass'
        },
        {
            'description': 'desert with sand dunes',
            'expected_type': 'environment',
            'expected_material': 'sand',
            'expected_physics': 'sand'
        },
        {
            'description': 'lake surrounded by terrain',
            'expected_type': 'environment',
            'expected_material': 'water',
            'expected_physics': 'water'
        },
        {
            'description': 'rolling hills landscape',
            'expected_type': 'terrain',
            'expected_material': 'terrain',
            'expected_physics': 'grass'
        },
        {
            'description': 'large cube 5 meters',
            'expected_type': 'cube',
            'expected_material': 'default',
            'expected_physics': 'default'
        }
    ]
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test {i}/{total_tests}: {test_case['description']} ---")
        
        try:
            # Generate the mesh
            mesh, collision_mesh, confidence, material_type, physics_type = generator.generate_mesh(test_case['description'])
            
            # Create filename
            safe_description = "".join(c for c in test_case['description'] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_description = safe_description.replace(' ', '_')
            filename = f"output/test_unity_{safe_description}.obj"
            
            # Save with Unity optimization
            generator.save_mesh(mesh, collision_mesh, filename, material_type, physics_type)
            
            # Verify results
            print(f"✅ Generated successfully!")
            print(f"   - Material: {material_type} (expected: {test_case['expected_material']})")
            print(f"   - Physics: {physics_type} (expected: {test_case['expected_physics']})")
            print(f"   - Confidence: {confidence:.2f}")
            print(f"   - Vertices: {len(mesh.vertices)}")
            print(f"   - Collision vertices: {len(collision_mesh.vertices)}")
            
            # Check if files were created
            visual_file = filename
            collision_file = filename.replace('.obj', '_collision.obj')
            prefab_file = filename.replace('.obj', '_prefab.json')
            
            files_exist = all(os.path.exists(f) for f in [visual_file, collision_file, prefab_file])
            
            if files_exist:
                print(f"   - Files created: ✓")
                successful_tests += 1
            else:
                print(f"   - Files created: ✗")
            
            # Verify material and physics types
            material_match = material_type == test_case['expected_material']
            physics_match = physics_type == test_case['expected_physics']
            
            if material_match and physics_match:
                print(f"   - Material/Physics match: ✓")
            else:
                print(f"   - Material/Physics match: ✗")
                print(f"     Expected: {test_case['expected_material']}/{test_case['expected_physics']}")
                print(f"     Got: {material_type}/{physics_type}")
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
    
    # Summary
    print(f"\n=== Test Summary ===")
    print(f"Successful tests: {successful_tests}/{total_tests}")
    print(f"Success rate: {successful_tests/total_tests*100:.1f}%")
    
    if successful_tests == total_tests:
        print("🎉 All tests passed! Unity-ready meshes generated successfully.")
        print("\nNext steps:")
        print("1. Open Unity and create a new project")
        print("2. Import the .obj files from the 'output' folder")
        print("3. Create materials based on the prefab JSON files")
        print("4. Set up GameObjects with MeshRenderer and MeshCollider")
        print("5. See UNITY_IMPORT_GUIDE.md for detailed instructions")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return successful_tests == total_tests

def test_material_properties():
    """Test material and physics material generation."""
    
    print("\n=== Material Properties Test ===")
    
    from utils.unity_utils import create_unity_material, create_unity_physics_material
    
    # Test material types
    material_types = ['default', 'terrain', 'rock', 'snow', 'water', 'sand', 'forest']
    
    print("Testing material generation:")
    for mat_type in material_types:
        material = create_unity_material(mat_type)
        print(f"  {mat_type}: {material['name']} - Color: {material['color']}")
    
    # Test physics material types
    physics_types = ['default', 'grass', 'rock', 'sand', 'water', 'snow']
    
    print("\nTesting physics material generation:")
    for phys_type in physics_types:
        physics_material = create_unity_physics_material(phys_type)
        print(f"  {phys_type}: {physics_material['name']} - Friction: {physics_material['friction']}, Bounciness: {physics_material['bounciness']}")

def main():
    """Run all Unity export tests."""
    
    print("Unity-Ready Mesh Generator Test Suite")
    print("=====================================")
    
    # Test material properties
    test_material_properties()
    
    # Test Unity export
    success = test_unity_export()
    
    if success:
        print("\n🎯 All Unity export tests completed successfully!")
        print("Your meshes are ready for Unity import with colors and collision!")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")

if __name__ == "__main__":
    main() 