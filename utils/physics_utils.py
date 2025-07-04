import numpy as np
import trimesh
from scipy.spatial import ConvexHull

class PhysicsUtils:
    @staticmethod
    def create_physics_material(material_type='default'):
        """Create physics material properties for different terrain types."""
        materials = {
            'default': {
                'friction': 0.6,
                'bounciness': 0.0,
                'density': 1.0
            },
            'grass': {
                'friction': 0.8,
                'bounciness': 0.1,
                'density': 0.8
            },
            'rock': {
                'friction': 0.4,
                'bounciness': 0.2,
                'density': 2.5
            },
            'sand': {
                'friction': 0.9,
                'bounciness': 0.0,
                'density': 1.6
            },
            'water': {
                'friction': 0.1,
                'bounciness': 0.0,
                'density': 1.0,
                'is_fluid': True
            },
            'snow': {
                'friction': 0.7,
                'bounciness': 0.3,
                'density': 0.3
            }
        }
        
        return materials.get(material_type, materials['default'])

    @staticmethod
    def create_collision_box(mesh, padding=0.1):
        """Create a bounding box collision mesh."""
        bounds = mesh.bounds
        center = (bounds[0] + bounds[1]) / 2
        size = bounds[1] - bounds[0] + padding
        
        # Create box vertices
        half_size = size / 2
        vertices = np.array([
            [center[0] - half_size[0], center[1] - half_size[1], center[2] - half_size[2]],
            [center[0] + half_size[0], center[1] - half_size[1], center[2] - half_size[2]],
            [center[0] + half_size[0], center[1] + half_size[1], center[2] - half_size[2]],
            [center[0] - half_size[0], center[1] + half_size[1], center[2] - half_size[2]],
            [center[0] - half_size[0], center[1] - half_size[1], center[2] + half_size[2]],
            [center[0] + half_size[0], center[1] - half_size[1], center[2] + half_size[2]],
            [center[0] + half_size[0], center[1] + half_size[1], center[2] + half_size[2]],
            [center[0] - half_size[0], center[1] + half_size[1], center[2] + half_size[2]]
        ])
        
        # Create box faces
        faces = np.array([
            [0, 1, 2], [0, 2, 3],  # bottom
            [4, 7, 6], [4, 6, 5],  # top
            [0, 4, 5], [0, 5, 1],  # front
            [2, 6, 7], [2, 7, 3],  # back
            [0, 3, 7], [0, 7, 4],  # left
            [1, 5, 6], [1, 6, 2]   # right
        ])
        
        return trimesh.Trimesh(vertices=vertices, faces=faces)

    @staticmethod
    def create_collision_sphere(mesh, padding=0.1):
        """Create a bounding sphere collision mesh."""
        bounds = mesh.bounds
        center = (bounds[0] + bounds[1]) / 2
        radius = np.linalg.norm(bounds[1] - bounds[0]) / 2 + padding
        
        # Create sphere mesh
        sphere = trimesh.creation.icosphere(radius=radius, subdivisions=2)
        sphere.vertices += center
        
        return sphere

    @staticmethod
    def create_collision_capsule(mesh, padding=0.1):
        """Create a capsule collision mesh."""
        bounds = mesh.bounds
        center = (bounds[0] + bounds[1]) / 2
        size = bounds[1] - bounds[0] + padding
        
        # Create capsule
        height = size[2]
        radius = max(size[0], size[1]) / 2
        
        capsule = trimesh.creation.capsule(height=height, radius=radius)
        capsule.vertices += center
        
        return capsule

    @staticmethod
    def optimize_collision_mesh(mesh, target_vertices=100):
        """Optimize collision mesh for physics performance."""
        if len(mesh.vertices) <= target_vertices:
            return mesh
        
        # Simplify mesh using available methods
        try:
            if hasattr(mesh, 'simplify_quadratic_decimation'):
                simplified = mesh.simplify_quadratic_decimation(
                    target_vertices=target_vertices
                )
            else:
                # Fallback to convex hull for optimization
                simplified = mesh.convex_hull
        except:
            # If simplification fails, use convex hull
            simplified = mesh.convex_hull
        
        # Ensure mesh is watertight
        if not simplified.is_watertight:
            # Create convex hull as fallback
            simplified = simplified.convex_hull
        
        return simplified

    @staticmethod
    def create_terrain_collision_layers(mesh, height_thresholds=None):
        """Create multiple collision layers for complex terrain."""
        if height_thresholds is None:
            # Default height thresholds
            heights = mesh.vertices[:, 2]
            min_h, max_h = heights.min(), heights.max()
            height_thresholds = [
                min_h + (max_h - min_h) * 0.2,  # Low terrain
                min_h + (max_h - min_h) * 0.5,  # Medium terrain
                min_h + (max_h - min_h) * 0.8   # High terrain
            ]
        
        layers = []
        heights = mesh.vertices[:, 2]
        
        for i, threshold in enumerate(height_thresholds):
            # Create mask for this height layer
            if i == 0:
                mask = heights <= threshold
            elif i == len(height_thresholds) - 1:
                mask = heights > height_thresholds[i-1]
            else:
                mask = (heights > height_thresholds[i-1]) & (heights <= threshold)
            
            if np.any(mask):
                # Extract vertices and faces for this layer
                layer_vertices = mesh.vertices[mask]
                layer_faces = []
                
                # Find faces that belong to this layer
                for face in mesh.faces:
                    if all(mask[face]):
                        layer_faces.append(face)
                
                if len(layer_faces) > 0:
                    layer_mesh = trimesh.Trimesh(
                        vertices=layer_vertices,
                        faces=layer_faces
                    )
                    
                    # Create collision mesh for this layer
                    collision_mesh = PhysicsUtils.optimize_collision_mesh(layer_mesh)
                    layers.append({
                        'mesh': layer_mesh,
                        'collision': collision_mesh,
                        'height_range': (height_thresholds[i-1] if i > 0 else -np.inf, 
                                       threshold if i < len(height_thresholds) else np.inf)
                    })
        
        return layers

    @staticmethod
    def export_unity_physics(mesh, collision_mesh, filename, material_type='default'):
        """Export mesh with Unity physics properties."""
        # Get physics material
        physics_material = PhysicsUtils.create_physics_material(material_type)
        
        # Create Unity physics metadata
        unity_metadata = {
            'physics_material': physics_material,
            'collision_type': 'mesh',
            'is_trigger': False,
            'is_static': True,
            'mass': physics_material['density'] * mesh.volume if hasattr(mesh, 'volume') else 1.0
        }
        
        # Save mesh files
        mesh.export(filename)
        collision_mesh.export(filename.replace('.obj', '_collision.obj'))
        
        # Save physics metadata
        import json
        metadata_file = filename.replace('.obj', '_physics.json')
        with open(metadata_file, 'w') as f:
            json.dump(unity_metadata, f, indent=2)
        
        return unity_metadata

    @staticmethod
    def create_water_physics(mesh, water_level=0.0, flow_direction=(0, 0, -1)):
        """Create water physics properties."""
        water_physics = {
            'water_level': water_level,
            'flow_direction': flow_direction,
            'flow_speed': 1.0,
            'viscosity': 0.8,
            'buoyancy': 1.0,
            'surface_tension': 0.1,
            'is_fluid': True
        }
        
        return water_physics

    @staticmethod
    def create_wind_physics(wind_direction=(1, 0, 0), wind_strength=1.0):
        """Create wind physics properties."""
        wind_physics = {
            'direction': wind_direction,
            'strength': wind_strength,
            'turbulence': 0.2,
            'gust_frequency': 0.1,
            'gust_strength': 0.5
        }
        
        return wind_physics 