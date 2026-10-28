using System.Collections.Generic;
using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

/// <summary>
/// Simple forward melee attack and short dodge for the first combat test.
/// Attack input: J or left mouse. Dodge input: Space.
/// </summary>
[RequireComponent(typeof(CharacterController))]
[RequireComponent(typeof(CombatHealth))]
public sealed class PlayerMeleeCombat : MonoBehaviour
{
    [Header("Melee")]
    [SerializeField, Min(0f)] private float attackDamage = 25f;
    [SerializeField, Min(0.1f)] private float attackCooldown = 0.55f;
    [SerializeField, Min(0.5f)] private float attackRange = 2.25f;
    [SerializeField, Range(20f, 180f)] private float attackArcDegrees = 115f;
    [SerializeField, Min(0.1f)] private float attackRadius = 1.25f;

    [Header("Dodge")]
    [SerializeField, Min(0.5f)] private float dodgeDistance = 2.2f;
    [SerializeField, Min(0.05f)] private float dodgeDuration = 0.18f;
    [SerializeField, Min(0f)] private float dodgeCooldown = 0.75f;
    [SerializeField, Min(0f)] private float dodgeInvulnerability = 0.28f;

    private CharacterController characterController;
    private CombatHealth health;
    private float attackCooldownRemaining;
    private float dodgeCooldownRemaining;
    private float dodgeRemaining;
    private Vector3 dodgeDirection;
    private PlayerLocomotionAnimator locomotionAnimator;
    private TrailRenderer dodgeTrail;
    private Material dodgeTrailMaterial;

    private void Awake()
    {
        characterController = GetComponent<CharacterController>();
        health = GetComponent<CombatHealth>();
        locomotionAnimator = GetComponent<PlayerLocomotionAnimator>();
        SetupDodgeTrail();
    }

    private void Update()
    {
        attackCooldownRemaining = Mathf.Max(0f, attackCooldownRemaining - Time.deltaTime);
        dodgeCooldownRemaining = Mathf.Max(0f, dodgeCooldownRemaining - Time.deltaTime);

        if (dodgeRemaining > 0f)
        {
            float delta = Mathf.Min(Time.deltaTime, dodgeRemaining);
            characterController.Move(dodgeDirection * (dodgeDistance / Mathf.Max(0.05f, dodgeDuration)) * delta);
            dodgeRemaining -= delta;
            if (dodgeRemaining <= 0f && dodgeTrail != null)
                dodgeTrail.emitting = false;
        }

        if (ReadDodgePressed())
            TryDodge();

        if (ReadAttackPressed())
            TryAttack();
    }

    private void TryAttack()
    {
        if (attackCooldownRemaining > 0f || dodgeRemaining > 0f || health.IsDefeated)
            return;

        attackCooldownRemaining = attackCooldown;
        if (locomotionAnimator != null)
            locomotionAnimator.TriggerAttack();
        ShowSlashArc();

        Vector3 origin = transform.position + Vector3.up * 0.85f + transform.forward * 0.7f;
        Collider[] hits = Physics.OverlapSphere(origin, attackRadius, ~0, QueryTriggerInteraction.Ignore);
        HashSet<CombatHealth> damaged = new HashSet<CombatHealth>();

        foreach (Collider hit in hits)
        {
            TrainingEnemyAI enemy = hit.GetComponentInParent<TrainingEnemyAI>();
            if (enemy == null || enemy.Health == null || enemy.Health.IsDefeated)
                continue;

            Vector3 toTarget = enemy.transform.position - transform.position;
            toTarget.y = 0f;
            if (toTarget.sqrMagnitude > attackRange * attackRange)
                continue;

            if (toTarget.sqrMagnitude > 0.001f &&
                Vector3.Angle(transform.forward, toTarget.normalized) > attackArcDegrees * 0.5f)
                continue;

            if (damaged.Add(enemy.Health))
                enemy.Health.TakeDamage(attackDamage);
        }
    }

    private void TryDodge()
    {
        if (dodgeCooldownRemaining > 0f || dodgeRemaining > 0f || health.IsDefeated)
            return;

        Vector3 direction = transform.forward;
        Vector2 movement = ReadMovementInput();
        if (movement.sqrMagnitude > 0.05f)
        {
            Transform cam = Camera.main != null ? Camera.main.transform : null;
            if (cam != null)
            {
                Vector3 forward = cam.forward;
                Vector3 right = cam.right;
                forward.y = 0f;
                right.y = 0f;
                forward.Normalize();
                right.Normalize();
                direction = (forward * movement.y + right * movement.x).normalized;
            }
        }

        if (direction.sqrMagnitude < 0.001f)
            direction = transform.forward;

        dodgeDirection = direction.normalized;
        dodgeRemaining = dodgeDuration;
        dodgeCooldownRemaining = dodgeCooldown;
        health.GrantInvulnerability(dodgeInvulnerability);

        if (dodgeTrail != null)
        {
            dodgeTrail.Clear();
            dodgeTrail.emitting = true;
        }
    }

