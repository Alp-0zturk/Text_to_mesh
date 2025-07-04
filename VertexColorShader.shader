Shader "Custom/VertexColor"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}
        _ColorIntensity ("Color Intensity", Range(0, 2)) = 1.0
        _Glossiness ("Smoothness", Range(0,1)) = 0.5
        _Metallic ("Metallic", Range(0,1)) = 0.0
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 200

        CGPROGRAM
        #pragma surface surf Standard fullforwardshadows vertex:vert
        #pragma target 3.0

        sampler2D _MainTex;
        half _Glossiness;
        half _Metallic;
        fixed _ColorIntensity;

        struct Input
        {
            float2 uv_MainTex;
            float4 color : COLOR;
        };

        void vert(inout appdata_full v)
        {
            // Pass vertex colors to fragment shader
        }

        void surf (Input IN, inout SurfaceOutputStandard o)
        {
            // Sample the texture
            fixed4 texColor = tex2D(_MainTex, IN.uv_MainTex);
            
            // Combine texture with vertex colors
            fixed4 finalColor = texColor * IN.color * _ColorIntensity;
            
            o.Albedo = finalColor.rgb;
            o.Metallic = _Metallic;
            o.Smoothness = _Glossiness;
            o.Alpha = finalColor.a;
        }
        ENDCG
    }
    FallBack "Diffuse"
} 