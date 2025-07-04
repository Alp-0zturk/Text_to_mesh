#!/usr/bin/env python3
"""
Test script for terrain generation capabilities
"""

import os
from src.mesh_generator import MeshGenerator

def test_terrain_generation():
    """Test various terrain generation scenarios."""
    print("Testing Terrain Generation Capabilities")
    print("=" * 50)
    
    generator = MeshGenerator()
    
    # Test cases
    test_cases = [
        "a tall mountain peak",
        "rolling hills landscape", 
        "dense forest with trees",
        "desert with sand dunes",
        "lake surrounded by terrain",
        "rocky mountain terrain"
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
            output_file = f'output/test_terrain_{i+1}.obj'
            generator.save_mesh(mesh, collision_mesh, output_file)
            
            print(f"✓ Successfully generated mesh")
            print(f"  Confidence: {confidence:.2%}")
            print(f"  Vertices: {len(mesh.vertices)}")
            print(f"  Faces: {len(mesh.faces)}")
            print(f"  Collision vertices: {len(collision_mesh.vertices)}")
            print(f"  Colors: Vertex colors applied")
            print(f"  Saved to: {output_file}")
            
        except Exception as e:
            print(f"✗ Error: {str(e)}")
    
    print(f"\n" + "=" * 50)
    print("Terrain generation test completed!")
    print("Check the 'output' directory for generated meshes.")

if __name__ == "__main__":
    test_terrain_generation() 