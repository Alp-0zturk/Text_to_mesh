# Unity Import Guide

This guide explains how to import the generated 3D meshes into Unity with proper materials, colors, and collision.

## Generated Files

For each mesh generation, you'll get these files:

1. **`mesh_name.obj`** - Visual mesh with vertex colors
2. **`mesh_name_collision.obj`** - Optimized collision mesh
3. **`mesh_name_prefab.json`** - Unity prefab metadata with materials and physics

## Import Process

### Step 1: Import Meshes into Unity

1. **Create a new Unity project** or open your existing project
2. **Create an `Assets/Models` folder** in your project
3. **Drag and drop** the `.obj` files into the `Assets/Models` folder
4. **Select the imported mesh** in the Project window
5. **In the Inspector**, ensure these settings:
   - **Model** tab:
     - Scale Factor: `1`
     - Import Blendshapes: `✓`
     - Generate Normals: `✓`
     - Generate Tangents: `✓`
   - **Rig** tab:
     - Animation Type: `None`
   - **Materials** tab:
     - Material Creation Mode: `Standard (Specular setup)`
     - Location: `Use External Materials (Legacy)`

### Step 2: Create Materials

The system generates appropriate materials for different object types:

#### Terrain Materials
- **TerrainMaterial**: Green terrain with low smoothness
- **RockMaterial**: Gray rock with medium friction
- **SnowMaterial**: White snow with high smoothness

#### Environment Materials
- **ForestMaterial**: Dark green for forests
- **SandMaterial**: Beige sand with low smoothness
- **WaterMaterial**: Blue water with high smoothness

#### Basic Shape Materials
- **DefaultMaterial**: Standard gray material

### Step 3: Set Up Physics Materials

Create physics materials for proper collision behavior:

1. **Right-click** in Project window → **Create** → **Physics Material**
2. **Name it** according to the type (e.g., "GrassPhysicsMaterial")
3. **Set properties** based on the prefab JSON data:
   - **Friction**: 0.6-0.9 (higher for rough surfaces)
   - **Bounciness**: 0.0-0.3 (higher for bouncy surfaces)
   - **Friction Combine**: Average
   - **Bounce Combine**: Average

### Step 4: Create GameObjects

#### Method 1: Manual Setup

1. **Create an empty GameObject** in your scene
2. **Add MeshRenderer component**:
   - Drag the visual mesh to the Mesh field
   - Assign the appropriate material
3. **Add MeshCollider component**:
   - Drag the collision mesh to the Mesh field
   - Check "Convex" for dynamic objects
   - Assign the physics material
4. **Add Rigidbody** (if needed):
   - Check "Is Kinematic" for static objects
   - Uncheck "Use Gravity" for static objects

#### Method 2: Using the Prefab JSON

The `_prefab.json` file contains all the component settings. You can use this as a reference:

```json
{
  "name": "Mountain",
  "components": {
    "MeshRenderer": {
      "enabled": true,
      "material": "RockMaterial"
    },
    "MeshCollider": {
      "enabled": true,
      "convex": true,
      "isTrigger": false,
      "physicsMaterial": "RockPhysicsMaterial"
    },
    "Rigidbody": {
      "enabled": false,
      "isKinematic": true,
      "useGravity": false
    }
  }
}
```

### Step 5: Position and Scale

All meshes are automatically:
- **Rotated 90° on X-axis** (Y→Z, Z→-Y)
- **Scaled 10x larger** (1 unit = 10 meters in Unity)

You can adjust the Transform component as needed:
- **Position**: Set to desired location
- **Rotation**: Adjust if needed (90° X-rotation already applied)
- **Scale**: Modify if you want different size

## Material Types and Properties

### Terrain Materials

| Material | Color | Metallic | Smoothness | Use Case |
|----------|-------|----------|------------|----------|
| TerrainMaterial | Green (0.3, 0.6, 0.3) | 0.0 | 0.3 | General terrain |
| RockMaterial | Gray (0.5, 0.5, 0.5) | 0.1 | 0.2 | Rocky surfaces |
| SnowMaterial | White (0.9, 0.9, 0.9) | 0.0 | 0.8 | Snow-capped peaks |

