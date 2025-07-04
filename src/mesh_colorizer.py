import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import colorsys
from typing import Dict, List, Tuple, Optional, Union
import cv2
from PIL import Image, ImageDraw, ImageFilter
import warnings
warnings.filterwarnings("ignore")

class MeshColorizer:
    """
    Advanced mesh coloring system that applies colors to 3D meshes based on
    semantic segmentation results from MeshAnalyzer.
    """
    
    def __init__(self):
        # Predefined color palettes for different environment types
        self.environment_palettes = {
            'alpine': {
                'water': np.array([0.15, 0.45, 0.75]),      # Deep blue
                'terrain': np.array([0.45, 0.35, 0.25]),    # Brown earth
                'vegetation': np.array([0.2, 0.6, 0.3]),    # Forest green
                'rocks': np.array([0.6, 0.6, 0.65]),        # Light gray
                'snow': np.array([0.95, 0.95, 1.0])         # Pure white
            },
            'desert': {
                'water': np.array([0.2, 0.5, 0.8]),         # Oasis blue
                'terrain': np.array([0.85, 0.7, 0.45]),     # Sand color
                'vegetation': np.array([0.4, 0.6, 0.2]),    # Desert vegetation
                'rocks': np.array([0.7, 0.5, 0.3]),         # Desert rocks
                'snow': np.array([0.9, 0.9, 0.9])           # Rare snow
            },
            'forest': {
                'water': np.array([0.1, 0.3, 0.6]),         # Dark water
                'terrain': np.array([0.3, 0.2, 0.1]),       # Rich soil
                'vegetation': np.array([0.15, 0.5, 0.2]),   # Deep forest green
                'rocks': np.array([0.4, 0.4, 0.4]),         # Moss-covered rocks
                'snow': np.array([0.8, 0.8, 0.85])          # Forest snow
            },
            'tropical': {
                'water': np.array([0.0, 0.7, 0.9]),         # Turquoise
                'terrain': np.array([0.6, 0.4, 0.2]),       # Tropical soil
                'vegetation': np.array([0.1, 0.8, 0.3]),    # Lush green
                'rocks': np.array([0.3, 0.3, 0.3]),         # Dark volcanic rock
                'snow': np.array([1.0, 1.0, 1.0])           # Pure mountain snow
            },
            'tundra': {
                'water': np.array([0.2, 0.4, 0.6]),         # Cold water
                'terrain': np.array([0.5, 0.4, 0.3]),       # Tundra ground
                'vegetation': np.array([0.4, 0.5, 0.2]),    # Hardy vegetation
                'rocks': np.array([0.5, 0.5, 0.6]),         # Cold rocks
                'snow': np.array([0.9, 0.95, 1.0])          # Tundra snow
            },
            'volcanic': {
                'water': np.array([0.1, 0.2, 0.4]),         # Dark mineral water
                'terrain': np.array([0.3, 0.15, 0.1]),      # Volcanic soil
                'vegetation': np.array([0.2, 0.4, 0.15]),   # Sparse vegetation
                'rocks': np.array([0.2, 0.2, 0.2]),         # Black volcanic rock
                'snow': np.array([0.85, 0.85, 0.9])         # Ash-tinted snow
            }
        }
        
        # Advanced color variation parameters
        self.color_variation = {
            'base_noise': 0.15,        # Base color variation
            'height_influence': 0.2,    # Height-based color shifts
            'normal_influence': 0.1,    # Normal-based lighting effects
            'curvature_influence': 0.15, # Curvature-based shading
            'wetness_factor': 0.3,      # Wetness darkening near water
            'exposure_factor': 0.2      # Sun exposure lightening
        }
    
    def colorize_mesh(self, mesh, analysis_results: Dict, text_description: str = "", 
                     environment_type: str = "alpine", advanced_effects: bool = True) -> Dict:
        """
        Apply colors to mesh based on semantic segmentation analysis.
        
        Args:
            mesh: TriMesh object from Shap-E
            analysis_results: Results from MeshAnalyzer.analyze_mesh()
            text_description: Original text description for context
            environment_type: Environment type for color palette selection
            advanced_effects: Whether to apply advanced color effects
        
        Returns:
            Dictionary containing colored mesh data and color information
        """
        print("\n🎨 Starting mesh colorization...")
        
        # Extract data from analysis results
        segmentation = analysis_results['segmentation']
        semantic_mapping = analysis_results['semantic_mapping']
        geometric_features = analysis_results['geometric_features']
        
        # Get vertices
        vertices = mesh.verts if hasattr(mesh, 'verts') else mesh.vertices
        
        # Determine environment type from text if not specified
        if environment_type == "auto":
            environment_type = self._detect_environment_type(text_description)
        
        # Get color palette
        color_palette = self._get_color_palette(environment_type, text_description)
        
        # Apply base colors based on segmentation
        base_colors = self._apply_base_colors(
            vertices, segmentation, semantic_mapping, color_palette
        )
        
        # Apply advanced color effects if enabled
        if advanced_effects:
            final_colors = self._apply_advanced_effects(
                vertices, base_colors, geometric_features, segmentation, semantic_mapping
            )
        else:
            final_colors = base_colors
        
        # Generate texture map (optional)
        texture_map = self._generate_texture_map(vertices, final_colors, mesh.faces)
        
        # Create color visualization
        color_info = self._create_color_info(
            segmentation, semantic_mapping, color_palette, environment_type
        )
        
        print(f"✅ Colorization complete! Applied {len(color_palette)} semantic colors")
        
        return {
            'vertex_colors': final_colors,
            'texture_map': texture_map,
            'color_palette': color_palette,
            'environment_type': environment_type,
            'color_info': color_info,
            'base_colors': base_colors
        }
    
    def _detect_environment_type(self, text_description: str) -> str:
        """Detect environment type from text description."""
        text_lower = text_description.lower()
        
        # Check for specific environment keywords
        environment_keywords = {
            'alpine': ['alpine', 'mountain', 'highland', 'peak', 'snow', 'glacier'],
            'desert': ['desert', 'sand', 'dune', 'arid', 'dry', 'oasis'],
            'forest': ['forest', 'woodland', 'tree', 'jungle', 'canopy'],
            'tropical': ['tropical', 'palm', 'beach', 'island', 'turquoise'],
            'tundra': ['tundra', 'arctic', 'frozen', 'polar', 'cold'],
            'volcanic': ['volcanic', 'lava', 'crater', 'ash', 'basalt']
        }
        
        for env_type, keywords in environment_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return env_type
        
        # Default to alpine if no specific type detected
        return 'alpine'
    
    def _get_color_palette(self, environment_type: str, text_description: str) -> Dict[str, np.ndarray]:
        """Get color palette for the specified environment type."""
        base_palette = self.environment_palettes.get(environment_type, self.environment_palettes['alpine'])
        
        # Customize palette based on text description
        customized_palette = base_palette.copy()
        text_lower = text_description.lower()
        
        # Adjust colors based on specific mentions
        color_adjustments = {
            'bright': 0.2,    # Increase brightness
            'dark': -0.15,    # Decrease brightness
            'vibrant': 0.3,   # Increase saturation
            'muted': -0.2,    # Decrease saturation
            'warm': (0.1, 0.1, 0),   # Add warmth (more red/yellow)
            'cool': (0, 0, 0.1),     # Add coolness (more blue)
            'golden': (0.2, 0.1, 0), # Golden tint
            'misty': (0, 0, 0.05)    # Misty blue tint
        }
        
        for modifier, adjustment in color_adjustments.items():
            if modifier in text_lower:
                for category, color in customized_palette.items():
                    if isinstance(adjustment, tuple):
                        # RGB adjustment
                        customized_palette[category] = np.clip(color + np.array(adjustment), 0, 1)
                    else:
                        # Brightness adjustment
                        hsv_color = colorsys.rgb_to_hsv(*color)
                        new_v = np.clip(hsv_color[2] + adjustment, 0, 1)
                        customized_palette[category] = np.array(colorsys.hsv_to_rgb(hsv_color[0], hsv_color[1], new_v))
        
        return customized_palette
    
    def _apply_base_colors(self, vertices: np.ndarray, segmentation: Dict, 
                          semantic_mapping: Dict, color_palette: Dict[str, np.ndarray]) -> np.ndarray:
        """Apply base colors to vertices based on segmentation."""
        print("  🖌️  Applying base colors...")
        
        labels = segmentation['labels']
        cluster_to_semantic = semantic_mapping['cluster_to_semantic']
        
        # Initialize color array
        vertex_colors = np.zeros((len(vertices), 3))
        
        # Apply colors based on cluster assignment
        for vertex_idx, cluster_id in enumerate(labels):
            semantic_category = cluster_to_semantic.get(cluster_id, 'terrain')
            base_color = color_palette.get(semantic_category, color_palette['terrain'])
            vertex_colors[vertex_idx] = base_color
        
        return vertex_colors
    
    def _apply_advanced_effects(self, vertices: np.ndarray, base_colors: np.ndarray,
                              geometric_features: Dict, segmentation: Dict, 
                              semantic_mapping: Dict) -> np.ndarray:
        """Apply advanced color effects for realism."""
        print("  ✨ Applying advanced color effects...")
        
        enhanced_colors = base_colors.copy()
        labels = segmentation['labels']
        cluster_to_semantic = semantic_mapping['cluster_to_semantic']
        
        # Extract features
        height = geometric_features['height']
        normals = geometric_features['normals']
        curvature = geometric_features['curvature']
        roughness = geometric_features['roughness']
        
        # 1. Height-based color variation
        enhanced_colors = self._apply_height_effects(enhanced_colors, height, labels, cluster_to_semantic)
        
        # 2. Normal-based lighting effects
        enhanced_colors = self._apply_lighting_effects(enhanced_colors, normals)
        
        # 3. Curvature-based shading
        enhanced_colors = self._apply_curvature_shading(enhanced_colors, curvature)
        
        # 4. Roughness-based texture effects
        enhanced_colors = self._apply_roughness_effects(enhanced_colors, roughness)
        
        # 5. Proximity effects (wetness near water, etc.)
        enhanced_colors = self._apply_proximity_effects(
            vertices, enhanced_colors, labels, cluster_to_semantic
        )
        
        # 6. Add natural color noise
        enhanced_colors = self._add_color_noise(enhanced_colors)
        
        # Ensure colors are in valid range
        enhanced_colors = np.clip(enhanced_colors, 0, 1)
        
        return enhanced_colors
    
    def _apply_height_effects(self, colors: np.ndarray, height: np.ndarray, 
                            labels: np.ndarray, cluster_to_semantic: Dict) -> np.ndarray:
        """Apply height-based color variations."""
        height_adjusted = colors.copy()
        
        for i, (color, h, label) in enumerate(zip(colors, height, labels)):
            semantic_type = cluster_to_semantic.get(label, 'terrain')
            
            # Different height effects for different semantic types
            if semantic_type == 'terrain':
                # Terrain gets lighter at higher elevations
                brightness_factor = 1.0 + self.color_variation['height_influence'] * h
                height_adjusted[i] *= brightness_factor
            elif semantic_type == 'vegetation':
                # Vegetation changes color with altitude
                if h > 0.7:  # High altitude vegetation
                    height_adjusted[i] = self._blend_colors(color, np.array([0.6, 0.4, 0.2]), 0.3)
                elif h < 0.3:  # Low altitude vegetation (lusher)
                    height_adjusted[i] = self._blend_colors(color, np.array([0.1, 0.8, 0.2]), 0.2)
            elif semantic_type == 'rocks':
                # Rocks get more weathered (lighter) at higher elevations
                if h > 0.8:
                    height_adjusted[i] = self._blend_colors(color, np.array([0.8, 0.8, 0.8]), 0.2)
        
        return height_adjusted
    
    def _apply_lighting_effects(self, colors: np.ndarray, normals: np.ndarray) -> np.ndarray:
        """Apply lighting effects based on surface normals."""
        # Simulate sunlight from above and slightly to the side
        light_direction = np.array([0.3, 0.3, 0.9])
        light_direction = light_direction / np.linalg.norm(light_direction)
        
        # Calculate dot product for each vertex normal
        lighting_intensity = np.dot(normals, light_direction)
        lighting_intensity = np.clip(lighting_intensity, 0.4, 1.0)  # Ambient lighting minimum
        
        # Apply lighting
        lit_colors = colors * lighting_intensity.reshape(-1, 1)
        
        return lit_colors
    
    def _apply_curvature_shading(self, colors: np.ndarray, curvature: np.ndarray) -> np.ndarray:
        """Apply shading based on surface curvature."""
        # Normalize curvature
        curvature_normalized = (curvature - curvature.min()) / (curvature.max() - curvature.min() + 1e-8)
        
        # Areas with high curvature get slightly darker (crevices)
        curvature_factor = 1.0 - self.color_variation['curvature_influence'] * curvature_normalized
        curvature_shaded = colors * curvature_factor.reshape(-1, 1)
        
        return curvature_shaded
    
    def _apply_roughness_effects(self, colors: np.ndarray, roughness: np.ndarray) -> np.ndarray:
        """Apply texture effects based on surface roughness."""
        # Normalize roughness
        roughness_normalized = (roughness - roughness.min()) / (roughness.max() - roughness.min() + 1e-8)
        
        # Rough areas get slightly desaturated
        roughness_factor = 1.0 - 0.1 * roughness_normalized
        
        # Convert to HSV for saturation adjustment
        roughness_adjusted = colors.copy()
        for i, (color, factor) in enumerate(zip(colors, roughness_factor)):
            hsv_color = colorsys.rgb_to_hsv(*color)
            new_saturation = hsv_color[1] * factor
            roughness_adjusted[i] = np.array(colorsys.hsv_to_rgb(hsv_color[0], new_saturation, hsv_color[2]))
        
        return roughness_adjusted
    
    def _apply_proximity_effects(self, vertices: np.ndarray, colors: np.ndarray,
                               labels: np.ndarray, cluster_to_semantic: Dict) -> np.ndarray:
        """Apply color effects based on proximity to other semantic regions."""
        proximity_adjusted = colors.copy()
        
        # Find water vertices
        water_vertices = []
        for i, label in enumerate(labels):
            if cluster_to_semantic.get(label, '') == 'water':
                water_vertices.append(i)
        
        if water_vertices:
            water_coords = vertices[water_vertices]
            
            # Apply wetness effects to nearby non-water vertices
            for i, (vertex, color, label) in enumerate(zip(vertices, colors, labels)):
                semantic_type = cluster_to_semantic.get(label, 'terrain')
                
                if semantic_type != 'water':
                    # Calculate distance to nearest water
                    distances = np.linalg.norm(water_coords - vertex, axis=1)
                    min_distance = np.min(distances)
                    
                    # Apply wetness effect if close to water
                    max_wetness_distance = 0.1  # Adjust based on mesh scale
                    if min_distance < max_wetness_distance:
                        wetness_factor = 1.0 - (min_distance / max_wetness_distance)
                        # Make colors darker and more saturated near water
                        darkness_factor = 1.0 - self.color_variation['wetness_factor'] * wetness_factor * 0.3
                        proximity_adjusted[i] *= darkness_factor
                        
                        # Add slight blue tint
                        blue_tint = np.array([0, 0, 0.1]) * wetness_factor * 0.2
                        proximity_adjusted[i] = self._blend_colors(proximity_adjusted[i], blue_tint, 0.3)
        
        return proximity_adjusted
    
    def _add_color_noise(self, colors: np.ndarray) -> np.ndarray:
        """Add subtle color noise for natural variation."""
        noise_strength = self.color_variation['base_noise']
        
        # Generate random noise
        noise = np.random.normal(0, noise_strength, colors.shape)
        
        # Apply noise
        noisy_colors = colors + noise
        
        return noisy_colors
    
    def _blend_colors(self, color1: np.ndarray, color2: np.ndarray, blend_factor: float) -> np.ndarray:
        """Blend two colors together."""
        return color1 * (1 - blend_factor) + color2 * blend_factor
    
    def _generate_texture_map(self, vertices: np.ndarray, colors: np.ndarray, 
                            faces: np.ndarray, texture_size: int = 512) -> Optional[np.ndarray]:
        """Generate a texture map from vertex colors."""
        try:
            print("  🗺️  Generating texture map...")
            
            # Create UV coordinates (simple projection)
            uv_coords = self._generate_uv_coordinates(vertices)
            
            # Create texture image
            texture = np.ones((texture_size, texture_size, 3))
            
            # Map vertex colors to texture
            for i, (uv, color) in enumerate(zip(uv_coords, colors)):
                u, v = uv
                x = int(u * (texture_size - 1))
                y = int(v * (texture_size - 1))
                
                # Apply color with some blending
                texture[y, x] = color
            
            # Apply Gaussian blur for smoother transitions
            for channel in range(3):
                texture[:, :, channel] = cv2.GaussianBlur(texture[:, :, channel], (5, 5), 1.0)
            
            return texture
            
        except Exception as e:
            print(f"  ⚠️ Could not generate texture map: {e}")
            return None
    
    def _generate_uv_coordinates(self, vertices: np.ndarray) -> np.ndarray:
        """Generate UV coordinates for vertices using simple cylindrical projection."""
        # Center the vertices
        center = np.mean(vertices, axis=0)
        centered_vertices = vertices - center
        
        # Cylindrical projection
        x, y, z = centered_vertices[:, 0], centered_vertices[:, 1], centered_vertices[:, 2]
        
        # Calculate UV coordinates
        u = np.arctan2(x, z) / (2 * np.pi) + 0.5
        v = (y - y.min()) / (y.max() - y.min() + 1e-8)
        
        uv_coords = np.column_stack([u, v])
        
        return uv_coords
    
    def _create_color_info(self, segmentation: Dict, semantic_mapping: Dict,
                          color_palette: Dict, environment_type: str) -> Dict:
        """Create color information summary."""
        labels = segmentation['labels']
        cluster_to_semantic = semantic_mapping['cluster_to_semantic']
        
        # Count vertices per semantic category
        semantic_counts = {}
        for label in labels:
            semantic_type = cluster_to_semantic.get(label, 'unknown')
            semantic_counts[semantic_type] = semantic_counts.get(semantic_type, 0) + 1
        
        # Create color legend
        color_legend = {}
        for semantic_type, count in semantic_counts.items():
            if semantic_type in color_palette:
                color_legend[semantic_type] = {
                    'color': color_palette[semantic_type],
                    'vertex_count': count,
                    'percentage': count / len(labels) * 100
                }
        
        return {
            'environment_type': environment_type,
            'semantic_counts': semantic_counts,
            'color_legend': color_legend,
            'total_vertices': len(labels),
            'unique_semantics': len(set(cluster_to_semantic.values()))
        }
    
    def save_color_visualization(self, color_info: Dict, output_path: str):
        """Save a color legend visualization."""
        try:
            print(f"  📊 Saving color visualization to {output_path}...")
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
            
            # Plot 1: Color legend
            legend_items = color_info['color_legend']
            colors = [item['color'] for item in legend_items.values()]
            labels = list(legend_items.keys())
            
            ax1.barh(range(len(labels)), [item['vertex_count'] for item in legend_items.values()],
                    color=colors)
            ax1.set_yticks(range(len(labels)))
            ax1.set_yticklabels(labels)
            ax1.set_xlabel('Vertex Count')
            ax1.set_title(f'Semantic Region Distribution\n({color_info["environment_type"]} environment)')
            
            # Plot 2: Pie chart
            percentages = [item['percentage'] for item in legend_items.values()]
            ax2.pie(percentages, labels=labels, colors=colors, autopct='%1.1f%%')
            ax2.set_title('Semantic Region Percentages')
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            
        except Exception as e:
            print(f"  ⚠️ Could not save color visualization: {e}") 