// Simple Vertex Color Shader for MeshLab
// This is a combined vertex and fragment shader for basic vertex color display

#ifdef VERTEX_SHADER
attribute vec3 vertex;
attribute vec3 normal;
attribute vec4 color;

uniform mat4 gl_ModelViewProjectionMatrix;
uniform mat3 gl_NormalMatrix;

varying vec4 vertex_color;
varying vec3 vertex_normal;

void main()
{
    gl_Position = gl_ModelViewProjectionMatrix * vec4(vertex, 1.0);
    vertex_color = color;
    vertex_normal = normalize(gl_NormalMatrix * normal);
}
#endif

#ifdef FRAGMENT_SHADER
varying vec4 vertex_color;
varying vec3 vertex_normal;

uniform vec3 light_direction;
uniform float ambient_strength;
uniform float diffuse_strength;

void main()
{
    // Simple lighting calculation
    vec3 norm = normalize(vertex_normal);
    vec3 light_dir = normalize(light_direction);
    
    // Ambient component
    vec3 ambient = ambient_strength * vertex_color.rgb;
    
    // Diffuse component
    float diff = max(dot(norm, light_dir), 0.0);
    vec3 diffuse = diffuse_strength * diff * vertex_color.rgb;
    
    // Combine lighting
    vec3 result = ambient + diffuse;
    
    gl_FragColor = vec4(result, vertex_color.a);
}
#endif 