### Environment Materials

| Material | Color | Metallic | Smoothness | Use Case |
|----------|-------|----------|------------|----------|
| ForestMaterial | Dark Green (0.2, 0.5, 0.2) | 0.0 | 0.4 | Forest areas |
| SandMaterial | Beige (0.8, 0.7, 0.5) | 0.0 | 0.1 | Desert/sand |
| WaterMaterial | Blue (0.0, 0.3, 0.8, 0.8) | 0.0 | 1.0 | Water bodies |

### Physics Materials

| Material | Friction | Bounciness | Use Case |
|----------|----------|------------|----------|
| GrassPhysicsMaterial | 0.8 | 0.1 | Grass/terrain |
| RockPhysicsMaterial | 0.4 | 0.2 | Rock surfaces |
| SandPhysicsMaterial | 0.9 | 0.0 | Sand/desert |
| WaterPhysicsMaterial | 0.1 | 0.0 | Water |
| SnowPhysicsMaterial | 0.7 | 0.3 | Snow |

## Advanced Setup

### Terrain Layers

For complex terrain, you can create multiple material layers based on height:

1. **Create a Terrain GameObject**
2. **Add Terrain component**
3. **Set up multiple terrain layers**:
   - Grass layer for low elevations
   - Rock layer for medium elevations
   - Snow layer for high elevations
4. **Paint the layers** based on height

### LOD (Level of Detail)

For performance optimization:

1. **Create multiple mesh versions** at different resolutions
2. **Set up LOD Group component**
3. **Assign meshes** to different LOD levels
4. **Set distance thresholds** for LOD switching

### Collision Optimization

- **Use convex collision** for dynamic objects
- **Use mesh collision** for static complex shapes
- **Simplify collision meshes** for better performance
- **Combine collision meshes** for large scenes

## Troubleshooting

### Common Issues

1. **Mesh appears black**:
   - Check if material is assigned
   - Ensure lighting is set up
   - Verify shader compatibility

2. **Collision not working**:
   - Ensure MeshCollider is enabled
   - Check if mesh is convex (for dynamic objects)
   - Verify physics material is assigned

3. **Wrong scale/orientation**:
   - Remember: 10x scaling and 90° X-rotation already applied
   - Adjust Transform component as needed

4. **Performance issues**:
   - Use LOD for complex meshes
   - Simplify collision meshes
   - Combine static objects

### Performance Tips

1. **Use LOD Groups** for complex terrain
2. **Simplify collision meshes** for better physics performance
3. **Combine static objects** to reduce draw calls
4. **Use occlusion culling** for large scenes
5. **Optimize materials** by sharing textures

## Example Scene Setup

Here's a complete example of setting up a mountain scene:

1. **Import mountain mesh** and collision mesh
2. **Create RockMaterial** with gray color and low smoothness
3. **Create RockPhysicsMaterial** with medium friction
4. **Set up GameObject**:
   - MeshRenderer with mountain mesh and RockMaterial
   - MeshCollider with collision mesh and RockPhysicsMaterial
   - Rigidbody (Is Kinematic = true, Use Gravity = false)
5. **Position and scale** as needed
6. **Add lighting** and camera setup

## Unity Version Compatibility

This system is compatible with:
- **Unity 2020.3 LTS** and newer
- **Built-in Render Pipeline**
- **Universal Render Pipeline (URP)**
- **High Definition Render Pipeline (HDRP)**

For URP/HDRP, you may need to:
1. **Convert materials** to the appropriate shader
2. **Adjust lighting** settings
3. **Update physics materials** if needed

## Support

If you encounter issues:
1. Check the console for error messages
2. Verify all files are properly imported
3. Ensure Unity version compatibility
4. Check material and shader settings 