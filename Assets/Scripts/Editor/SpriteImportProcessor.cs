#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;

namespace Ashen.EditorTools
{
    /// <summary>Imports PNGs under Resources/Sprites (characters, 128px frames at 72 px/unit, pivot at the feet) and Resources/Backgrounds (32 px/unit) as crisp pixel-art sprites.</summary>
    public class SpriteImportProcessor : AssetPostprocessor
    {
        void OnPreprocessTexture()
        {
            bool character = assetPath.StartsWith("Assets/Resources/Sprites/");
            bool background = assetPath.StartsWith("Assets/Resources/Backgrounds/");
            bool environment = assetPath.StartsWith("Assets/Resources/Environment/");
            bool props = assetPath.StartsWith("Assets/Resources/Props/");
            if (!character && !background && !environment && !props) return;
            var ti = (TextureImporter)assetImporter;
            ti.textureType = TextureImporterType.Sprite;
            ti.spriteImportMode = SpriteImportMode.Single;
            ti.spritePixelsPerUnit = character ? 72 : 32;   // environment tiles are 32 px/unit too
            ti.filterMode = FilterMode.Point;
            ti.mipmapEnabled = false;
            ti.alphaIsTransparency = true;
            ti.textureCompression = TextureImporterCompression.Uncompressed;

            var s = new TextureImporterSettings();
            ti.ReadTextureSettings(s);
            if (character)
            {
                s.spriteAlignment = (int)SpriteAlignment.Custom;
                s.spritePivot = new Vector2(0.375f, 0f); // character centre is x=48 of 128, feet on the bottom row
            }
            else if (props)
            {
                string n = System.IO.Path.GetFileNameWithoutExtension(assetPath);
                s.spriteAlignment = (int)(n == "glow" ? SpriteAlignment.Center : n == "chain" ? SpriteAlignment.TopCenter : SpriteAlignment.BottomCenter);
                s.spriteMeshType = SpriteMeshType.FullRect;
                if (n == "glow") ti.filterMode = FilterMode.Bilinear;   // soft gradient, no pixel banding
            }
            else if (environment)
            {
                string n = System.IO.Path.GetFileNameWithoutExtension(assetPath);
                bool prop = n == "checkpoint";
                s.spriteAlignment = (int)(prop ? SpriteAlignment.BottomCenter : SpriteAlignment.Center);
                s.spriteMeshType = SpriteMeshType.FullRect;
                // 9-slice borders (L,B,R,T in px): keep the mossy lip on top, tile everything else
                if (n == "ground") ti.spriteBorder = new Vector4(0, 0, 0, 10);
                else if (n == "platform") ti.spriteBorder = new Vector4(0, 6, 0, 10);
                ti.wrapMode = TextureWrapMode.Repeat;
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
