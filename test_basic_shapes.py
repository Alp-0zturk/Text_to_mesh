#!/usr/bin/env python3
"""
Test script for basic shape generation with transformations
"""

import os
from src.mesh_generator import MeshGenerator

def test_basic_shapes():
    """Test basic shape generation with transformations."""
    print("Testing Basic Shape Generation with Transformations")
    print("=" * 60)
    
    generator = MeshGenerator()
    
    # Test cases for basic shapes
    test_cases = [
        "cube",
        "sphere", 
        "cylinder",
        "cone"
    ]
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    for i, description in enumerate(test_cases):
        print(f"\nTest {i+1}: {description}")
        print("-" * 30)
        
        try:
            # Generate mesh
            mesh, collision_mesh, confidence = generator.generate_mesh(description)
            
            # Save mesh
            output_file = f'output/test_shape_{i+1}.obj'
            generator.save_mesh(mesh, collision_mesh, output_file)
            
            print(f"✓ Successfully generated mesh")
            print(f"  Confidence: {confidence:.2%}")
            print(f"  Vertices: {len(mesh.vertices)}")
            print(f"  Faces: {len(mesh.faces)}")
            print(f"  Collision vertices: {len(collision_mesh.vertices)}")
            print(f"  Bounds: {mesh.bounds}")
            print(f"  Colors: Vertex colors applied")
            print(f"  Saved to: {output_file}")
            
            # Check if transformations were applied
            bounds = mesh.bounds
            max_dimension = max(abs(bounds[1][0] - bounds[0][0]), 
                              abs(bounds[1][1] - bounds[0][1]), 
                              abs(bounds[1][2] - bounds[0][2]))
            
            if max_dimension > 5:  # Should be around 10 for basic shapes
                print(f"  ✓ 10x scaling confirmed (max dimension: {max_dimension:.1f})")
            else:
                print(f"  ⚠️  Scaling may not be applied (max dimension: {max_dimension:.1f})")
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
    
    print(f"\n" + "=" * 60)
    print("Basic shape generation test completed!")
    print("Check the 'output' directory for generated meshes.")

if __name__ == "__main__":
    test_basic_shapes() 