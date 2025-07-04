import numpy as np
import trimesh
import json
import os

def prepare_for_unity(mesh):
    """Prepare the mesh for Unity import by ensuring correct orientation and scale."""
    # Make a copy of the mesh to avoid modifying the original
    unity_mesh = mesh.copy()
    
    # Unity uses a left-handed coordinate system, while most 3D software uses right-handed
    # Flip the Z-axis to convert from right-handed to left-handed
    unity_mesh.vertices[:, 2] *= -1
    
    # Ensure the mesh has proper face normals
    unity_mesh.fix_normals()
    
    # Ensure the mesh is centered
    unity_mesh.vertices -= unity_mesh.center_mass
    
    # Scale the mesh to be more visible (if it's too small)
    bounds = unity_mesh.bounds
    max_dim = np.max(np.abs(bounds[1] - bounds[0]))
    if max_dim < 0.1:  # If the mesh is very small
        scale_factor = 1.0 / max_dim
        unity_mesh.vertices *= scale_factor
    
    return unity_mesh

def save_for_unity(mesh, filename):
    """Save mesh optimized for Unity with proper coordinate system and colors."""
    # Ensure mesh has proper normals
    if not hasattr(mesh, 'face_normals') or mesh.face_normals is None:
        mesh.face_normals = mesh.face_normals
    
    # Ensure mesh has proper vertex normals
    if not hasattr(mesh, 'vertex_normals') or mesh.vertex_normals is None:
        mesh.vertex_normals = mesh.vertex_normals
    
    # Ensure vertex colors are in the correct format
    if hasattr(mesh, 'visual') and hasattr(mesh.visual, 'vertex_colors'):
        # Ensure colors are RGBA uint8 format
        colors = mesh.visual.vertex_colors
        if colors.dtype != np.uint8:
            colors = (colors * 255).astype(np.uint8)
        mesh.visual.vertex_colors = colors
    
    # Export with proper settings for Unity
    mesh.export(filename, include_normals=True, include_texture=True)

def create_unity_material(material_type='default'):
    """Create Unity material properties."""
    materials = {
        'default': {
            'name': 'DefaultMaterial',
            'shader': 'Standard',
            'color': [0.5, 0.5, 0.5, 1.0],
            'metallic': 0.0,
            'smoothness': 0.5
        },
        'terrain': {
            'name': 'TerrainMaterial',
            'shader': 'Standard',
            'color': [0.3, 0.6, 0.3, 1.0],
            'metallic': 0.0,
            'smoothness': 0.3
        },
        'rock': {
            'name': 'RockMaterial',
            'shader': 'Standard',
            'color': [0.5, 0.5, 0.5, 1.0],
            'metallic': 0.1,
            'smoothness': 0.2
        },
        'snow': {
            'name': 'SnowMaterial',
            'shader': 'Standard',
            'color': [0.9, 0.9, 0.9, 1.0],
            'metallic': 0.0,
            'smoothness': 0.8
        },
        'water': {
            'name': 'WaterMaterial',
            'shader': 'Standard',
            'color': [0.0, 0.3, 0.8, 0.8],
            'metallic': 0.0,
            'smoothness': 1.0
        },
        'sand': {
            'name': 'SandMaterial',
            'shader': 'Standard',
            'color': [0.8, 0.7, 0.5, 1.0],
            'metallic': 0.0,
            'smoothness': 0.1
        },
        'forest': {
            'name': 'ForestMaterial',
            'shader': 'Standard',
            'color': [0.2, 0.5, 0.2, 1.0],
            'metallic': 0.0,
            'smoothness': 0.4
        }
    }
    
    return materials.get(material_type, materials['default'])

def create_unity_physics_material(material_type='default'):
    """Create Unity physics material properties."""
    physics_materials = {
        'default': {
            'name': 'DefaultPhysicsMaterial',
            'friction': 0.6,
            'bounciness': 0.0,
            'frictionCombine': 'Average',
            'bounceCombine': 'Average'
        },
        'grass': {
            'name': 'GrassPhysicsMaterial',
            'friction': 0.8,
            'bounciness': 0.1,
            'frictionCombine': 'Average',
            'bounceCombine': 'Average'
        },
        'rock': {
            'name': 'RockPhysicsMaterial',
            'friction': 0.4,
            'bounciness': 0.2,
            'frictionCombine': 'Average',
            'bounceCombine': 'Average'
        },
        'sand': {
            'name': 'SandPhysicsMaterial',
            'friction': 0.9,
            'bounciness': 0.0,
            'frictionCombine': 'Average',
            'bounceCombine': 'Average'
        },
        'water': {
            'name': 'WaterPhysicsMaterial',
            'friction': 0.1,
            'bounciness': 0.0,
            'frictionCombine': 'Average',
            'bounceCombine': 'Average'
        },
        'snow': {
            'name': 'SnowPhysicsMaterial',
            'friction': 0.7,
            'bounciness': 0.3,
            'frictionCombine': 'Average',
            'bounceCombine': 'Average'
        }
    }
    
    return physics_materials.get(material_type, physics_materials['default'])

