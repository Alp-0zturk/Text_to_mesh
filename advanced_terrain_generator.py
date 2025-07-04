#!/usr/bin/env python3
"""
Advanced Terrain Generator with AI Integration
Supports local AI models like Ollama for enhanced terrain generation
"""

import os
import json
import requests
from src.mesh_generator import MeshGenerator
from utils.terrain_utils import TerrainUtils

class AdvancedTerrainGenerator:
    def __init__(self, use_ai=False, ai_endpoint="http://localhost:11434"):
        self.mesh_generator = MeshGenerator()
        self.terrain_utils = TerrainUtils()
        self.use_ai = use_ai
        self.ai_endpoint = ai_endpoint
        
    def check_ai_availability(self):
        """Check if local AI model (Ollama) is available."""
        if not self.use_ai:
            return False
            
        try:
            response = requests.get(f"{self.ai_endpoint}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def enhance_description_with_ai(self, description):
        """Use local AI to enhance the terrain description."""
        if not self.check_ai_availability():
            return description
            
        try:
            # Create a prompt for terrain enhancement
            prompt = f"""
            Enhance this terrain description with more specific details for 3D generation:
            Original: "{description}"
            
            Provide a detailed description including:
            - Terrain type and features
            - Size and scale
            - Environmental elements
            - Specific details for realistic generation
            
            Return only the enhanced description:
            """
            
            # Call Ollama API
            response = requests.post(
                f"{self.ai_endpoint}/api/generate",
                json={
                    "model": "llama3.2",  # or any available model
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                enhanced_description = result.get('response', description).strip()
                print(f"AI Enhanced Description: {enhanced_description}")
                return enhanced_description
            else:
                print("AI enhancement failed, using original description")
                return description
                
        except Exception as e:
            print(f"AI enhancement error: {e}")
            return description
    
    def generate_terrain_with_ai(self, description, output_dir="output"):
        """Generate terrain with optional AI enhancement."""
        print(f"Original Description: {description}")
        
        # Enhance description with AI if available
        if self.use_ai:
            enhanced_description = self.enhance_description_with_ai(description)
        else:
            enhanced_description = description
        
        # Generate mesh
        mesh, confidence = self.mesh_generator.generate_mesh(enhanced_description)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save mesh
        output_file = os.path.join(output_dir, "advanced_terrain.obj")
        self.mesh_generator.save_mesh(mesh, output_file)
        
        # Generate additional outputs
        self._generate_additional_outputs(mesh, output_dir)
        
        return mesh, confidence, output_file
    
    def _generate_additional_outputs(self, mesh, output_dir):
        """Generate additional outputs like heightmaps and textures."""
        try:
            # Extract heightmap from mesh if possible
            vertices = mesh.vertices
            if len(vertices) > 0:
                # Create a simple heightmap visualization
                x_coords = vertices[:, 0]
                y_coords = vertices[:, 1]
                z_coords = vertices[:, 2]
                
                # Create a 2D heightmap
                import numpy as np
                from matplotlib import pyplot as plt
                
                # Create a grid for heightmap
                x_min, x_max = x_coords.min(), x_coords.max()
                y_min, y_max = y_coords.min(), y_coords.max()
                
                # Generate heightmap
                resolution = 100
                x_grid = np.linspace(x_min, x_max, resolution)
                y_grid = np.linspace(y_min, y_max, resolution)
                X, Y = np.meshgrid(x_grid, y_grid)
                
                # Interpolate Z values
                from scipy.interpolate import griddata
                Z = griddata((x_coords, y_coords), z_coords, (X, Y), method='linear')
                
                # Save heightmap
                heightmap_file = os.path.join(output_dir, "heightmap.png")
                plt.figure(figsize=(10, 8))
                plt.imshow(Z, cmap='terrain', extent=[x_min, x_max, y_min, y_max])
                plt.colorbar(label='Height')
                plt.title('Terrain Heightmap')
                plt.savefig(heightmap_file, dpi=150, bbox_inches='tight')
                plt.close()
                
                print(f"Heightmap saved to: {heightmap_file}")
                
        except Exception as e:
            print(f"Could not generate additional outputs: {e}")
    
    def batch_generate(self, descriptions, output_dir="output"):
        """Generate multiple terrains from a list of descriptions."""
        results = []
        
        for i, description in enumerate(descriptions):
            print(f"\nGenerating terrain {i+1}/{len(descriptions)}")
            print(f"Description: {description}")
            
            try:
                mesh, confidence, output_file = self.generate_terrain_with_ai(
                    description, 
                    os.path.join(output_dir, f"batch_{i+1}")
                )
                
                results.append({
                    'description': description,
                    'confidence': confidence,
                    'output_file': output_file,
                    'vertices': len(mesh.vertices),
                    'faces': len(mesh.faces)
                })
                
                print(f"✓ Successfully generated: {output_file}")
                
            except Exception as e:
                print(f"✗ Error generating terrain {i+1}: {e}")
                results.append({
                    'description': description,
                    'error': str(e)
                })
        
        return results

def main():
    """Main function to demonstrate advanced terrain generation."""
    print("Advanced Terrain Generator with AI Integration")
    print("=" * 60)
    
    # Initialize generator
    use_ai = input("Use AI enhancement? (y/n): ").lower().startswith('y')
    generator = AdvancedTerrainGenerator(use_ai=use_ai)
    
    if use_ai:
        if generator.check_ai_availability():
            print("✓ AI model (Ollama) is available")
        else:
            print("✗ AI model not available, continuing without AI enhancement")
            generator.use_ai = False
    
    # Example descriptions
    examples = [
        "a majestic mountain range with snow-capped peaks",
        "rolling green hills with scattered trees",
        "desert landscape with towering sand dunes",
        "alpine forest with rocky outcrops",
        "tropical island with palm trees and beaches"
    ]
    
    print(f"\nAvailable examples:")
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")
    
    choice = input(f"\nChoose an example (1-{len(examples)}) or enter custom description: ")
    
    try:
        choice_num = int(choice)
        if 1 <= choice_num <= len(examples):
            description = examples[choice_num - 1]
        else:
            description = choice
    except ValueError:
        description = choice
    
    if not description:
        description = "a beautiful mountain landscape"
    
    print(f"\nGenerating terrain: {description}")
    
    # Generate terrain
    mesh, confidence, output_file = generator.generate_terrain_with_ai(description)
    
    print(f"\nGeneration completed!")
    print(f"Confidence: {confidence:.2%}")
    print(f"Output file: {output_file}")
    print(f"Mesh stats: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")

if __name__ == "__main__":
    main() 