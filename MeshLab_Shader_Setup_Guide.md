# MeshLab Vertex Color Shader Setup Guide

## Overview
These GLSL shaders allow MeshLab to display vertex colors from your generated meshes with proper lighting and material effects.

## Files Provided
- `VertexColorShader.gdp` - Advanced vertex color shader with lighting
- `SimpleVertexColor.gdp` - Basic vertex color display shader
- `MeshLab_SimpleVertexColor.glsl` - Alternative single-file shader
- This guide

## Quick Setup

### Option 1: Using MeshLab's Built-in Vertex Color Display (Easiest)
1. **Open your mesh** in MeshLab (the .obj file with vertex colors)
2. **Go to Render menu** → **Render Mode** → **Color per Vertex**
3. **Vertex colors should display** immediately!

### Option 2: Custom GDP Shader Setup (Advanced)
If you want more control with custom lighting:

1. **Copy .gdp shader files** to MeshLab's shader directory:
   - Windows: `C:\Program Files\MeshLab\shaders\`
   - Mac: `/Applications/meshlab.app/Contents/shaders/`
   - Linux: `/usr/share/meshlab/shaders/`

2. **Open MeshLab** and load your colored mesh

3. **Load the shader**:
   - Go to **Render** → **Shaders** → **Load Shader**
   - Select `VertexColorShader.gdp` or `SimpleVertexColor.gdp`

4. **Apply the shader**:
   - The shader should appear in your Render Mode options
   - Go to **Render** → **Render Mode** → Select your loaded shader

## MeshLab Render Modes for Vertex Colors

### Basic Vertex Color Display
- **Render** → **Render Mode** → **Color per Vertex**
- Shows vertex colors directly without additional lighting

### Vertex Color + Lighting
- **Render** → **Render Mode** → **Color per Vertex + Lighting**
- Combines vertex colors with scene lighting

### Flat Shading
- **Render** → **Shading** → **Flat**
- Shows distinct color regions clearly

### Smooth Shading  
- **Render** → **Shading** → **Smooth**
- Smoothly blends colors between vertices

## Adjusting Display Settings

### Lighting Controls
- **View** → **Show Layer Dialog** → **Decorations** tab
- Adjust light position and intensity
- Enable/disable different light types

### Color Intensity
- **Render** → **Render Mode** → **Color per Vertex**
- Some versions allow color intensity adjustment

### Material Properties
- **Render** → **Material Properties**
- Adjust ambient, diffuse, and specular properties

## Troubleshooting

### Vertex Colors Not Visible
1. **Check mesh has vertex colors**:
   - **Filters** → **Color Creation and Processing** → **Colorize by vertex quality**
   - If no colors exist, the mesh may not have vertex color data

2. **Force vertex color display**:
   - **Render** → **Render Mode** → **Color per Vertex**
   - Make sure this mode is selected

3. **Reset view**:
   - **View** → **Reset Trackball**
   - **View** → **Fit All**

### Colors Look Wrong
1. **Check color range**:
   - Vertex colors should be in 0-1 range
   - If colors appear too dark/bright, adjust lighting

2. **Verify mesh import**:
   - Make sure the .obj file was generated with vertex colors
   - Check that MeshLab imported the colors correctly

### Shader Errors
1. **Check OpenGL version**:
   - MeshLab requires OpenGL 2.0+ for custom shaders
   - Update graphics drivers if needed

2. **GDP file not loading**:
   - Ensure .gdp files are in MeshLab's shader directory
   - Check that XML format is valid
   - Try the SimpleVertexColor.gdp first (simpler shader)

3. **Shader compilation errors**:
   - Check MeshLab console for error messages
   - Try switching between the two GDP files provided

## Alternative Methods

### Using PLY Format
If OBJ vertex colors don't work:
1. **Export to PLY** from the mesh generator (if supported)
2. **Import PLY in MeshLab** - often better vertex color support
3. **PLY typically preserves vertex colors** more reliably

### Manual Color Assignment
If vertex colors are missing:
1. **Use the JSON color data** to manually assign colors
2. **Filters** → **Color Creation and Processing** → **Per Vertex Color Function**
3. **Use vertex indices** from JSON to assign specific colors

### Texture Mapping Alternative
Convert vertex colors to texture:
1. **Filters** → **Texture** → **Vertex Color to Texture**
2. **Creates a texture map** from vertex colors
3. **Apply as regular texture** with UV mapping

## Performance Tips

1. **Large meshes**: Use simplified shading for better performance
2. **Complex lighting**: Disable advanced lighting for real-time viewing
3. **Memory usage**: Close other applications when working with large colored meshes

## Expected Results

With vertex colors properly displayed, you should see:
- **Blue regions**: Water areas, streams, lakes
- **Green regions**: Vegetation, trees, grass
- **Brown regions**: Terrain, soil, rocks
- **Gray regions**: Stone, concrete surfaces
- **White regions**: Snow, ice, bright areas

The colors should smoothly blend between semantic regions, creating a realistic appearance of your generated 3D environment.

## Common MeshLab Vertex Color Commands

```
Render → Render Mode → Color per Vertex
Render → Shading → Smooth/Flat
Filters → Color Creation and Processing → (various color tools)
View → Show Layer Dialog → Decorations (lighting controls)
```

## Getting Help

If vertex colors still don't appear:
1. **Check MeshLab version** - newer versions have better color support
2. **Try different mesh formats** - PLY often works better than OBJ for colors
3. **Check the color legend PNG** to verify expected colors
4. **Test with a simple colored mesh** first

The semantic mesh coloring system should work seamlessly with MeshLab's built-in vertex color display modes! 