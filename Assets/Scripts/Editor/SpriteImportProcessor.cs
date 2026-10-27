#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;

namespace Ashen.EditorTools
{
    /// <summary>Imports every PNG under Resources/Sprites as a crisp pixel-art sprite (36 px/unit, pivot at the feet).</summary>
    public class SpriteImportProcessor : AssetPostprocessor
    {
        void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith("Assets/Resources/Sprites/")) return;
            var ti = (TextureImporter)assetImporter;
            ti.textureType = TextureImporterType.Sprite;
            ti.spriteImportMode = SpriteImportMode.Single;
            ti.spritePixelsPerUnit = 36;
            ti.filterMode = FilterMode.Point;
            ti.mipmapEnabled = false;
            ti.alphaIsTransparency = true;
            ti.textureCompression = TextureImporterCompression.Uncompressed;

            var s = new TextureImporterSettings();
            ti.ReadTextureSettings(s);
            s.spriteAlignment = (int)SpriteAlignment.Custom;
            s.spritePivot = new Vector2(0.375f, 0f); // character centre is x=24 of 64, feet on the bottom row
            ti.SetTextureSettings(s);
        }
    }
}
#endif
