#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;

namespace Ashen.EditorTools
{
    /// <summary>Imports PNGs under Resources/Sprites (characters, 36 px/unit, pivot at the feet) and Resources/Backgrounds (32 px/unit) as crisp pixel-art sprites.</summary>
    public class SpriteImportProcessor : AssetPostprocessor
    {
        void OnPreprocessTexture()
        {
            bool character = assetPath.StartsWith("Assets/Resources/Sprites/");
            bool background = assetPath.StartsWith("Assets/Resources/Backgrounds/");
            if (!character && !background) return;
            var ti = (TextureImporter)assetImporter;
            ti.textureType = TextureImporterType.Sprite;
            ti.spriteImportMode = SpriteImportMode.Single;
            ti.spritePixelsPerUnit = character ? 36 : 32;
            ti.filterMode = FilterMode.Point;
            ti.mipmapEnabled = false;
            ti.alphaIsTransparency = true;
            ti.textureCompression = TextureImporterCompression.Uncompressed;

            var s = new TextureImporterSettings();
            ti.ReadTextureSettings(s);
            if (character)
            {
                s.spriteAlignment = (int)SpriteAlignment.Custom;
                s.spritePivot = new Vector2(0.375f, 0f); // character centre is x=24 of 64, feet on the bottom row
            }
            else
            {
                bool sky = System.IO.Path.GetFileName(assetPath).StartsWith("sky");
                s.spriteAlignment = (int)(sky ? SpriteAlignment.Center : SpriteAlignment.BottomCenter);
                s.spriteMeshType = SpriteMeshType.FullRect;
            }
            ti.SetTextureSettings(s);
        }
    }
}
#endif
