#!/usr/bin/env python3
"""
Enhanced Terrain Generator Demo
Demonstrates the new terrain and environment generation capabilities
"""

import os
import time
from src.mesh_generator import MeshGenerator
from utils.terrain_utils import TerrainUtils

def demo_basic_terrain():
    """Demonstrate basic terrain generation."""
    print("🌄 Basic Terrain Generation Demo")
    print("=" * 50)
    
    generator = MeshGenerator()
    
    terrains = [
        ("Mountain Peak", "a tall mountain peak"),
        ("Rolling Hills", "rolling hills landscape"),
        ("Deep Valley", "deep valley with river"),
        ("Plateau", "flat plateau landscape"),
        ("Canyon", "canyon with steep walls")
    ]
    
    os.makedirs('output/demo', exist_ok=True)
    
    for name, description in terrains:
        print(f"\n🏔️  Generating: {name}")
        print(f"Description: {description}")
        
        start_time = time.time()
        mesh, confidence = generator.generate_mesh(description)
        generation_time = time.time() - start_time
        
        output_file = f'output/demo/{name.lower().replace(" ", "_")}.obj'
        generator.save_mesh(mesh, output_file)
        
        print(f"✓ Generated in {generation_time:.2f}s")
        print(f"  Confidence: {confidence:.2%}")
        print(f"  Vertices: {len(mesh.vertices):,}")
        print(f"  Faces: {len(mesh.faces):,}")
        print(f"  Saved to: {output_file}")

def demo_environments():
    """Demonstrate environment generation."""
    print("\n🌲 Environment Generation Demo")
    print("=" * 50)
    
    generator = MeshGenerator()
    
    environments = [
        ("Forest", "dense forest with trees"),
        ("Desert", "desert with sand dunes"),
        ("Lake", "lake surrounded by terrain"),
        ("Alpine", "alpine forest with rocky outcrops")
    ]
    
    for name, description in environments:
        print(f"\n🌳 Generating: {name}")
        print(f"Description: {description}")
        
        start_time = time.time()
        mesh, confidence = generator.generate_mesh(description)
        generation_time = time.time() - start_time
        
        output_file = f'output/demo/{name.lower()}_environment.obj'
        generator.save_mesh(mesh, output_file)
        
        print(f"✓ Generated in {generation_time:.2f}s")
        print(f"  Confidence: {confidence:.2%}")
        print(f"  Vertices: {len(mesh.vertices):,}")
        print(f"  Faces: {len(mesh.faces):,}")
        print(f"  Saved to: {output_file}")

def demo_advanced_features():
    """Demonstrate advanced terrain features."""
    print("\n🔧 Advanced Features Demo")
    print("=" * 50)
    
    terrain_utils = TerrainUtils()
    
    # Generate heightmap
    print("📊 Generating heightmap...")
    heightmap = terrain_utils.generate_heightmap(
        width=200, height=200, 
        scale=50, octaves=6, 
        terrain_type='mountain'
    )
    
    # Save heightmap visualization
    heightmap_file = 'output/demo/heightmap.png'
    terrain_utils.save_heightmap_as_image(heightmap, heightmap_file)
    print(f"✓ Heightmap saved to: {heightmap_file}")
    
    # Apply erosion
    print("🌊 Applying erosion...")
    eroded_heightmap = terrain_utils.apply_erosion(heightmap, iterations=50)
    
    # Save eroded heightmap
    eroded_file = 'output/demo/eroded_heightmap.png'
    terrain_utils.save_heightmap_as_image(eroded_heightmap, eroded_file)
    print(f"✓ Eroded heightmap saved to: {eroded_file}")
    
    # Generate slope map
    print("📐 Generating slope map...")
    slope_map = terrain_utils.generate_slope_map(heightmap)
    slope_file = 'output/demo/slope_map.png'
    terrain_utils.save_heightmap_as_image(slope_map, slope_file, colormap='viridis')
    print(f"✓ Slope map saved to: {slope_file}")

def demo_parameter_extraction():
    """Demonstrate parameter extraction from text."""
    print("\n📝 Parameter Extraction Demo")
    print("=" * 50)
    
    generator = MeshGenerator()
    
    test_descriptions = [
        "mountain 100 meters wide high resolution",
        "forest 50 meters tall",
        "desert landscape 200 meters across",
        "small hills 25 meters wide",
        "large valley 150 meters deep"
    ]
    
    for description in test_descriptions:
        print(f"\n🔍 Analyzing: {description}")
        
        # Process text to extract parameters
        result = generator.text_processor.process_text(description)
        
        print(f"  Detected shape: {result['shape']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"  Parameters:")
        for key, value in result['parameters'].items():
            if key in ['width', 'height', 'size', 'resolution']:
                print(f"    {key}: {value}")
        print(f"  Is terrain: {result.get('is_terrain', False)}")

def demo_performance_comparison():
    """Compare performance of different terrain types."""
    print("\n⚡ Performance Comparison Demo")
    print("=" * 50)
    
    generator = MeshGenerator()
    
    terrain_types = [
        ("Basic Mountain", "mountain"),
        ("Detailed Mountain", "mountain high resolution"),
        ("Large Mountain", "mountain 200 meters wide"),
        ("Forest Environment", "forest with trees"),
        ("Desert Environment", "desert with dunes")
    ]
    
    results = []
    
    for name, description in terrain_types:
        print(f"\n⏱️  Testing: {name}")
        
        start_time = time.time()
        mesh, confidence = generator.generate_mesh(description)
        generation_time = time.time() - start_time
        
        results.append({
            'name': name,
            'time': generation_time,
            'vertices': len(mesh.vertices),
            'faces': len(mesh.faces),
            'confidence': confidence
        })
        
        print(f"  Time: {generation_time:.2f}s")
        print(f"  Vertices: {len(mesh.vertices):,}")
        print(f"  Faces: {len(mesh.faces):,}")
    
    # Summary
    print(f"\n📊 Performance Summary:")
    print(f"{'Terrain Type':<20} {'Time (s)':<10} {'Vertices':<10} {'Faces':<10}")
    print("-" * 60)
    for result in results:
        print(f"{result['name']:<20} {result['time']:<10.2f} {result['vertices']:<10,} {result['faces']:<10,}")

def main():
    """Run all demos."""
    print("🎮 Enhanced Terrain Generator Demo")
    print("=" * 60)
    print("This demo showcases the new terrain and environment generation capabilities.")
    print("All generated files will be saved to the 'output/demo' directory.")
    
    # Create output directory
    os.makedirs('output/demo', exist_ok=True)
    
    # Run demos
    demo_basic_terrain()
    demo_environments()
    demo_advanced_features()
    demo_parameter_extraction()
    demo_performance_comparison()
    
    print(f"\n🎉 Demo completed!")
    print(f"Check the 'output/demo' directory for all generated files.")
    print(f"\nGenerated files:")
    
    # List generated files
    demo_files = os.listdir('output/demo')
    for file in sorted(demo_files):
        file_path = os.path.join('output/demo', file)
        size = os.path.getsize(file_path)
        if size > 1024*1024:
            size_str = f"{size/(1024*1024):.1f}MB"
        else:
            size_str = f"{size/1024:.1f}KB"
        print(f"  📁 {file} ({size_str})")

if __name__ == "__main__":
    main() 