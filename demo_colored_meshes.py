#!/usr/bin/env python3
"""
Demo script showcasing the advanced mesh analysis and coloring system.
This script demonstrates how the system can intelligently analyze and color
generated 3D meshes based on semantic segmentation.
"""

import os
import time
from src.mesh_generator import MeshGenerator

def main():
    print("🎨 Advanced 3D Mesh Generation with Intelligent Coloring Demo")
    print("=" * 70)
    print("This demo showcases:")
    print("- Semantic mesh analysis and segmentation")
    print("- Automatic color application based on detected features")
    print("- Multiple environment types and color palettes")
    print("- Detailed analysis and visualization outputs")
    print()
    
    # Initialize the enhanced mesh generator
    print("🚀 Initializing AI models and analysis systems...")
    generator = MeshGenerator()
    print("✅ Ready for intelligent mesh generation!")
    print()
    
    # Demo examples with increasing complexity
    demo_examples = [
        {
            'name': 'Alpine Lake',
            'description': 'serene alpine lake surrounded by snow-capped mountains and pine trees',
            'expected_features': ['water', 'terrain', 'vegetation', 'snow'],
            'environment_type': 'alpine'
        },
        {
            'name': 'Desert Oasis',
            'description': 'lush desert oasis with palm trees around a clear blue pool surrounded by golden sand dunes',
            'expected_features': ['water', 'vegetation', 'terrain'],
            'environment_type': 'desert'
        },
        {
            'name': 'Volcanic Landscape',
            'description': 'dramatic volcanic landscape with black rock formations, steaming hot springs, and sparse vegetation',
            'expected_features': ['rocks', 'water', 'terrain', 'vegetation'],
            'environment_type': 'volcanic'
        },
        {
            'name': 'Forest Clearing',
            'description': 'peaceful forest clearing with moss-covered rocks, a small stream, and ancient trees',
            'expected_features': ['vegetation', 'rocks', 'water', 'terrain'],
            'environment_type': 'forest'
        },
        {
            'name': 'Tropical Paradise',
            'description': 'tropical beach paradise with turquoise water, white sand, palm trees, and coral formations',
            'expected_features': ['water', 'terrain', 'vegetation', 'rocks'],
            'environment_type': 'tropical'
        },
        {
            'name': 'Arctic Tundra',
            'description': 'vast arctic tundra with frozen ground, scattered rocks, patches of hardy vegetation, and ice formations',
            'expected_features': ['terrain', 'rocks', 'vegetation', 'snow'],
            'environment_type': 'tundra'
        }
    ]
    
    print(f"📋 Generating {len(demo_examples)} diverse colored meshes...")
    print()
    
    results_summary = []
    
    for i, example in enumerate(demo_examples, 1):
        print(f"🌍 {i}/{len(demo_examples)}: {example['name']}")
        print(f"   Description: {example['description']}")
        print(f"   Expected environment: {example['environment_type']}")
        print(f"   Expected features: {', '.join(example['expected_features'])}")
        
        try:
            start_time = time.time()
            
            # Generate the colored mesh
            print("   🔄 Generating mesh...")
            result = generator.generate_mesh(example['description'])
            mesh, collision_mesh, confidence, material_type, physics_type, analysis_results, color_results = result
            
            generation_time = time.time() - start_time
            
            # Create filename
            safe_name = example['name'].lower().replace(' ', '_')
            filename = f"output/demo_colored/{safe_name}.obj"
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Save with coloring information
            print("   💾 Saving colored mesh and analysis...")
            generator.save_mesh(
                mesh, collision_mesh, filename, material_type, physics_type, 
                analysis_results, color_results
            )
            
            # Analyze results
            detected_features = list(color_results['color_info']['color_legend'].keys())
            detected_environment = color_results['environment_type']
            semantic_regions = color_results['color_info']['unique_semantics']
            
            # Create result summary
            result_info = {
                'name': example['name'],
                'filename': filename,
                'generation_time': generation_time,
                'confidence': confidence,
                'vertices': len(mesh.verts) if hasattr(mesh, 'verts') else len(mesh.vertices),
                'faces': len(mesh.faces),
                'detected_environment': detected_environment,
                'expected_environment': example['environment_type'],
                'detected_features': detected_features,
                'expected_features': example['expected_features'],
                'semantic_regions': semantic_regions,
                'material_type': material_type,
                'physics_type': physics_type
            }
            
            results_summary.append(result_info)
            
            print(f"   ✅ Success! Generated in {generation_time:.1f}s")
            print(f"   📊 Stats:")
            print(f"      - Vertices: {result_info['vertices']:,}")
            print(f"      - Faces: {result_info['faces']:,}")
            print(f"      - Confidence: {confidence:.2f}")
            print(f"      - Environment: {detected_environment}")
            print(f"      - Semantic regions: {semantic_regions}")
            print(f"      - Detected features: {', '.join(detected_features)}")
            
            # Check accuracy
            feature_matches = set(detected_features) & set(example['expected_features'])
            feature_accuracy = len(feature_matches) / len(example['expected_features']) * 100
            env_match = detected_environment == example['environment_type']
            
            print(f"   🎯 Analysis accuracy:")
            print(f"      - Environment match: {'✓' if env_match else '✗'} ({detected_environment} vs {example['environment_type']})")
            print(f"      - Feature detection: {feature_accuracy:.0f}% ({len(feature_matches)}/{len(example['expected_features'])} matched)")
            print(f"      - Matched features: {', '.join(feature_matches) if feature_matches else 'None'}")
            
            print()
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            print()
            continue
    
    # Generate comprehensive summary report
    if results_summary:
        print("📈 GENERATION SUMMARY REPORT")
        print("=" * 50)
        
        total_time = sum(r['generation_time'] for r in results_summary)
        avg_confidence = sum(r['confidence'] for r in results_summary) / len(results_summary)
        total_vertices = sum(r['vertices'] for r in results_summary)
        total_faces = sum(r['faces'] for r in results_summary)
        
        print(f"✅ Successfully generated: {len(results_summary)}/{len(demo_examples)} meshes")
        print(f"⏱️  Total generation time: {total_time:.1f}s (avg: {total_time/len(results_summary):.1f}s)")
        print(f"🎯 Average confidence: {avg_confidence:.2f}")
        print(f"📊 Total geometry: {total_vertices:,} vertices, {total_faces:,} faces")
        print()
        
        # Environment detection accuracy
        env_matches = sum(1 for r in results_summary if r['detected_environment'] == r['expected_environment'])
        env_accuracy = env_matches / len(results_summary) * 100
        print(f"🌍 Environment detection accuracy: {env_accuracy:.0f}% ({env_matches}/{len(results_summary)})")
        
        # Feature detection analysis
        all_detected_features = set()
        all_expected_features = set()
        for r in results_summary:
            all_detected_features.update(r['detected_features'])
            all_expected_features.update(r['expected_features'])
        
        print(f"🔍 Feature types detected: {len(all_detected_features)} ({', '.join(sorted(all_detected_features))})")
        print(f"🎨 Average semantic regions per mesh: {sum(r['semantic_regions'] for r in results_summary) / len(results_summary):.1f}")
        print()
        
        # Detailed results table
        print("📋 DETAILED RESULTS")
        print("-" * 70)
        print(f"{'Mesh':<20} {'Time':<6} {'Conf':<5} {'Env':<8} {'Regions':<8} {'Features':<15}")
        print("-" * 70)
        
        for r in results_summary:
            env_indicator = "✓" if r['detected_environment'] == r['expected_environment'] else "✗"
            print(f"{r['name']:<20} {r['generation_time']:<6.1f} {r['confidence']:<5.2f} "
                  f"{r['detected_environment']:<7}{env_indicator} {r['semantic_regions']:<8} "
                  f"{', '.join(r['detected_features'][:2]):<15}")
        
        print("-" * 70)
        print()
        
        # File locations
        print("📁 OUTPUT FILES")
        print("All generated files are saved in the 'output/demo_colored/' directory:")
        print()
        for r in results_summary:
            base_name = os.path.basename(r['filename']).replace('.obj', '')
            print(f"🎨 {r['name']}:")
            print(f"   - Visual mesh: {base_name}.obj")
            print(f"   - Collision mesh: {base_name}_collision.obj")
            print(f"   - Color information: {base_name}_color_info.json")
            print(f"   - Color legend: {base_name}_color_legend.png")
            print(f"   - Mesh analysis: {base_name}_analysis.json")
            print(f"   - Unity prefab: {base_name}_prefab.json")
            print()
        
        print("🚀 Ready for Unity import with intelligent semantic coloring!")
        print()
        print("💡 USAGE TIPS:")
        print("- Load the .obj files into Unity or Blender")
        print("- Check the color legend images to understand the semantic regions")
        print("- Use the analysis JSON files for detailed mesh information")
        print("- The vertex colors are embedded in the mesh files")
        print("- Each color represents a different semantic region (water, terrain, vegetation, etc.)")
        
    else:
        print("❌ No meshes were successfully generated.")
        print("Please check your environment and try again.")

if __name__ == "__main__":
    main() 