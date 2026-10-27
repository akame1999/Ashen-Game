using UnityEngine;

namespace Ashen.Core
{
    /// <summary>Generates flat-colour placeholder sprites so the game runs before real art exists.</summary>
    public static class Placeholder
    {
        public static Sprite Square(Color color)
        {
            var tex = new Texture2D(1, 1, TextureFormat.RGBA32, false) { filterMode = FilterMode.Point };
            tex.SetPixel(0, 0, color);
            tex.Apply();
            return Sprite.Create(tex, new Rect(0, 0, 1, 1), new Vector2(0.5f, 0.5f), 1f);
        }
    }
}
