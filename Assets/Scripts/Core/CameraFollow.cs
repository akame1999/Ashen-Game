using UnityEngine;

namespace Ashen.Core
{
    public class CameraFollow : MonoBehaviour
    {
        public Transform target;
        public Vector2 offset = new Vector2(0f, 1.5f);
        public float smoothing = 6f;

        void LateUpdate()
        {
            if (target == null) return;
            var goal = new Vector3(target.position.x + offset.x, target.position.y + offset.y, transform.position.z);
            transform.position = Vector3.Lerp(transform.position, goal, 1f - Mathf.Exp(-smoothing * Time.deltaTime));
        }
    }
}