def export_unity_prefab(mesh, collision_mesh, filename, material_type='default', physics_type='default'):
    """Export complete Unity-ready prefab with materials and physics."""
    base_name = os.path.splitext(os.path.basename(filename))[0]
    
    # Create Unity material
    material = create_unity_material(material_type)
    physics_material = create_unity_physics_material(physics_type)
    
    # Save visual mesh
    save_for_unity(mesh, filename)
    
    # Save collision mesh (always use the same base as filename)
    collision_filename = filename.replace('.obj', '_collision.obj')
    save_for_unity(collision_mesh, collision_filename)
    
    # Create Unity prefab metadata
    prefab_data = {
        'name': base_name,
        'visual_mesh': os.path.basename(filename),
        'collision_mesh': os.path.basename(collision_filename),
        'material': material,
        'physics_material': physics_material,
        'transform': {
            'position': [0, 0, 0],
            'rotation': [0, 0, 0],
            'scale': [1, 1, 1]
        },
        'components': {
            'MeshRenderer': {
                'enabled': True,
                'material': material['name']
            },
            'MeshCollider': {
                'enabled': True,
                'convex': True,
                'isTrigger': False,
                'physicsMaterial': physics_material['name']
            },
            'Rigidbody': {
                'enabled': False,  # Static by default
                'isKinematic': True,
                'useGravity': False
            }
        }
    }
    
    # Save prefab metadata (always use the same base as filename)
    prefab_filename = filename.replace('.obj', '_prefab.json')
    with open(prefab_filename, 'w') as f:
        json.dump(prefab_data, f, indent=2)
    
    return prefab_data

def create_unity_terrain_layers(mesh, height_thresholds=None):
    """Create Unity terrain layers based on height."""
    if height_thresholds is None:
        heights = mesh.vertices[:, 2]
        min_h, max_h = heights.min(), heights.max()
        height_thresholds = [
            min_h + (max_h - min_h) * 0.2,  # Grass
            min_h + (max_h - min_h) * 0.5,  # Rock
            min_h + (max_h - min_h) * 0.8   # Snow
        ]
    
    layers = []
    heights = mesh.vertices[:, 2]
    
    layer_types = ['grass', 'rock', 'snow']
    
    for i, threshold in enumerate(height_thresholds):
        if i == 0:
            mask = heights <= threshold
        elif i == len(height_thresholds) - 1:
            mask = heights > height_thresholds[i-1]
        else:
            mask = (heights > height_thresholds[i-1]) & (heights <= threshold)
        
        if np.any(mask):
            layer_material = create_unity_material(layer_types[i])
            layer_physics = create_unity_physics_material(layer_types[i])
            
            layers.append({
                'name': f'{layer_types[i].capitalize()}Layer',
                'material': layer_material,
                'physics_material': layer_physics,
                'height_range': (height_thresholds[i-1] if i > 0 else -np.inf, 
                               threshold if i < len(height_thresholds) else np.inf)
            })
    
    return layers

def export_unity_scene(meshes_data, scene_name="GeneratedScene"):
    """Export a complete Unity scene with multiple objects."""
    scene_data = {
        'name': scene_name,
        'objects': [],
        'materials': {},
        'physics_materials': {}
    }
    
    for i, (mesh, collision_mesh, mesh_type, material_type) in enumerate(meshes_data):
        obj_name = f"{mesh_type}_{i}"
        
        # Save individual mesh files
        mesh_filename = f"output/{obj_name}.obj"
        collision_filename = f"output/{obj_name}_collision.obj"
        
        save_for_unity(mesh, mesh_filename)
        save_for_unity(collision_mesh, collision_filename)
        
        # Create materials
        material = create_unity_material(material_type)
        physics_material = create_unity_physics_material(material_type)
        
        # Add to scene
        scene_data['objects'].append({
            'name': obj_name,
            'mesh_file': mesh_filename,
            'collision_file': collision_filename,
            'material': material['name'],
            'physics_material': physics_material['name'],
            'transform': {
                'position': [0, 0, 0],
                'rotation': [0, 0, 0],
                'scale': [1, 1, 1]
            }
        })
        
        # Add materials to scene
        scene_data['materials'][material['name']] = material
        scene_data['physics_materials'][physics_material['name']] = physics_material
    
    # Save scene data
    scene_filename = f"output/{scene_name}.json"
    with open(scene_filename, 'w') as f:
        json.dump(scene_data, f, indent=2)
    
    return scene_data 