using UnityEngine;

/// <summary>
/// Smooth-follow camera for a readable, elevated isometric-style view.
/// </summary>
[DisallowMultipleComponent]
[RequireComponent(typeof(Camera))]
public sealed class IsometricCameraFollow : MonoBehaviour
{
    [SerializeField] private Transform target;
    [SerializeField] private Vector3 offset = new Vector3(0f, 12f, -12f);
    [SerializeField, Min(0f)] private float smoothTime = 0.12f;
    [SerializeField, Range(20f, 70f)] private float pitch = 45f;
    [SerializeField, Min(1f)] private float orthographicSize = 10f;

    private Vector3 positionVelocity;
    private Camera attachedCamera;

    public Transform Target
    {
        get => target;
        set => target = value;
    }

    private void Awake()
    {
        attachedCamera = GetComponent<Camera>();
        ConfigureCamera();
    }

    private void OnValidate()
    {
        if (attachedCamera == null)
            attachedCamera = GetComponent<Camera>();

        ConfigureCamera();
    }

    private void LateUpdate()
    {
        if (target == null)
            return;

        Vector3 desiredPosition = target.position + offset;
        transform.position = smoothTime <= 0f
            ? desiredPosition
            : Vector3.SmoothDamp(transform.position, desiredPosition, ref positionVelocity, smoothTime);

        transform.rotation = Quaternion.Euler(pitch, 0f, 0f);
    }

    private void ConfigureCamera()
    {
        if (attachedCamera == null)
            return;

        attachedCamera.orthographic = true;
        attachedCamera.orthographicSize = orthographicSize;
    }
}
