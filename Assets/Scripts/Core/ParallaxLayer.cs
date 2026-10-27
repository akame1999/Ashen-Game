using UnityEngine;

namespace Ashen.Core
{
    /// <summary>
    /// Scrolling background layer. follow = fraction of camera movement the layer keeps up with
    /// (0.9 = far away / barely moves, 0.4 = close / scrolls fast). Layers tile endlessly in X.
    /// </summary>
    public class ParallaxLayer : MonoBehaviour
    {
        public string resourcePath;
        [Range(0f, 1f)] public float follow = 0.8f;
        [Range(0f, 1f)] public float verticalFollow = 0.6f;
        public float baseY = -4.5f;
        public float referenceCameraY = 2.3f;
        public int sortingOrder = -10;
        public bool pinToCamera;          // used by the sky: always centred on the camera

        Transform _cam;
        float _tileWidth;

        void Start()
        {
            var cam = Camera.main;
            if (cam == null) { enabled = false; return; }
            _cam = cam.transform;

            var sprite = Resources.Load<Sprite>(resourcePath);
            if (sprite == null) { Debug.LogWarning("ParallaxLayer: missing sprite Resources/" + resourcePath); enabled = false; return; }

            _tileWidth = sprite.bounds.size.x;
            int copies = pinToCamera ? 1 : 3;
            for (int i = 0; i < copies; i++)
            {
                var go = new GameObject(sprite.name + "_" + i);
                go.transform.SetParent(transform, false);
                go.transform.localPosition = new Vector3(pinToCamera ? 0f : (i - 1) * _tileWidth, 0f, 0f);
                var sr = go.AddComponent<SpriteRenderer>();
                sr.sprite = sprite;
                sr.sortingOrder = sortingOrder;
            }
            LateUpdate();
        }

        void LateUpdate()
        {
            if (_cam == null) return;
            var c = _cam.position;

            if (pinToCamera) { transform.position = new Vector3(c.x, c.y, 0f); return; }

            float x = c.x * follow;
            // snap to the nearest tile so the 3 copies always cover the screen
            x += Mathf.Round((c.x - x) / _tileWidth) * _tileWidth;
            float y = baseY + (c.y - referenceCameraY) * verticalFollow;
            transform.position = new Vector3(x, y, 0f);
        }
    }
}
