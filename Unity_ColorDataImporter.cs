using System.Collections.Generic;
using UnityEngine;
using UnityEditor;
using System.IO;

namespace MeshColoring
{
    [System.Serializable]
    public class ColorInfo
    {
        public List<float[]> vertex_colors;
        public Dictionary<string, float[]> color_legend;
        public List<string> unique_semantics;
        public string environment_type;
        public int total_vertices;
    }

    [System.Serializable]
    public class ColorData
    {
        public ColorInfo color_info;
        public string environment_type;
        public Dictionary<string, object> analysis_results;
    }

    public class MeshColorImporter : MonoBehaviour
    {
        [Header("Color Data")]
        public TextAsset colorDataJson;
        public MeshFilter targetMeshFilter;
        public MeshRenderer targetMeshRenderer;
        
        [Header("Material Settings")]
        public Material vertexColorMaterial;
        public bool createNewMaterial = true;
        
        [Header("Debug")]
        public bool showColorLegend = true;
        
        private ColorData colorData;
        private Color[] vertexColors;
        
        public void ImportColorData()
        {
            if (colorDataJson == null)
            {
                Debug.LogError("No color data JSON file assigned!");
                return;
            }
            
            if (targetMeshFilter == null)
            {
                targetMeshFilter = GetComponent<MeshFilter>();
            }
            
            if (targetMeshRenderer == null)
            {
                targetMeshRenderer = GetComponent<MeshRenderer>();
            }
            
            try
            {
                // Parse JSON data
                string jsonText = colorDataJson.text;
                colorData = JsonUtility.FromJson<ColorData>(jsonText);
                
                // Apply vertex colors to mesh
                ApplyVertexColors();
                
                // Create/assign material
                if (createNewMaterial)
                {
                    CreateVertexColorMaterial();
                }
                
                Debug.Log($"✅ Successfully imported color data for {colorData.environment_type} environment");
                Debug.Log($"Applied colors to {colorData.color_info.total_vertices} vertices");
                Debug.Log($"Semantic regions: {string.Join(", ", colorData.color_info.unique_semantics)}");
                
            }
            catch (System.Exception e)
            {
                Debug.LogError($"Failed to import color data: {e.Message}");
            }
        }
        
        private void ApplyVertexColors()
        {
            if (targetMeshFilter.mesh == null)
            {
                Debug.LogError("No mesh found on target MeshFilter!");
                return;
            }
            
            Mesh mesh = targetMeshFilter.mesh;
            
            // Convert vertex colors from JSON format
            if (colorData.color_info.vertex_colors != null)
            {
                vertexColors = new Color[colorData.color_info.vertex_colors.Count];
                
                for (int i = 0; i < colorData.color_info.vertex_colors.Count; i++)
                {
                    float[] colorArray = colorData.color_info.vertex_colors[i];
                    if (colorArray.Length >= 3)
                    {
                        vertexColors[i] = new Color(
                            colorArray[0],
                            colorArray[1],
                            colorArray[2],
                            colorArray.Length > 3 ? colorArray[3] : 1.0f
                        );
                    }
                }
                
                // Apply to mesh
                mesh.colors = vertexColors;
                Debug.Log($"Applied {vertexColors.Length} vertex colors to mesh");
            }
        }
        
        private void CreateVertexColorMaterial()
        {
            if (vertexColorMaterial == null)
            {
                // Create a new material with vertex color support
                Material material = new Material(Shader.Find("Standard"));
                material.name = $"Generated_{colorData.environment_type}_Material";
                
                // Enable vertex colors (this depends on your shader)
                // For standard shader, you might need a custom shader
                material.EnableKeyword("_VERTEX_COLORS");
                
                targetMeshRenderer.material = material;
                vertexColorMaterial = material;
                
                Debug.Log($"Created new material: {material.name}");
            }
            else
            {
                targetMeshRenderer.material = vertexColorMaterial;
            }
        }
        
        // Editor-only method to show color legend
        #if UNITY_EDITOR
        private void OnDrawGizmos()
        {
            if (showColorLegend && colorData?.color_info?.color_legend != null)
            {
                Vector3 position = transform.position + Vector3.up * 2f;
                
                int index = 0;
                foreach (var kvp in colorData.color_info.color_legend)
                {
                    string semantic = kvp.Key;
                    float[] colorArray = kvp.Value;
                    
                    if (colorArray.Length >= 3)
                    {
                        Color color = new Color(colorArray[0], colorArray[1], colorArray[2]);
                        Gizmos.color = color;
                        
                        Vector3 gizmoPos = position + Vector3.right * (index * 0.5f);
                        Gizmos.DrawSphere(gizmoPos, 0.1f);
                        
                        UnityEditor.Handles.Label(gizmoPos + Vector3.up * 0.2f, semantic);
                    }
                    
                    index++;
                }
            }
        }
        #endif
    }
    
    #if UNITY_EDITOR
    [CustomEditor(typeof(MeshColorImporter))]
    public class MeshColorImporterEditor : Editor
    {
        public override void OnInspectorGUI()
        {
            DrawDefaultInspector();
            
            MeshColorImporter importer = (MeshColorImporter)target;
            
            EditorGUILayout.Space();
            
            if (GUILayout.Button("Import Color Data", GUILayout.Height(30)))
            {
                importer.ImportColorData();
            }
            
            EditorGUILayout.Space();
            
            if (importer.colorDataJson != null)
            {
                EditorGUILayout.HelpBox(
                    "1. Assign the JSON color data file\n" +
                    "2. Assign the target mesh (or it will use this GameObject's mesh)\n" +
                    "3. Click 'Import Color Data' to apply colors\n" +
                    "4. The mesh will be colored based on semantic regions",
                    MessageType.Info
                );
            }
            else
            {
                EditorGUILayout.HelpBox(
                    "Please assign a color data JSON file generated by the mesh coloring system.",
                    MessageType.Warning
                );
            }
        }
    }
    #endif
} 