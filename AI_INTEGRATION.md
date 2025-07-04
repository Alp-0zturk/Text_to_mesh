# AI Integration Guide

This guide explains how to integrate local AI models with the Text-to-3D Mesh Generator for enhanced terrain creation.

## Supported AI Models

### Ollama (Recommended)
Ollama is a local AI model runner that supports various open-source models.

#### Installation
1. **macOS/Linux**: 
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Windows**: Download from [ollama.ai](https://ollama.ai)

#### Setup
1. Start Ollama:
   ```bash
   ollama serve
   ```

2. Pull a model (recommended models):
   ```bash
   # For terrain generation
   ollama pull llama3.2
   ollama pull mistral
   ollama pull codellama
   
   # For creative descriptions
   ollama pull llama3.2:3b
   ollama pull phi3
   ```

3. Test the model:
   ```bash
   ollama run llama3.2 "Hello, world!"
   ```

### Other Local AI Options

#### LM Studio
- Download from [lmstudio.ai](https://lmstudio.ai)
- Supports various GGUF models
- GUI interface for model management

#### Text Generation WebUI
- GitHub: [oobabooga/text-generation-webui](https://github.com/oobabooga/text-generation-webui)
- Supports multiple model formats
- Web-based interface

## Integration with Terrain Generator

### Basic Integration
The `AdvancedTerrainGenerator` class automatically detects and uses local AI models:

```python
from advanced_terrain_generator import AdvancedTerrainGenerator

# Initialize with AI support
generator = AdvancedTerrainGenerator(use_ai=True)

# Generate terrain with AI enhancement
mesh, confidence, output_file = generator.generate_terrain_with_ai(
    "a beautiful mountain landscape"
)
```

### Custom AI Endpoints
If using a different AI service or custom endpoint:

```python
# Custom endpoint
generator = AdvancedTerrainGenerator(
    use_ai=True, 
    ai_endpoint="http://localhost:8080"
)
```

### Batch Generation
Generate multiple terrains with AI enhancement:

```python
descriptions = [
    "snow-capped mountain range",
    "tropical rainforest",
    "desert oasis",
    "alpine meadow"
]

results = generator.batch_generate(descriptions)
```

## AI Enhancement Features

### Description Enhancement
The AI can enhance simple descriptions with detailed specifications:

**Input**: "mountain"
**AI Enhanced**: "a majestic mountain range with snow-capped peaks, rocky outcrops, and alpine vegetation, approximately 2000 meters high with steep cliffs and gentle lower slopes"

### Parameter Extraction
AI can extract specific parameters from natural language:

**Input**: "a large mountain with lots of trees"
**Extracted**: 
- Terrain type: mountain
- Size: large (100+ meters)
- Features: forested
- Scale: detailed

### Creative Variations
AI can suggest creative variations and combinations:

**Input**: "forest"
**AI Suggestions**:
- "dense pine forest with moss-covered rocks"
- "tropical rainforest with hanging vines"
- "autumn forest with colorful leaves"

## Configuration

### Model Selection
Different models work better for different tasks:

- **Llama 3.2**: Good for general terrain descriptions
- **Mistral**: Excellent for creative variations
- **CodeLlama**: Good for technical specifications
- **Phi-3**: Fast and efficient for simple tasks

### Prompt Engineering
Customize prompts for specific needs:

```python
def custom_enhancement_prompt(description):
    return f"""
    Create a detailed 3D terrain description for game development:
    Base description: "{description}"
    
    Include:
    - Terrain type and features
    - Scale and dimensions
    - Environmental elements
    - Technical specifications for mesh generation
    
    Format: Return only the enhanced description
    """
```

## Performance Optimization

### Model Size vs Speed
- **Small models** (3B-7B): Fast, good for basic enhancement
- **Medium models** (13B-34B): Balanced performance and quality
- **Large models** (70B+): Best quality, slower generation

### Caching
Implement caching for repeated descriptions:

```python
import hashlib
import json

class CachedTerrainGenerator(AdvancedTerrainGenerator):
    def __init__(self, cache_file="terrain_cache.json"):
        super().__init__()
        self.cache_file = cache_file
        self.cache = self._load_cache()
    
    def _load_cache(self):
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)
    
    def generate_terrain_with_ai(self, description, output_dir="output"):
        # Create cache key
        cache_key = hashlib.md5(description.encode()).hexdigest()
        
        if cache_key in self.cache:
            print("Using cached result")
            return self.cache[cache_key]
        
        # Generate new result
        result = super().generate_terrain_with_ai(description, output_dir)
        
        # Cache result
        self.cache[cache_key] = result
        self._save_cache()
        
        return result
```

## Troubleshooting

### Common Issues

1. **AI Model Not Available**
   - Check if Ollama is running: `ollama list`
   - Verify endpoint URL: `http://localhost:11434`
   - Test with: `curl http://localhost:11434/api/tags`

2. **Slow Generation**
   - Use smaller models for faster response
   - Reduce prompt complexity
   - Implement caching for repeated requests

3. **Poor Quality Results**
   - Try different models
   - Improve prompt engineering
   - Use more specific descriptions

4. **Memory Issues**
   - Close other applications
   - Use smaller models
   - Reduce batch size

### Debug Mode
Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

generator = AdvancedTerrainGenerator(use_ai=True)
```

## Future Enhancements

### Planned Features
- **Real-time AI suggestions** during typing
- **Multi-model ensemble** for better results
- **Style transfer** for different art styles
- **Interactive refinement** with AI feedback
- **Texture generation** using AI models

### Integration Ideas
- **Stable Diffusion** for texture generation
- **ControlNet** for guided terrain generation
- **DreamShaper** for artistic variations
- **Custom fine-tuned models** for specific terrain types

## Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [Model Hub](https://ollama.ai/library)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [Local AI Models List](https://github.com/awesome-selfhosted/awesome-selfhosted#ai) 