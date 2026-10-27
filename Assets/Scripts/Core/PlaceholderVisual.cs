using UnityEngine;

namespace Ashen.Core
{
    /// <summary>Gives a SpriteRenderer a flat-colour sprite at runtime (generated sprites can't be saved in scenes).</summary>
    [ExecuteAlways, RequireComponent(typeof(SpriteRenderer))]
    public class PlaceholderVisual : MonoBehaviour
    {
        public Color color = Color.white;

        void OnEnable()
        {
            var sr = GetComponent<SpriteRenderer>();
            if (sr.sprite == null) sr.sprite = Placeholder.Square(Color.white);
            sr.color = color;
        }
    }
}
