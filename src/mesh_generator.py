import torch
from transformers import BertTokenizer, BertModel, CLIPTextModel, CLIPTokenizer
from shap_e.diffusion.sample import sample_latents
from shap_e.diffusion.gaussian_diffusion import diffusion_from_config
from shap_e.models.download import load_model, load_config
from shap_e.util.notebooks import create_pan_cameras, decode_latent_images, decode_latent_mesh
from utils.unity_utils import save_for_unity, export_unity_prefab, create_unity_material, create_unity_physics_material
from .mesh_analyzer import MeshAnalyzer
from .mesh_colorizer import MeshColorizer
import os
import numpy as np
from collections import defaultdict
import re

class MeshGenerator:
    def __init__(self):
        # Initialize device
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # Load Shap-E models with higher quality settings
        print("Loading Shap-E models...")
        self.xm = load_model('transmitter', device=self.device)
        self.model = load_model('text300M', device=self.device)
        self.diffusion = diffusion_from_config(load_config('diffusion'))
        
        # Load BERT and CLIP models for enhanced text understanding
        print("Loading language models...")
        self.tokenizer = BertTokenizer.from_pretrained('bert-large-uncased')
        self.bert_model = BertModel.from_pretrained('bert-large-uncased').to(self.device)
        self.clip_tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-large-patch14")
        self.clip_model = CLIPTextModel.from_pretrained("openai/clip-vit-large-patch14").to(self.device)
        
        # Get model max lengths
        self.bert_max_length = self.bert_model.config.max_position_embeddings
        self.clip_max_length = self.clip_tokenizer.model_max_length
        
        # Initialize mesh analysis and coloring components
        print("Initializing mesh analysis and coloring systems...")
        self.mesh_analyzer = MeshAnalyzer(device=self.device)
        self.mesh_colorizer = MeshColorizer()
        
        # Scene understanding categories
        self.scene_categories = {
            'landscape_features': ['mountain', 'hill', 'valley', 'plateau', 'cliff', 'rock', 'boulder', 'highland'],
            'water_features': ['lake', 'pond', 'river', 'stream', 'spring', 'waterfall', 'reflection', 'pool', 'hot spring'],
            'vegetation': ['flower', 'grass', 'tree', 'bush', 'forest', 'lupine', 'tundra', 'moss'],
            'weather': ['fog', 'mist', 'cloud', 'rain', 'snow', 'sunny', 'storm', 'clear'],
            'time_of_day': ['sunrise', 'sunset', 'morning', 'evening', 'noon', 'dusk', 'dawn'],
            'atmosphere': ['quiet', 'peaceful', 'calm', 'serene', 'dramatic', 'moody', 'misty'],
            'colors': ['blue', 'green', 'white', 'aqua', 'turquoise', 'golden', 'pink', 'purple', 'bright'],
            'textures': ['rough', 'smooth', 'crisp', 'soft', 'sharp', 'jagged', 'opaque', 'transparent']
        }
        
        print("Models loaded successfully!")

    def chunk_text(self, text):
        """Split text into meaningful chunks that respect natural language boundaries."""
        # Split by commas and other natural breaks
        chunks = re.split(r'[,;]\s*', text)
        
        # Process chunks to ensure they're within length limits
        processed_chunks = []
        current_chunk = ""
        
        for chunk in chunks:
            # If chunk is too long, split it further by spaces
            if len(chunk) > self.bert_max_length:
                words = chunk.split()
                temp_chunk = ""
                for word in words:
                    if len(temp_chunk) + len(word) + 1 <= self.bert_max_length:
                        temp_chunk += " " + word if temp_chunk else word
                    else:
                        processed_chunks.append(temp_chunk)
                        temp_chunk = word
                if temp_chunk:
                    processed_chunks.append(temp_chunk)
            else:
                processed_chunks.append(chunk)
        
        return processed_chunks

    def analyze_text(self, text_description):
        """Enhanced text analysis that handles long descriptions by chunking."""
        # Split text into manageable chunks
        chunks = self.chunk_text(text_description)
        
        # Initialize combined results
        combined_scene_elements = defaultdict(list)
        combined_features = None
        
        print("\nAnalyzing text in chunks:")
        for i, chunk in enumerate(chunks, 1):
            print(f"Processing chunk {i}/{len(chunks)}: '{chunk}'")
            
            # Process BERT
            inputs = self.tokenizer(chunk, 
                                  return_tensors="pt", 
                                  padding=True, 
                                  truncation=True, 
                                  max_length=self.bert_max_length).to(self.device)
            with torch.no_grad():
                bert_outputs = self.bert_model(**inputs)
            
            # Process CLIP
            clip_inputs = self.clip_tokenizer(chunk, 
                                            return_tensors="pt", 
                                            padding=True, 
                                            truncation=True, 
                                            max_length=self.clip_max_length).to(self.device)
            with torch.no_grad():
                clip_outputs = self.clip_model(**clip_inputs)
            
            # Combine embeddings
            chunk_features = torch.cat([
                bert_outputs.pooler_output,
                clip_outputs.pooler_output
            ], dim=-1)
            
            # Update combined features
            if combined_features is None:
                combined_features = chunk_features
            else:
                combined_features = torch.max(combined_features, chunk_features)
            
            # Analyze scene elements in this chunk
            chunk_lower = chunk.lower()
            for category, keywords in self.scene_categories.items():
                for keyword in keywords:
                    if keyword in chunk_lower:
                        if keyword not in combined_scene_elements[category]:
                            combined_scene_elements[category].append(keyword)
        
        # Determine materials based on combined analysis
        materials = {
            'primary': 'terrain',
            'secondary': [],
            'details': []
        }
        
        # Process water features
        if combined_scene_elements['water_features']:
            materials['secondary'].append('water')
            if any('hot spring' in feat for feat in combined_scene_elements['water_features']):
                materials['details'].append('geothermal')
        
        # Process landscape features
        if any(k in str(combined_scene_elements) for k in ['mountain', 'cliff', 'rock', 'boulder']):
            materials['secondary'].append('rock')
        
        # Process vegetation
        if any(k in str(combined_scene_elements) for k in ['grass', 'flower', 'tree', 'forest', 'lupine']):
            materials['secondary'].append('grass')
            materials['details'].append('vegetation')
        
        # Determine environment type
        environment_type = self.determine_environment_type(combined_scene_elements)
        
        # Calculate overall scene complexity
        complexity = self.calculate_scene_complexity(combined_scene_elements)
        
        return {
            'features': combined_features,
            'scene_elements': dict(combined_scene_elements),
            'materials': materials,
            'environment_type': environment_type,
            'complexity': complexity
        }

    def determine_environment_type(self, scene_elements):
        """Determine the primary environment type based on scene elements."""
        # Check for mixed environments first
        has_water = bool(scene_elements.get('water_features', []))
        has_mountains = any('mountain' in feat for feat in scene_elements.get('landscape_features', []))
        has_vegetation = bool(scene_elements.get('vegetation', []))
        
        if has_water and has_mountains and has_vegetation:
            return 'mixed_landscape'
        elif has_water and 'hot spring' in str(scene_elements):
            return 'geothermal'
        elif has_mountains:
            return 'mountain'
        elif has_water:
            return 'water'
        elif 'tundra' in str(scene_elements):
            return 'tundra'
        elif has_vegetation:
            return 'vegetation'
        else:
            return 'terrain'

    def calculate_scene_complexity(self, scene_elements):
        """Calculate scene complexity for mesh generation parameters."""
        # Count unique elements across all categories
        total_elements = sum(len(elements) for elements in scene_elements.values())
        
        # Add complexity for specific combinations
        combination_bonus = 0
        if scene_elements.get('water_features') and scene_elements.get('landscape_features'):
            combination_bonus += 0.2
        if scene_elements.get('weather') and scene_elements.get('time_of_day'):
            combination_bonus += 0.1
        if scene_elements.get('atmosphere') and scene_elements.get('colors'):
            combination_bonus += 0.1
        
        # Calculate base complexity and add bonus
        base_complexity = np.log(1 + total_elements) / 4
        total_complexity = min(1.0, base_complexity + combination_bonus)
        
        return total_complexity

    def generate_mesh(self, text_description):
        """Generate a detailed mesh from a complex text description using Shap-E."""
        print(f"\nAnalyzing scene: '{text_description}'")
        text_analysis = self.analyze_text(text_description)
        
        # Adjust generation parameters based on scene complexity
        batch_size = 1
        guidance_scale = 20.0  # Increased for better prompt adherence
        karras_steps = max(64, int(128 * text_analysis['complexity']))  # More steps for complex scenes
        
        print("\nScene analysis results:")
        for category, elements in text_analysis['scene_elements'].items():
            if elements:
                print(f"- {category}: {', '.join(elements)}")
        print(f"- Environment type: {text_analysis['environment_type']}")
        print(f"- Scene complexity: {text_analysis['complexity']:.2f}")
        
        print("\nGenerating 3D mesh with enhanced parameters...")
        # Generate latents with Shap-E
        latents = sample_latents(
            batch_size=batch_size,
            model=self.model,
            diffusion=self.diffusion,
            guidance_scale=guidance_scale,
            model_kwargs=dict(texts=[text_description]),
            progress=True,
            clip_denoised=True,
            use_fp16=True,
            use_karras=True,
            karras_steps=karras_steps,
            sigma_min=1e-3,
            sigma_max=160,
            s_churn=0.1  # Added for better detail
        )
        
        # Convert latent to mesh with higher detail
        print("Converting latent to high-detail mesh...")
        latent = latents[0]
        mesh = decode_latent_mesh(self.xm, latent).tri_mesh()
        
        # Create optimized collision mesh
        print("Generating optimized collision mesh...")
        collision_mesh = mesh.convex_hull()  # Using convex hull instead of decimation
        
        # Set materials based on analysis
        material_type = text_analysis['environment_type']
        physics_type = 'terrain'  # Default physics type
        
        # Calculate confidence based on mesh complexity and scene understanding
        vertex_confidence = min(1.0, len(mesh.vertices) / 20000)
        scene_confidence = text_analysis['complexity']
        confidence = (vertex_confidence + scene_confidence) / 2
        
        print(f"\nMesh generated successfully:")
        print(f"- Vertices: {len(mesh.vertices)}")
        print(f"- Faces: {len(mesh.faces)}")
        print(f"- Primary material: {material_type}")
        print(f"- Secondary materials: {', '.join(text_analysis['materials']['secondary'])}")
        print(f"- Detail elements: {', '.join(text_analysis['materials']['details'])}")
        print(f"- Generation quality: {karras_steps} steps at {guidance_scale:.1f}x guidance")
        print(f"- Confidence: {confidence:.2f}")
        
        # Perform mesh analysis and semantic segmentation
        print("\n🧠 Analyzing mesh geometry and semantics...")
        analysis_results = self.mesh_analyzer.analyze_mesh(mesh, text_description)
        
        # Apply intelligent coloring based on analysis
        environment_type = self._map_environment_type(text_analysis['environment_type'])
        color_results = self.mesh_colorizer.colorize_mesh(
            mesh, analysis_results, text_description, 
            environment_type=environment_type, advanced_effects=True
        )
        
        # Apply vertex colors to the mesh
        vertex_colors = color_results['vertex_colors']
        mesh = self._apply_vertex_colors_to_mesh(mesh, vertex_colors)
        
        print(f"\n🎨 Mesh coloring complete:")
        print(f"- Environment type: {color_results['environment_type']}")
        print(f"- Semantic regions: {color_results['color_info']['unique_semantics']}")
        print(f"- Color categories: {list(color_results['color_info']['color_legend'].keys())}")
        
        return mesh, collision_mesh, confidence, material_type, physics_type, analysis_results, color_results
    
    def _save_color_info(self, color_results: dict, filename: str):
        """Save color information to JSON file."""
        import json
        
        # Convert numpy arrays to lists for JSON serialization
        color_info = color_results['color_info'].copy()
        for category, info in color_info.get('color_legend', {}).items():
            if 'color' in info:
                info['color'] = info['color'].tolist()
        
        # Convert color palette
        color_palette = {}
        for category, color in color_results['color_palette'].items():
            color_palette[category] = color.tolist()
        
        save_data = {
            'environment_type': color_results['environment_type'],
            'color_info': color_info,
            'color_palette': color_palette
        }
        
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)
    
    def _save_texture_map(self, texture_map: np.ndarray, filename: str):
        """Save texture map as PNG image."""
        try:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(8, 8))
            plt.imshow(texture_map)
            plt.axis('off')
            plt.title('Generated Texture Map')
            plt.savefig(filename, bbox_inches='tight', dpi=150)
            plt.close()
        except Exception as e:
            print(f"Warning: Could not save texture map: {e}")
    
    def _save_analysis_results(self, analysis_results: dict, filename: str):
        """Save mesh analysis results to JSON file."""
        import json
        
        # Prepare data for JSON serialization (exclude complex objects)
        save_data = {
            'segmentation': {
                'n_clusters': analysis_results['segmentation']['n_clusters'],
                'cluster_sizes': analysis_results['segmentation']['cluster_sizes'].tolist(),
                'labels_summary': {
                    'unique_labels': len(np.unique(analysis_results['segmentation']['labels'])),
                    'total_vertices': len(analysis_results['segmentation']['labels'])
                }
            },
            'semantic_mapping': {
                'cluster_to_semantic': analysis_results['semantic_mapping']['cluster_to_semantic'],
                'available_categories': analysis_results['semantic_mapping']['available_categories']
            },
            'geometric_features_summary': {
                'height_range': [
                    float(analysis_results['geometric_features']['height'].min()),
                    float(analysis_results['geometric_features']['height'].max())
                ],
                'curvature_stats': {
                    'mean': float(analysis_results['geometric_features']['curvature'].mean()),
                    'std': float(analysis_results['geometric_features']['curvature'].std())
                },
                'roughness_stats': {
                    'mean': float(analysis_results['geometric_features']['roughness'].mean()),
                    'std': float(analysis_results['geometric_features']['roughness'].std())
                }
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(save_data, f, indent=2)

    def save_mesh(self, mesh, collision_mesh, filename, material_type='default', physics_type='default', 
                  analysis_results=None, color_results=None):
        """Save the generated mesh with enhanced Unity integration and coloring."""
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        # Use the base filename (without .obj) for all outputs
        base, _ = os.path.splitext(filename)
        visual_filename = f"{base}.obj"
        collision_filename = f"{base}_collision.obj"
        prefab_filename = f"{base}_prefab.json"
        
        # Save meshes with optimized settings
        print("\nSaving Unity-ready files with intelligent coloring...")
        with open(visual_filename, 'w') as f:
            mesh.write_obj(f)
        with open(collision_filename, 'w') as f:
            collision_mesh.write_obj(f)
        
        # Save color information and analysis results
        if color_results:
            # Save color palette information
            color_info_filename = f"{base}_color_info.json"
            self._save_color_info(color_results, color_info_filename)
            
            # Save color visualization
            color_viz_filename = f"{base}_color_legend.png"
            self.mesh_colorizer.save_color_visualization(color_results['color_info'], color_viz_filename)
            
            # Save texture map if available
            if color_results.get('texture_map') is not None:
                texture_filename = f"{base}_texture.png"
                self._save_texture_map(color_results['texture_map'], texture_filename)
        
        # Save analysis results
        if analysis_results:
            analysis_filename = f"{base}_analysis.json"
            self._save_analysis_results(analysis_results, analysis_filename)
        
        # Export as Unity prefab with enhanced materials and physics
        prefab_data = export_unity_prefab(mesh, collision_mesh, visual_filename, material_type, physics_type)
        
        print(f"\nUnity-ready files saved:")
        print(f"- Visual mesh: {visual_filename}")
        print(f"- Collision mesh: {collision_filename}")
        print(f"- Prefab data: {prefab_filename}")
        if color_results:
            print(f"- Color information: {base}_color_info.json")
            print(f"- Color legend: {base}_color_legend.png")
            if color_results.get('texture_map') is not None:
                print(f"- Texture map: {base}_texture.png")
        if analysis_results:
            print(f"- Mesh analysis: {base}_analysis.json")
        
        print("Unity properties:")
        print(f"- Scale: 1 unit = 10 meters in Unity (10x scaled)")
        print(f"- Coordinate system: Adjusted for Unity (left-handed)")
        print(f"- Rotation: 90° on X-axis applied")
        print(f"- Colors: Intelligent semantic vertex colors applied")
        print(f"- Material: {material_type} with advanced shaders")
        print(f"- Physics: {physics_type} material with optimized collision")
        print(f"- Included: Normals, UV coordinates, semantic colors, and Unity metadata")

    def save_mesh_simple(self, mesh, filename):
        """Legacy method for backward compatibility."""
        # Create a simple collision mesh
        collision_mesh = mesh.convex_hull
        self.save_mesh(mesh, collision_mesh, filename)
    
    def _map_environment_type(self, analysis_environment_type: str) -> str:
        """Map the analysis environment type to colorizer environment type."""
        mapping = {
            'mixed_landscape': 'alpine',
            'geothermal': 'volcanic',
            'mountain': 'alpine',
            'water': 'tropical',
            'tundra': 'tundra',
            'vegetation': 'forest',
            'terrain': 'alpine'
        }
        return mapping.get(analysis_environment_type, 'alpine')
    
    def _apply_vertex_colors_to_mesh(self, mesh, vertex_colors: np.ndarray):
        """Apply vertex colors to the mesh object."""
        # Check if mesh has vertex_channels attribute (Shap-E TriMesh)
        if hasattr(mesh, 'vertex_channels'):
            if mesh.vertex_channels is None:
                mesh.vertex_channels = {}
            
            # Set RGB channels
            mesh.vertex_channels['R'] = vertex_colors[:, 0]
            mesh.vertex_channels['G'] = vertex_colors[:, 1]
            mesh.vertex_channels['B'] = vertex_colors[:, 2]
        
        # For trimesh objects, set visual colors
        elif hasattr(mesh, 'visual'):
            mesh.visual.vertex_colors = (vertex_colors * 255).astype(np.uint8)
        
        return mesh 