using UnityEngine;

/// <summary>
/// Small visible hit reaction for the prototype mannequin/enemy. It shakes and compresses
/// the visual child without moving the gameplay root or fighting the CharacterController.
/// </summary>
[DisallowMultipleComponent]
[RequireComponent(typeof(CombatHealth))]
public sealed class CombatHitFeedback : MonoBehaviour
{
    [SerializeField, Min(0.05f)] private float reactionDuration = 0.2f;
    [SerializeField, Range(0f, 35f)] private float yawShakeDegrees = 14f;
    [SerializeField, Range(0f, 25f)] private float rollShakeDegrees = 9f;
    [SerializeField, Range(0f, 0.3f)] private float squashAmount = 0.10f;

    private CombatHealth health;
    private Transform visualRoot;
    private Quaternion baseRotation;
    private Vector3 baseScale;
    private float timeRemaining;
    private float elapsed;
    private bool hasVisual;

    private void Awake()
    {
        health = GetComponent<CombatHealth>();

        visualRoot = transform.Find("VeyrWanderer");
        if (visualRoot == null)
            visualRoot = transform.Find("PlayerVisualRoot");
        if (visualRoot == null)
            visualRoot = transform.Find("EnemyVisual");

        if (visualRoot == null)
        {
            Animator childAnimator = GetComponentInChildren<Animator>();
            if (childAnimator != null && childAnimator.transform != transform)
                visualRoot = childAnimator.transform;
        }

        if (visualRoot == null)
        {
            foreach (Transform child in GetComponentsInChildren<Transform>(true))
            {
                if (child == transform)
                    continue;

                if (child.GetComponent<Renderer>() != null)
                {
                    visualRoot = child;
                    break;
                }
            }
        }

        if (visualRoot != null)
        {
            baseRotation = visualRoot.localRotation;
            baseScale = visualRoot.localScale;
            hasVisual = true;
        }

        if (health != null)
            health.DamageTaken += OnDamageTaken;
    }

    private void OnDamageTaken(float amount)
    {
        if (!hasVisual)
            return;

        timeRemaining = reactionDuration;
        elapsed = 0f;
    }

    private void LateUpdate()
    {
        if (!hasVisual)
            return;

        if (timeRemaining > 0f)
        {
            elapsed += Time.deltaTime;
            timeRemaining = Mathf.Max(0f, timeRemaining - Time.deltaTime);
            float fade = timeRemaining / Mathf.Max(0.05f, reactionDuration);
            float pulse = Mathf.Sin(elapsed * 48f) * fade;

            visualRoot.localRotation = baseRotation * Quaternion.Euler(
                pulse * 5f, pulse * yawShakeDegrees, pulse * rollShakeDegrees);

            float compress = 1f - Mathf.Sin((1f - fade) * Mathf.PI) * squashAmount;
            float stretch = 1f + (1f - compress) * 0.55f;
            visualRoot.localScale = new Vector3(
                baseScale.x * stretch,
                baseScale.y * compress,
                baseScale.z * stretch);

            if (timeRemaining <= 0f)
            {
                visualRoot.localRotation = baseRotation;
                visualRoot.localScale = baseScale;
            }
        }
    }

    private void OnDestroy()
    {
        if (health != null)
            health.DamageTaken -= OnDamageTaken;
    }
}
