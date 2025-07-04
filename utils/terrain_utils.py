import numpy as np
from noise import pnoise2, snoise2
from scipy.ndimage import gaussian_filter, sobel
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
from PIL import Image

class TerrainUtils:
    @staticmethod
    def _apply_transformations(vertices, scale_factor=10.0, rotate_x_90=True):
        """Apply scaling and rotation transformations to vertices."""
        if rotate_x_90:
            # Create rotation matrix for 90 degrees around X-axis
            # This rotates Y to Z and Z to -Y
            rotation_matrix = np.array([
                [1, 0, 0],
                [0, 0, -1],
                [0, 1, 0]
            ])
            
            # Apply rotation to vertices
            vertices = np.dot(vertices, rotation_matrix.T)
        
        # Apply scaling
        vertices *= scale_factor
        
        return vertices

    @staticmethod
    def generate_heightmap(width, height, scale=50, octaves=6, persistence=0.5, 
                          lacunarity=2.0, base=0, terrain_type='mountain'):
        """Generate a heightmap using multiple noise layers."""
        heightmap = np.zeros((height, width))
        
        for i in range(height):
            for j in range(width):
                x = i / height * scale
                y = j / width * scale
                
                if terrain_type == 'mountain':
                    # Multi-layered mountain terrain
                    heightmap[i, j] = (
                        pnoise2(x, y, octaves=octaves, persistence=persistence, 
                               lacunarity=lacunarity, base=base) * 0.5 +
                        pnoise2(x*2, y*2, octaves=4, persistence=0.3, 
                               lacunarity=2.5, base=base+1) * 0.3 +
                        pnoise2(x*4, y*4, octaves=2, persistence=0.2, 
                               lacunarity=3.0, base=base+2) * 0.2
                    )
                elif terrain_type == 'hills':
                    # Gentle rolling hills
                    heightmap[i, j] = pnoise2(x, y, octaves=4, persistence=0.4, 
                                            lacunarity=2.0, base=base) * 0.3
                elif terrain_type == 'valley':
                    # Valley with river-like features
                    base_noise = pnoise2(x, y, octaves=6, persistence=0.5, 
                                       lacunarity=2.0, base=base)
                    river_mask = np.exp(-((x - scale/2)**2 + (y - scale/2)**2) / (scale/4)**2)
                    heightmap[i, j] = -base_noise * 0.4 - river_mask * 0.3
                elif terrain_type == 'plateau':
                    # Plateau with some variation
                    base_height = pnoise2(x, y, octaves=2, persistence=0.3, 
                                        lacunarity=2.0, base=base) * 0.2
                    heightmap[i, j] = np.maximum(base_height, 0.1)
                elif terrain_type == 'canyon':
                    # Canyon terrain
                    base_noise = pnoise2(x, y, octaves=4, persistence=0.4, 
                                       lacunarity=2.0, base=base)
                    canyon_mask = np.exp(-((x - scale/2)**2) / (scale/8)**2)
                    heightmap[i, j] = base_noise * 0.3 - canyon_mask * 0.6
                else:
                    # Default terrain
                    heightmap[i, j] = pnoise2(x, y, octaves=octaves, persistence=persistence, 
                                            lacunarity=lacunarity, base=base) * 0.5
        
        return heightmap

    @staticmethod
    def apply_erosion(heightmap, iterations=100, erosion_rate=0.01):
        """Apply simple hydraulic erosion to the heightmap."""
        eroded = heightmap.copy()
        height, width = heightmap.shape
        
        for _ in range(iterations):
            # Random starting points
            for _ in range(width * height // 10):
                x = np.random.randint(1, width - 1)
                y = np.random.randint(1, height - 1)
                
                # Find steepest descent
                max_slope = 0
                dx, dy = 0, 0
                
                for nx in range(x-1, x+2):
                    for ny in range(y-1, y+2):
                        if nx != x or ny != y:
                            slope = (eroded[y, x] - eroded[ny, nx]) / np.sqrt((nx-x)**2 + (ny-y)**2)
                            if slope > max_slope:
                                max_slope = slope
                                dx, dy = nx - x, ny - y
                
                # Apply erosion
                if max_slope > 0:
                    eroded[y, x] -= erosion_rate * max_slope
                    if 0 <= y + dy < height and 0 <= x + dx < width:
                        eroded[y + dy, x + dx] += erosion_rate * max_slope * 0.5
        
        return eroded

    @staticmethod
    def generate_slope_map(heightmap):
        """Generate a slope map from the heightmap."""
        # Calculate gradients
        grad_x = sobel(heightmap, axis=1)
        grad_y = sobel(heightmap, axis=0)
        
        # Calculate slope magnitude
        slope = np.sqrt(grad_x**2 + grad_y**2)
        
        return slope

    @staticmethod
    def add_features(heightmap, feature_type='rocks', density=0.1):
        """Add features like rocks, trees, or other objects to the heightmap."""
        height, width = heightmap.shape
        modified = heightmap.copy()
        
        if feature_type == 'rocks':
            # Add rock formations (elevated areas)
            num_features = int(width * height * density)
            for _ in range(num_features):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                radius = np.random.uniform(2, 5)
                height_increase = np.random.uniform(0.5, 2.0)
                
                # Create rock formation
                for nx in range(max(0, int(x-radius)), min(width, int(x+radius))):
                    for ny in range(max(0, int(y-radius)), min(height, int(y+radius))):
                        dist = np.sqrt((nx-x)**2 + (ny-y)**2)
                        if dist < radius:
                            factor = 1 - (dist / radius)
                            modified[ny, nx] += height_increase * factor * factor
        
        elif feature_type == 'craters':
            # Add craters (depressions)
            num_features = int(width * height * density)
            for _ in range(num_features):
                x = np.random.randint(0, width)
                y = np.random.randint(0, height)
                radius = np.random.uniform(3, 8)
                depth = np.random.uniform(0.5, 1.5)
                
                # Create crater
                for nx in range(max(0, int(x-radius)), min(width, int(x+radius))):
                    for ny in range(max(0, int(y-radius)), min(height, int(y+radius))):
                        dist = np.sqrt((nx-x)**2 + (ny-y)**2)
                        if dist < radius:
                            factor = 1 - (dist / radius)
                            modified[ny, nx] -= depth * factor * factor
        
        return modified

    @staticmethod
    def generate_texture(heightmap, texture_type='grass'):
        """Generate a texture map based on height and slope."""
        height, width = heightmap.shape
        
        # Normalize heightmap
        normalized_height = (heightmap - heightmap.min()) / (heightmap.max() - heightmap.min())
        
        # Generate slope map
        slope = TerrainUtils.generate_slope_map(heightmap)
        normalized_slope = slope / slope.max()
        
        # Create texture based on type
        if texture_type == 'grass':
            # Green texture varying with height and slope
            texture = np.zeros((height, width, 3))
            texture[:, :, 0] = 0.1 + 0.3 * normalized_height  # Red
            texture[:, :, 1] = 0.3 + 0.5 * (1 - normalized_slope)  # Green
            texture[:, :, 2] = 0.1 + 0.2 * normalized_height  # Blue
        
        elif texture_type == 'rock':
            # Gray texture for rocky areas
            texture = np.zeros((height, width, 3))
            gray_value = 0.3 + 0.4 * normalized_height
            texture[:, :, 0] = gray_value
            texture[:, :, 1] = gray_value
            texture[:, :, 2] = gray_value
        
        elif texture_type == 'snow':
            # White texture for snow-capped peaks
            texture = np.zeros((height, width, 3))
            snow_mask = normalized_height > 0.7
            texture[snow_mask] = [0.9, 0.9, 0.9]
            texture[~snow_mask] = [0.3, 0.3, 0.3]
        
        return texture

    @staticmethod
    def save_heightmap_as_image(heightmap, filename, colormap='terrain'):
        """Save heightmap as an image file."""
        plt.figure(figsize=(10, 8))
        plt.imshow(heightmap, cmap=colormap)
        plt.colorbar(label='Height')
        plt.title('Terrain Heightmap')
        plt.axis('off')
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        plt.close()

    @staticmethod
    def create_terrain_mesh_from_heightmap(heightmap, width=50, height=50, scale=1.0):
        """Create a mesh from a heightmap."""
        h, w = heightmap.shape
        
        # Create coordinate grids
        x_coords = np.linspace(-width/2, width/2, w)
        y_coords = np.linspace(-height/2, height/2, h)
        X, Y = np.meshgrid(x_coords, y_coords)
        
        # Scale heightmap
        Z = heightmap * scale
        
        # Create vertices
        vertices = np.column_stack([X.flatten(), Y.flatten(), Z.flatten()])
        
        # Apply transformations (rotation and scaling)
        vertices = TerrainUtils._apply_transformations(vertices)
        
        # Create faces (triangles)
        faces = []
        for i in range(h - 1):
            for j in range(w - 1):
                # Calculate vertex indices
                v0 = i * w + j
                v1 = i * w + (j + 1)
                v2 = (i + 1) * w + j
                v3 = (i + 1) * w + (j + 1)
                
                # Create two triangles
                faces.append([v0, v1, v2])
                faces.append([v1, v3, v2])
        
        return vertices, faces 