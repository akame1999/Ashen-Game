using UnityEngine;

/// <summary>
/// Minimal training enemy: approaches, pauses for a readable wind-up, strikes, then recovers.
/// This is a prototype AI, not the production enemy framework.
/// </summary>
[RequireComponent(typeof(CharacterController))]
[RequireComponent(typeof(CombatHealth))]
public sealed class TrainingEnemyAI : MonoBehaviour
{
    private enum EnemyState { Approach, Telegraph, Recover, Defeated }

    [Header("Target and movement")]
    [SerializeField] private Transform target;
    [SerializeField, Min(0.1f)] private float moveSpeed = 2.1f;
    [SerializeField, Min(1f)] private float noticeRange = 12f;
    [SerializeField, Min(0.5f)] private float attackRange = 1.75f;

    [Header("Attack timing")]
    [SerializeField, Min(0.1f)] private float telegraphDuration = 0.75f;
    [SerializeField, Min(0.1f)] private float recoveryDuration = 0.75f;
    [SerializeField, Min(0f)] private float damage = 12f;
    [SerializeField, Min(0f)] private float turnSpeed = 540f;

    private CharacterController characterController;
    private CombatHealth health;
    private EnemyState state = EnemyState.Approach;
    private float stateTimer;
    private float verticalVelocity;
    private Renderer[] renderers;
    private Color[] originalColors;
    private bool telegraphColorSet;

    public CombatHealth Health => health;

    public void SetTarget(Transform value) => target = value;

    private void Awake()
    {
        characterController = GetComponent<CharacterController>();
        health = GetComponent<CombatHealth>();
        renderers = GetComponentsInChildren<Renderer>();
        originalColors = new Color[renderers.Length];

        for (int i = 0; i < renderers.Length; i++)
        {
            Material material = renderers[i].sharedMaterial;
            originalColors[i] = material != null && material.HasProperty("_BaseColor")
                ? material.GetColor("_BaseColor")
                : (material != null && material.HasProperty("_Color")
                    ? material.GetColor("_Color") : Color.white);
        }

        if (target == null)
        {
            GameObject player = GameObject.FindGameObjectWithTag("Player");
            if (player != null) target = player.transform;
        }
    }

    private void Update()
    {
        if (health == null || health.IsDefeated)
        {
            state = EnemyState.Defeated;
            return;
        }

        if (target == null)
        {
            GameObject player = GameObject.FindGameObjectWithTag("Player");
            if (player != null) target = player.transform;
            if (target == null) return;
        }

        Vector3 delta = target.position - transform.position;
        delta.y = 0f;
        float distance = delta.magnitude;

        if (distance > noticeRange)
        {
            state = EnemyState.Approach;
            RestoreVisualColor();
            ApplyGravityOnly();
            return;
        }

        if (delta.sqrMagnitude > 0.001f)
        {
            Quaternion look = Quaternion.LookRotation(delta.normalized, Vector3.up);
            transform.rotation = Quaternion.RotateTowards(transform.rotation, look, turnSpeed * Time.deltaTime);
        }

        switch (state)
        {
            case EnemyState.Approach:
                RestoreVisualColor();
                if (distance > attackRange)
                {
                    Vector3 velocity = delta.sqrMagnitude > 0.001f ? delta.normalized * moveSpeed : Vector3.zero;
                    ApplyControllerMove(velocity);
                }
                else
                {
                    state = EnemyState.Telegraph;
                    stateTimer = telegraphDuration;
                    SetTelegraphColor();
                    ApplyGravityOnly();
                }
                break;

            case EnemyState.Telegraph:
                stateTimer -= Time.deltaTime;
                SetTelegraphColor();
                ApplyGravityOnly();
                if (stateTimer <= 0f)
                {
                    CombatHealth playerHealth = target.GetComponent<CombatHealth>();
                    Vector3 currentDelta = target.position - transform.position;
                    currentDelta.y = 0f;
                    if (playerHealth != null && currentDelta.magnitude <= attackRange + 0.35f)
                        playerHealth.TakeDamage(damage);

                    state = EnemyState.Recover;
                    stateTimer = recoveryDuration;
                    RestoreVisualColor();
                }
                break;

            case EnemyState.Recover:
                ApplyGravityOnly();
                stateTimer -= Time.deltaTime;
                if (stateTimer <= 0f)
                    state = EnemyState.Approach;
                break;
        }
    }

    private void ApplyControllerMove(Vector3 horizontalVelocity)
    {
        if (characterController.isGrounded && verticalVelocity < 0f)
            verticalVelocity = -2f;

        verticalVelocity += Physics.gravity.y * Time.deltaTime;
        horizontalVelocity.y = verticalVelocity;
        characterController.Move(horizontalVelocity * Time.deltaTime);
    }

    private void ApplyGravityOnly() => ApplyControllerMove(Vector3.zero);

    private void SetTelegraphColor()
    {
        if (telegraphColorSet) return;
        SetColor(new Color(1f, 0.24f, 0.06f));
        telegraphColorSet = true;
    }

    private void RestoreVisualColor()
    {
        if (!telegraphColorSet) return;
        for (int i = 0; i < renderers.Length; i++)
        {
            if (renderers[i] == null) continue;
            MaterialPropertyBlock block = new MaterialPropertyBlock();
            renderers[i].GetPropertyBlock(block);
            block.SetColor("_BaseColor", originalColors[i]);
            block.SetColor("_Color", originalColors[i]);
            renderers[i].SetPropertyBlock(block);
        }
        telegraphColorSet = false;
    }

    private void SetColor(Color color)
    {
        foreach (Renderer renderer in renderers)
        {
            if (renderer == null) continue;
            MaterialPropertyBlock block = new MaterialPropertyBlock();
            renderer.GetPropertyBlock(block);
            block.SetColor("_BaseColor", color);
            block.SetColor("_Color", color);
            renderer.SetPropertyBlock(block);
        }
    }
}
