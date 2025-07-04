import os
from src.mesh_generator import MeshGenerator

def main():
    print("=== AI-Powered Text to 3D Mesh Generator with Intelligent Coloring ===")
    print("Generate photorealistic 3D meshes from text descriptions")
    print("Powered by Shap-E, BERT models, and advanced mesh analysis")
    print("\nCapabilities:")
    print("- Handles complex, detailed scene descriptions")
    print("- Intelligent semantic mesh analysis and segmentation")
    print("- Automatic color application based on detected features")
    print("- Supports multiple environment types in one scene")
    print("- Generates high-quality meshes with materials")
    print("- Creates Unity-ready assets with collision")
    print("- Detailed analysis and color information export")
    print()
    
    # Initialize the mesh generator
    print("Initializing AI models...")
    generator = MeshGenerator()
    print("Ready to generate!")
    
    while True:
        # Get user input
        print("\nExample prompts:")
        print("1. Complex landscape:")
        print("   'Iceland summer landscape with foggy morning mood, aqua hot springs")
        print("    and lupine flowers near highland mountains at sunrise'")
        print("\n2. Detailed environment:")
        print("   'Ancient forest clearing with moss-covered stones, morning mist")
        print("    floating between old trees, and a small stream nearby'")
        print("\n3. Mixed scene:")
        print("   'Desert oasis with palm trees around a clear blue pool,")
        print("    surrounded by golden sand dunes under the evening sky'")
        print("\nTips:")
        print("- Include environmental details (time of day, weather, mood)")
        print("- Describe materials and textures")
        print("- Mention colors and lighting")
        print("- Combine multiple elements (water, vegetation, terrain)")
        
        text_description = input("\nEnter your description (or 'quit' to exit): ").strip()
        
        if text_description.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not text_description:
            print("Please enter a description.")
            continue
        
        try:
            # Generate the mesh with intelligent analysis and coloring
            print(f"\nGenerating: '{text_description}'")
            mesh, collision_mesh, confidence, material_type, physics_type, analysis_results, color_results = generator.generate_mesh(text_description)
            
            # Create a more descriptive filename from the first few words
            words = text_description.split()[:3]  # Take first three words
            filename = '_'.join(word.strip('_,. ').lower() for word in words)
            filename = f"output/generated_{filename}.obj"
            
            # Save the mesh with Unity optimization and intelligent coloring
            generator.save_mesh(mesh, collision_mesh, filename, material_type, physics_type, analysis_results, color_results)
            
            print(f"\n✅ Successfully generated Unity-ready mesh with intelligent coloring!")
            print(f"Confidence: {confidence:.2f}")
            print(f"Environment: {color_results['environment_type']}")
            print(f"Semantic regions detected: {color_results['color_info']['unique_semantics']}")
            
            # Display color categories
            color_categories = list(color_results['color_info']['color_legend'].keys())
            print(f"Color categories applied: {', '.join(color_categories)}")
            
            print(f"\nFiles created in 'output/' directory:")
            print(f"- Main mesh: {os.path.basename(filename)}")
            print(f"- Collision mesh: {os.path.basename(filename).replace('.obj', '_collision.obj')}")
            print(f"- Unity prefab: {os.path.basename(filename).replace('.obj', '_prefab.json')}")
            print(f"- Color information: {os.path.basename(filename).replace('.obj', '_color_info.json')}")
            print(f"- Color legend: {os.path.basename(filename).replace('.obj', '_color_legend.png')}")
            print(f"- Mesh analysis: {os.path.basename(filename).replace('.obj', '_analysis.json')}")
            
            if color_results.get('texture_map') is not None:
                print(f"- Texture map: {os.path.basename(filename).replace('.obj', '_texture.png')}")
            
            print("\nReady to import into Unity with:")
            print("- Intelligent semantic vertex colors")
            print("- Photorealistic materials and textures")
            print("- Optimized collision meshes")
            print("- Physics properties")
            print("- Unity-ready transformations")
            print("- Detailed color and analysis information")
            
        except Exception as e:
            print(f"\n❌ Error generating mesh: {str(e)}")
            print("\nTroubleshooting tips:")
            print("1. Try breaking down very long descriptions into shorter ones")
            print("2. Focus on the most important elements first")
            print("3. Make sure the AI models are properly loaded")
            print("4. Check if you have enough GPU memory available")

if __name__ == "__main__":
    main()
