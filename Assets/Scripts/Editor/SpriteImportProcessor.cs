#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;

namespace Ashen.EditorTools
{
    /// <summary>Imports PNGs under Resources/Sprites (characters, 128px frames at 72 px/unit, pivot at the feet) and Resources/Backgrounds (painted, 64 px/unit, bilinear) as sprites; Props are painted at 128 px/unit (bilinear); Environment ground/platform are painted 256px tiles at 128 px/unit with bilinear filtering.</summary>
    public class SpriteImportProcessor : AssetPostprocessor
    {
        public override uint GetVersion() => 3;   // bump to force Unity to reimport sprites after importer changes

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
                bool painted = n == "ground" || n == "platform";   // 256px painted tiles, 128 px/unit, smooth filtering
                if (painted) { s.spritePixelsPerUnit = 128; s.filterMode = FilterMode.Bilinear; }
                s.spriteAlignment = (int)(prop ? SpriteAlignment.BottomCenter : SpriteAlignment.Center);
                s.spriteMeshType = SpriteMeshType.FullRect;
                // 9-slice borders (L,B,R,T in px): keep the mossy lip on top, tile everything else
                if (n == "ground") ti.spriteBorder = new Vector4(0, 0, 0, 40);
                else if (n == "platform") ti.spriteBorder = new Vector4(0, 24, 0, 40);
                ti.wrapMode = TextureWrapMode.Repeat;
            }
            else
            {
                bool sky = System.IO.Path.GetFileName(assetPath).StartsWith("sky");
                s.spriteAlignment = (int)(sky ? SpriteAlignment.Center : SpriteAlignment.BottomCenter);
                s.spriteMeshType = SpriteMeshType.FullRect;
            }
            // NOTE: ppu and filter must be set on `s` (TextureImporterSettings), otherwise SetTextureSettings below overwrites them.
            if (props)      { s.spritePixelsPerUnit = 128; s.filterMode = FilterMode.Bilinear; }   // painted props: 4x resolution, same world size
            if (background) { s.spritePixelsPerUnit = 64;  s.filterMode = FilterMode.Bilinear; }   // painted layers: 2x resolution, same world size
            ti.SetTextureSettings(s);
        }
    }
}
#endif
