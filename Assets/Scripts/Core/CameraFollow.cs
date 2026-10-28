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
            transform.position = Vector3.Lerp(transform.position, goal, 1f - Mathf.Exp(-smoothing * Time.deltaTime));
        }
    }
}
