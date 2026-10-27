using UnityEngine;

namespace Ashen.Core
{
    /// <summary>Animates a torch: cycles Props/flame_N frames and pulses a soft glow sprite (scale + alpha) with Perlin noise.</summary>
    public class TorchFlicker : MonoBehaviour
    {
        public SpriteRenderer flame;
        public SpriteRenderer glow;
        public Color glowColor = new Color(1f, 0.6f, 0.25f, 0.45f);
        public float glowScale = 6f;       // world units across at rest
        public float fps = 9f;

        Sprite[] _frames;
        float _seed;

        void Start()
        {
            _seed = Random.value * 100f;
            var list = new System.Collections.Generic.List<Sprite>();
            for (int i = 0; ; i++)
            {
                var s = Resources.Load<Sprite>("Props/flame_" + i);
                if (s == null) break;
                list.Add(s);
            }
            _frames = list.ToArray();
        }

        void Update()
        {
            if (_frames != null && _frames.Length > 0 && flame != null)
                flame.sprite = _frames[(int)(Time.time * fps + _seed) % _frames.Length];

            if (glow == null) return;
            float n = Mathf.PerlinNoise(Time.time * 6f, _seed);
            float size = glowScale * (0.92f + 0.16f * n);
            glow.transform.localScale = Vector3.one * (size / glow.sprite.bounds.size.x);
            var c = glowColor; c.a = glowColor.a * (0.75f + 0.5f * n);
            glow.color = c;
        }
    }
}
