# Using JSON Color Data in Unity

## Overview
While you cannot directly drag .json files onto meshes in Unity, you can use the generated color data with the provided scripts and shaders.

## Quick Setup

### Method 1: Pre-Embedded Vertex Colors (Easiest)
The generated .obj files already contain vertex colors. Unity should import these automatically:

1. **Import the .obj file** into Unity
2. **Create a material** with the `Custom/VertexColor` shader
3. **Apply the material** to your mesh
4. **Vertex colors will be displayed** automatically

### Method 2: JSON Color Data Import (Advanced)
Use the `MeshColorImporter` script for more control:

1. **Add the script** to your GameObject with the mesh
2. **Assign the JSON file** as a TextAsset
3. **Click "Import Color Data"** in the inspector
4. **Colors will be applied** to the mesh

## Detailed Instructions

### Step 1: Import Generated Files
1. Copy your generated files to Unity's `Assets` folder:
   - `generated_scene.obj` (main mesh)
   - `generated_scene_color_info.json` (color data)
   - `generated_scene_color_legend.png` (color reference)

### Step 2: Create Vertex Color Material
1. Create a new Material
2. Set shader to `Custom/VertexColor`
3. Adjust properties:
   - `Color Intensity`: Controls how vibrant the vertex colors appear
   - `Smoothness`: Surface smoothness (0=rough, 1=smooth)
   - `Metallic`: Metallic properties

### Step 3: Apply to Mesh
1. Select your mesh GameObject
2. Assign the vertex color material
3. The mesh should now display semantic colors

### Step 4: Advanced Color Import (Optional)
If you want to modify colors or apply JSON data to different meshes:

1. **Add MeshColorImporter script** to your GameObject
2. **Assign the JSON file** (must be imported as TextAsset)
3. **Set target mesh** (or leave empty to use current GameObject's mesh)
4. **Click "Import Color Data"** button
5. **Colors will be applied** to the mesh

## Understanding the Color System

### Semantic Categories
The system automatically detects and colors different semantic regions:
- **Blue**: Water bodies, streams, lakes
- **Green**: Vegetation, trees, grass, moss
- **Brown**: Terrain, soil, rocks, mountains
- **Gray**: Stone, concrete, hard surfaces
- **White**: Snow, ice, bright surfaces

### Environment Types
The system supports multiple environment types:
- **Alpine**: Mountain/snow environments
- **Desert**: Arid/sandy environments  
- **Forest**: Wooded/green environments
- **Tropical**: Warm/humid environments
- **Tundra**: Cold/sparse environments
- **Volcanic**: Dark/rocky environments

### Color Effects
Generated colors include advanced effects:
- **Height variation**: Colors change based on elevation
- **Lighting effects**: Simulated ambient occlusion
- **Curvature shading**: Enhanced surface detail
- **Proximity effects**: Wetness near water
- **Natural noise**: Realistic color variation

## Troubleshooting

### Vertex Colors Not Showing
- Ensure you're using the `Custom/VertexColor` shader
- Check that the mesh has vertex colors imported
- Try increasing `Color Intensity` in the material

### JSON Import Fails
- Make sure the JSON file is imported as a TextAsset
- Check that the JSON format matches the expected structure
- Verify the mesh has the correct number of vertices

### Colors Look Wrong
- The mesh might not have vertex colors imported
- Try using the `MeshColorImporter` script to re-apply colors
- Check that the JSON file corresponds to the correct mesh

## Advanced Usage

### Custom Shaders
You can create custom shaders that use vertex colors:
```hlsl
// In your surface shader
struct Input
{
    float2 uv_MainTex;
    float4 color : COLOR;  // This gets vertex colors
};

void surf (Input IN, inout SurfaceOutputStandard o)
{
    o.Albedo = IN.color.rgb;  // Use vertex colors directly
}
```

### Runtime Color Changes
You can modify colors at runtime:
```csharp
// Get the mesh
Mesh mesh = GetComponent<MeshFilter>().mesh;

// Modify vertex colors
Color[] colors = mesh.colors;
colors[0] = Color.red;  // Change first vertex to red
mesh.colors = colors;
```

### Blending with Textures
The vertex color shader supports texture blending:
1. Assign a texture to `_MainTex`
2. The texture will be multiplied with vertex colors
3. Use white textures for pure vertex colors
4. Use detailed textures for enhanced surfaces

## File Structure
```
Assets/
├── Models/
│   └── generated_scene.obj          # Main mesh with vertex colors
├── Scripts/
│   └── MeshColorImporter.cs         # Color data importer
├── Shaders/
│   └── VertexColorShader.shader     # Vertex color display shader
├── Materials/
│   └── VertexColorMaterial.mat      # Material using vertex colors
└── Data/
    ├── generated_scene_color_info.json    # Color data
    └── generated_scene_color_legend.png   # Color reference
```

## Tips for Best Results

1. **Use appropriate lighting**: Vertex colors look best with good lighting setup
2. **Adjust color intensity**: Fine-tune the `Color Intensity` parameter
3. **Combine with textures**: Use subtle textures for enhanced detail
4. **Test different environments**: Try various Unity lighting environments
5. **Consider post-processing**: Unity's post-processing can enhance colors

## Performance Notes

- Vertex colors have minimal performance impact
- The JSON import is a one-time operation
- Meshes with vertex colors render efficiently
- No additional texture memory is used for colors

## Support

For issues or questions:
1. Check the Unity Console for error messages
2. Verify file formats and imports
3. Test with simpler meshes first
4. Review the generated color legend for expected results 