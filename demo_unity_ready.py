#!/usr/bin/env python3
"""
Unity-Ready Mesh Generator Demo
This script demonstrates the complete pipeline for generating Unity-ready 3D meshes
with colors, collision, materials, and physics.
"""

from src.mesh_generator import MeshGenerator
import os
import json

def demo_unity_ready_generation():
    """Demonstrate Unity-ready mesh generation with various examples."""
    
    print("🎮 Unity-Ready Mesh Generator Demo")
    print("=" * 50)
    print("This demo showcases the complete Unity export pipeline")
    print("including colors, collision, materials, and physics.")
    print()
    
    # Initialize the mesh generator
    generator = MeshGenerator()
    
    # Create output directory
    os.makedirs('output/demo', exist_ok=True)
    
    # Demo examples
    demo_examples = [
        {
            'name': 'Alpine Mountain',
            'description': 'snow-capped mountain peak with rocky terrain',
            'type': 'mountain_peak',
            'expected_material': 'rock',
            'expected_physics': 'rock'
        },
        {
            'name': 'Dense Forest',
            'description': 'thick forest with tall trees and undergrowth',
            'type': 'environment',
            'expected_material': 'forest',
            'expected_physics': 'grass'
        },
        {
            'name': 'Desert Oasis',
            'description': 'sandy desert with scattered rocks and dunes',
            'type': 'environment',
            'expected_material': 'sand',
            'expected_physics': 'sand'
        },
        {
            'name': 'Crystal Lake',
            'description': 'clear lake surrounded by gentle hills',
            'type': 'environment',
            'expected_material': 'water',
            'expected_physics': 'water'
        },
        {
            'name': 'Rolling Hills',
            'description': 'gentle rolling hills with grass and flowers',
            'type': 'terrain',
            'expected_material': 'terrain',
            'expected_physics': 'grass'
        }
    ]
    
    print(f"Generating {len(demo_examples)} Unity-ready meshes...")
    print()
    
    generated_files = []
    
    for i, example in enumerate(demo_examples, 1):
        print(f"🌍 {i}. {example['name']}")
        print(f"   Description: {example['description']}")
        
        try:
            # Generate the mesh
            mesh, collision_mesh, confidence, material_type, physics_type = generator.generate_mesh(example['description'])
            
            # Create filename
            safe_name = example['name'].lower().replace(' ', '_')
            filename = f"output/demo/{safe_name}.obj"
            
            # Save with Unity optimization
            generator.save_mesh(mesh, collision_mesh, filename, material_type, physics_type)
            
            # Collect file information
            file_info = {
                'name': example['name'],
                'visual_mesh': filename,
                'collision_mesh': filename.replace('.obj', '_collision.obj'),
                'prefab_data': filename.replace('.obj', '_prefab.json'),
                'material_type': material_type,
                'physics_type': physics_type,
                'vertices': len(mesh.vertices),
                'collision_vertices': len(collision_mesh.vertices),
                'confidence': confidence
            }
            
            generated_files.append(file_info)
            
            print(f"   ✅ Generated successfully!")
            print(f"   📊 Stats: {len(mesh.vertices)} vertices, {len(collision_mesh.vertices)} collision vertices")
            print(f"   🎨 Material: {material_type}")
            print(f"   ⚡ Physics: {physics_type}")
            print(f"   📁 Files: {os.path.basename(filename)}")
            print()
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
            print()
    
    # Generate Unity scene file
    generate_unity_scene_file(generated_files)
    
    # Print summary
    print("🎯 Demo Summary")
    print("=" * 30)
    print(f"Successfully generated: {len(generated_files)} Unity-ready meshes")
    print(f"Output location: output/demo/")
    print()
    
    print("📦 Generated Files:")
    for file_info in generated_files:
        print(f"   • {file_info['name']}:")
        print(f"     - Visual: {os.path.basename(file_info['visual_mesh'])}")
        print(f"     - Collision: {os.path.basename(file_info['collision_mesh'])}")
        print(f"     - Prefab: {os.path.basename(file_info['prefab_data'])}")
    
    print()
    print("🚀 Unity Import Instructions:")
    print("1. Open Unity and create a new project")
    print("2. Import all .obj files from 'output/demo/' folder")
    print("3. Create materials based on the prefab JSON files")
    print("4. Set up GameObjects with MeshRenderer and MeshCollider")
    print("5. See UNITY_IMPORT_GUIDE.md for detailed instructions")
    print()
    print("🎮 Your Unity-ready meshes are ready to use!")

def generate_unity_scene_file(generated_files):
    """Generate a Unity scene file with all the generated objects."""
    
    scene_data = {
        'name': 'GeneratedTerrainScene',
        'description': 'Unity scene with procedurally generated terrain and environments',
        'objects': [],
        'materials': {},
        'physics_materials': {}
    }
    
    # Add objects to scene
    for file_info in generated_files:
        scene_data['objects'].append({
            'name': file_info['name'],
            'mesh_file': os.path.basename(file_info['visual_mesh']),
            'collision_file': os.path.basename(file_info['collision_mesh']),
            'material': file_info['material_type'],
            'physics_material': file_info['physics_type'],
            'transform': {
                'position': [0, 0, 0],
                'rotation': [0, 0, 0],
                'scale': [1, 1, 1]
            },
            'stats': {
                'vertices': file_info['vertices'],
                'collision_vertices': file_info['collision_vertices'],
                'confidence': file_info['confidence']
            }
        })
    
    # Save scene file
    scene_file = 'output/demo/unity_scene.json'
    with open(scene_file, 'w') as f:
        json.dump(scene_data, f, indent=2)
    
    print(f"📄 Scene file generated: {scene_file}")

def show_material_reference():
    """Show a reference of all available materials and their properties."""
    
    print("\n🎨 Material Reference")
    print("=" * 25)
    
    from utils.unity_utils import create_unity_material, create_unity_physics_material
    
    # Visual materials
    print("Visual Materials:")
    material_types = ['default', 'terrain', 'rock', 'snow', 'water', 'sand', 'forest']
    
    for mat_type in material_types:
        material = create_unity_material(mat_type)
        color = material['color']
        print(f"  {mat_type:10} | Color: RGB({color[0]:.1f}, {color[1]:.1f}, {color[2]:.1f}) | Metallic: {material['metallic']} | Smoothness: {material['smoothness']}")
    
    print("\nPhysics Materials:")
    physics_types = ['default', 'grass', 'rock', 'sand', 'water', 'snow']
    
    for phys_type in physics_types:
        physics_material = create_unity_physics_material(phys_type)
        print(f"  {phys_type:10} | Friction: {physics_material['friction']} | Bounciness: {physics_material['bounciness']}")

def main():
    """Run the Unity-ready demo."""
    
    print("🎮 Unity-Ready Mesh Generator Demo")
    print("Generating Unity-compatible 3D meshes with colors and collision")
    print()
    
    # Show material reference
    show_material_reference()
    
    # Run the demo
    demo_unity_ready_generation()
    
    print("\n🎉 Demo completed successfully!")
    print("Check the 'output/demo/' folder for your Unity-ready meshes.")

if __name__ == "__main__":
    main() 