    private void SetupDodgeTrail()
    {
        Transform visualRoot = transform.Find("PlayerVisualRoot");
        if (visualRoot == null && transform.childCount > 0)
            visualRoot = transform.GetChild(0);

        if (visualRoot == null)
            return;

        dodgeTrail = visualRoot.GetComponent<TrailRenderer>();
        if (dodgeTrail == null)
            dodgeTrail = visualRoot.gameObject.AddComponent<TrailRenderer>();

        dodgeTrail.time = 0.22f;
        dodgeTrail.minVertexDistance = 0.08f;
        dodgeTrail.startWidth = 0.32f;
        dodgeTrail.endWidth = 0f;
        dodgeTrail.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        dodgeTrail.receiveShadows = false;
        dodgeTrail.alignment = LineAlignment.View;
        dodgeTrail.textureMode = LineTextureMode.Stretch;
        dodgeTrail.autodestruct = false;

        AnimationCurve width = new AnimationCurve(
            new Keyframe(0f, 1f),
            new Keyframe(1f, 0f));
        dodgeTrail.widthCurve = width;

        Gradient gradient = new Gradient();
        gradient.SetKeys(
            new[]
            {
                new GradientColorKey(new Color(0.25f, 0.9f, 1f), 0f),
                new GradientColorKey(new Color(0.1f, 0.45f, 1f), 1f)
            },
            new[]
            {
                new GradientAlphaKey(0.8f, 0f),
                new GradientAlphaKey(0f, 1f)
            });
        dodgeTrail.colorGradient = gradient;

        Shader shader = Shader.Find("Universal Render Pipeline/Unlit");
        if (shader == null)
            shader = Shader.Find("Sprites/Default");

        if (shader != null)
        {
            if (dodgeTrailMaterial == null)
            {
                dodgeTrailMaterial = new Material(shader);
                dodgeTrailMaterial.name = "Runtime_DodgeTrail_Material";
                dodgeTrailMaterial.hideFlags = HideFlags.HideAndDontSave;
            }
            dodgeTrail.material = dodgeTrailMaterial;
        }

        dodgeTrail.emitting = false;
        dodgeTrail.enabled = true;
    }

    private void OnDestroy()
    {
        if (dodgeTrailMaterial != null)
        {
            if (Application.isPlaying)
                Destroy(dodgeTrailMaterial);
            else
                DestroyImmediate(dodgeTrailMaterial);
        }
    }

    private void ShowSlashArc()
    {
        GameObject arcObject = new GameObject("MeleeSlashFX");
        LineRenderer line = arcObject.AddComponent<LineRenderer>();
        line.useWorldSpace = true;
        line.positionCount = 17;
        line.startWidth = 0.07f;
        line.endWidth = 0.015f;
        line.numCapVertices = 2;
        line.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        line.receiveShadows = false;

        Shader shader = Shader.Find("Sprites/Default");
        if (shader != null)
        {
            Material material = new Material(shader);
            material.color = new Color(1f, 0.58f, 0.16f, 0.95f);
            line.material = material;
        }

        Vector3 center = transform.position + Vector3.up * 0.9f + transform.forward * 0.65f;
        float startAngle = -attackArcDegrees * 0.5f;
        for (int i = 0; i < line.positionCount; i++)
        {
            float angle = startAngle + attackArcDegrees * i / (line.positionCount - 1f);
            Vector3 direction = Quaternion.AngleAxis(angle, Vector3.up) * transform.forward;
            line.SetPosition(i, center + direction * (attackRange * 0.67f));
        }

        Destroy(arcObject, 0.14f);
    }

    private static bool ReadAttackPressed()
    {
#if ENABLE_INPUT_SYSTEM
        if (Keyboard.current == null && Mouse.current == null)
            return false;
        return (Keyboard.current != null && Keyboard.current.jKey.wasPressedThisFrame) ||
               (Mouse.current != null && Mouse.current.leftButton.wasPressedThisFrame);
#else
        return Input.GetKeyDown(KeyCode.J) || Input.GetMouseButtonDown(0);
#endif
    }

    private static bool ReadDodgePressed()
    {
#if ENABLE_INPUT_SYSTEM
        return Keyboard.current != null && Keyboard.current.spaceKey.wasPressedThisFrame;
#else
        return Input.GetKeyDown(KeyCode.Space);
#endif
    }

    private static Vector2 ReadMovementInput()
    {
#if ENABLE_INPUT_SYSTEM
        if (Keyboard.current == null)
            return Vector2.zero;

        float x = 0f;
        float y = 0f;
        if (Keyboard.current.aKey.isPressed || Keyboard.current.leftArrowKey.isPressed) x -= 1f;
        if (Keyboard.current.dKey.isPressed || Keyboard.current.rightArrowKey.isPressed) x += 1f;
        if (Keyboard.current.sKey.isPressed || Keyboard.current.downArrowKey.isPressed) y -= 1f;
        if (Keyboard.current.wKey.isPressed || Keyboard.current.upArrowKey.isPressed) y += 1f;
        return Vector2.ClampMagnitude(new Vector2(x, y), 1f);
#else
        return Vector2.ClampMagnitude(new Vector2(Input.GetAxisRaw("Horizontal"), Input.GetAxisRaw("Vertical")), 1f);
#endif
    }
}
