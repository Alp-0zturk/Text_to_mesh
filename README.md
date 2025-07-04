# Text to 3D Mesh Generator

A powerful text-to-3D mesh generator that creates **Unity-ready** terrain, environments, and basic shapes from textual descriptions. This project generates realistic 3D landscapes including mountains, forests, lakes, and deserts using procedural generation techniques with **automatic colors and collision**.

## 🎮 Unity-Ready Features

- **🎨 Automatic Colors**: Vertex colors applied based on height and environment type
- **💥 Collision Meshes**: Optimized collision meshes for Unity physics
- **🏗️ Unity Materials**: Pre-configured materials with proper shaders and properties
- **⚡ Physics Materials**: Realistic friction and bounciness for different surfaces
- **📦 Prefab Metadata**: JSON files with complete Unity component setup
- **🔄 Automatic Transformations**: 90° X-axis rotation and 10x scaling for Unity
- **📐 Proper Coordinate System**: Left-handed coordinate system for Unity

## Features
- **Terrain Generation**: Create mountains, hills, valleys, plateaus, and canyons
- **Environment Creation**: Generate forests, lakes, deserts, and other landscapes
- **Procedural Generation**: Uses Perlin noise for realistic terrain variation
- **Basic Shapes**: Traditional geometric primitives (cube, sphere, cylinder, cone)
- **Local Processing**: Runs entirely on your machine without external dependencies
- **Unity Integration**: Optimized mesh output for Unity game development
- **Automatic Transformations**: All outputs are automatically rotated and scaled for optimal viewing

## Automatic Transformations
All generated meshes automatically receive the following transformations:
- **90° X-axis Rotation**: Rotates Y→Z and Z→-Y for better orientation
- **10x Scaling**: Increases all dimensions by 10x for better visibility and detail

## Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Project Structure
- `main.py`: Entry point of the application
- `src/`
  - `mesh_generator.py`: Core mesh generation logic
  - `text_processor.py`: Text processing and interpretation
  - `primitives.py`: 3D primitive shapes and terrain generation
- `utils/`
  - `terrain_utils.py`: Advanced terrain generation utilities
  - `unity_utils.py`: Unity-specific mesh optimization and material generation
  - `physics_utils.py`: Physics material properties and collision mesh creation

## Usage Examples

### Terrain Generation
```
"a tall mountain peak"           # Creates a mountain with peak
"rolling hills landscape"        # Gentle rolling hills
"rocky mountain terrain"         # Mountainous terrain with rocks
"deep valley with river"         # Valley terrain
"flat plateau landscape"         # Plateau terrain
"canyon with steep walls"        # Canyon terrain
```

### Environment Creation
```
"dense forest with trees"        # Forest environment with scattered trees
"lake surrounded by terrain"     # Lake with surrounding landscape
"desert with sand dunes"         # Desert environment with dunes
"alpine mountain range"          # Snow-capped mountain range
```

### Basic Shapes
```
"large cube 5 meters"            # 5-meter cube (scaled to 50m)
"small sphere"                   # Small sphere (scaled to 10x size)
"tall cylinder"                  # Tall cylinder (scaled to 10x size)
"wide cone"                      # Wide cone (scaled to 10x size)
```

### Advanced Parameters
```
"mountain 100 meters wide high resolution"  # Large, detailed mountain
"forest 50 meters tall"                     # Forest with specified height
"terrain with erosion"                      # Terrain with erosion effects
```

## Terrain Types
- **Mountain**: Steep, rocky terrain with peaks
- **Hills**: Gentle rolling hills
- **Valley**: Depressed terrain with river-like features
- **Plateau**: Flat elevated terrain
- **Canyon**: Deep, narrow valleys

## Environment Types
- **Forest**: Terrain with scattered trees
- **Lake**: Water body with surrounding landscape
- **Desert**: Sandy terrain with dunes and rocks

## Unity Material Types

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

## Technical Details
- **Noise Generation**: Uses Perlin noise for realistic terrain variation
- **Mesh Resolution**: Configurable detail levels
- **Erosion Simulation**: Optional hydraulic erosion effects
- **Texture Generation**: Automatic texture mapping based on height and slope
- **Unity Optimization**: Proper coordinate system and scaling for Unity
- **Automatic Transformations**: 90° X-axis rotation and 10x scaling applied to all outputs
- **Vertex Colors**: Automatic color assignment based on height and environment
- **Collision Optimization**: Simplified collision meshes for performance

## Output Files

For each generation, you get:

1. **`mesh_name.obj`** - Visual mesh with vertex colors
2. **`mesh_name_collision.obj`** - Optimized collision mesh
3. **`mesh_name_prefab.json`** - Unity prefab metadata with materials and physics

## Unity Import

### Quick Start
1. **Import meshes** into Unity Assets folder
2. **Create materials** based on the prefab JSON files
3. **Set up GameObjects** with MeshRenderer and MeshCollider
4. **Assign materials** and physics materials
5. **Position and scale** as needed

### Detailed Guide
See `UNITY_IMPORT_GUIDE.md` for complete Unity import instructions.

## Testing

Run the Unity export test to verify everything works:

```bash
python test_unity_export.py
```

This will generate test meshes with all Unity features enabled.

## Tips for Best Results
1. Use descriptive terms like "tall", "wide", "steep", "gentle"
2. Specify size with units: "100 meters wide"
3. Request high resolution for detailed terrain
4. Combine terrain types: "rocky mountain with forest"
5. Use environment keywords: "forest", "lake", "desert"
6. Remember that all outputs are 10x larger than specified
7. Colors and collision are automatically applied
8. Unity materials and physics are pre-configured

## Future Enhancements
- Integration with local AI models (Ollama, etc.)
- Real-time terrain preview
- Advanced texture and material generation
- Weather and seasonal effects
- Multi-scale terrain generation
- Unity package export
- Real-time collaboration features 