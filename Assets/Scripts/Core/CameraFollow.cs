using UnityEngine;

namespace Ashen.Core
{
    public class CameraFollow : MonoBehaviour
    {
        public Transform target;
        public Vector2 offset = new Vector2(0f, 1.5f);
        public float smoothing = 6f;
        public bool clampToLevel = true;
        public float levelMinX = -19f, levelMaxX = 19f;   // inner faces of the boundary walls

        Vector3 _basePos;
        static float _shakeMag, _shakeUntil, _shakeDur;

        /// <summary>Trigger a short camera shake (world units, seconds). Stronger shakes override weaker ones.</summary>
        public static void Shake(float magnitude, float duration)
        {
            if (magnitude < RemainingShake()) return;
            _shakeMag = magnitude; _shakeDur = Mathf.Max(0.01f, duration); _shakeUntil = Time.time + duration;
        }

        static float RemainingShake()
        {
            float left = _shakeUntil - Time.time;
            return left <= 0f ? 0f : _shakeMag * (left / _shakeDur);
        }

        void LateUpdate()
        {
            if (target == null) return;
            var goal = new Vector3(target.position.x + offset.x, target.position.y + offset.y, transform.position.z);
            if (clampToLevel)
            {
                var cam = GetComponent<Camera>();
                float half = cam != null ? cam.orthographicSize * cam.aspect : 0f;
                float lo = levelMinX + half, hi = levelMaxX - half;
                goal.x = lo < hi ? Mathf.Clamp(goal.x, lo, hi) : (levelMinX + levelMaxX) * 0.5f;
            }
            // Smooth toward goal, then add shake on top without feeding it back into the follow.
            _basePos = Vector3.Lerp(_basePos == Vector3.zero ? transform.position : _basePos, goal, 1f - Mathf.Exp(-smoothing * Time.deltaTime));
            var shake = Random.insideUnitCircle * RemainingShake();
            transform.position = _basePos + new Vector3(shake.x, shake.y, 0f);
        }
    }
}
