using UnityEngine;

/// <summary>
/// Visible procedural locomotion for the temporary primitive mannequin.
/// Arms and legs swing independently; walk and run use different cadence and range.
/// A future rigged character should use authored humanoid clips instead.
/// </summary>
[DisallowMultipleComponent]
public sealed class PlayerLocomotionAnimator : MonoBehaviour
{
    [Header("Rig references")]
    [SerializeField] private Transform visualRoot;
    [SerializeField] private Transform torso;
    [SerializeField] private Transform head;
    [SerializeField] private Transform leftArm;
    [SerializeField] private Transform rightArm;
    [SerializeField] private Transform leftLeg;
    [SerializeField] private Transform rightLeg;

    [Header("Gait")]
    [SerializeField, Min(0.1f)] private float walkCyclesPerSecond = 2.0f;
    [SerializeField, Min(0.1f)] private float runCyclesPerSecond = 3.1f;
    [SerializeField, Range(0f, 60f)] private float walkLegSwing = 46f;
    [SerializeField, Range(0f, 70f)] private float runLegSwing = 62f;
    [SerializeField, Range(0f, 20f)] private float walkLean = 8f;
    [SerializeField, Range(0f, 25f)] private float runLean = 15f;
    [SerializeField, Min(0f)] private float walkBounceHeight = 0.08f;
    [SerializeField, Min(0f)] private float runBounceHeight = 0.15f;
    [SerializeField, Min(0f)] private float stateBlendSpeed = 10f;

    private bool isMoving;
    private bool isRunning;
    private float movementBlend;
    private float gaitPhase;

    private Vector3 rootBasePosition;
    private Vector3 torsoBasePosition;
    private Vector3 headBasePosition;
    private Quaternion torsoBaseRotation;
    private Quaternion headBaseRotation;
    private Quaternion leftArmBaseRotation;
    private Quaternion rightArmBaseRotation;
    private Quaternion leftLegBaseRotation;
    private Quaternion rightLegBaseRotation;
    private bool basePoseCached;
    [Header("Animator Controller bridge")]
    [SerializeField] private Animator characterAnimator;
    [SerializeField, Min(0f)] private float animatorDamping = 0.10f;
    private bool hasMoveSpeedParameter;
    private bool hasAttackTriggerParameter;
    private static readonly int MoveSpeedHash = Animator.StringToHash("MoveSpeed");
    private static readonly int AttackHash = Animator.StringToHash("Attack");
    private float attackTimeRemaining;
    [SerializeField, Min(0.05f)] private float attackAnimationDuration = 0.24f;
    [SerializeField, Range(0f, 150f)] private float attackArmSwingDegrees = 112f;

    public void ConfigureRig(
        Transform root,
        Transform torsoPivot,
        Transform headPivot,
        Transform leftArmPivot,
        Transform rightArmPivot,
        Transform leftLegPivot,
        Transform rightLegPivot)
    {
        visualRoot = root;
        torso = torsoPivot;
        head = headPivot;
        leftArm = leftArmPivot;
        rightArm = rightArmPivot;
        leftLeg = leftLegPivot;
        rightLeg = rightLegPivot;
        CacheBasePose();
    }

    public Animator CharacterAnimator
    {
        get => characterAnimator;
        set
        {
            characterAnimator = value;
            CacheAnimatorParameters();
        }
    }

    public void SetMovementState(bool moving, bool running)
    {
        isMoving = moving;
        isRunning = moving && running;
        if (characterAnimator != null && hasMoveSpeedParameter)
        {
            float speedValue = !moving ? 0f : (running ? 1f : 0.5f);
            characterAnimator.SetFloat(MoveSpeedHash, speedValue, animatorDamping, Time.deltaTime);
        }
    }

    public void TriggerAttack()
    {
        attackTimeRemaining = attackAnimationDuration;
        if (characterAnimator != null && hasAttackTriggerParameter)
        {
            characterAnimator.ResetTrigger(AttackHash);
            characterAnimator.SetTrigger(AttackHash);
        }
    }

    private void CacheAnimatorParameters()
    {
        hasMoveSpeedParameter = false;
        hasAttackTriggerParameter = false;
        if (characterAnimator == null) return;

        foreach (AnimatorControllerParameter parameter in characterAnimator.parameters)
        {
            if (parameter.nameHash == MoveSpeedHash && parameter.type == AnimatorControllerParameterType.Float)
                hasMoveSpeedParameter = true;
            else if (parameter.nameHash == AttackHash && parameter.type == AnimatorControllerParameterType.Trigger)
                hasAttackTriggerParameter = true;
        }
    }

    private void Awake()
    {
        if (characterAnimator == null)
            characterAnimator = GetComponentInChildren<Animator>();
        CacheAnimatorParameters();
        CacheBasePose();
    }

    private void LateUpdate()
    {
        movementBlend = Mathf.MoveTowards(
            movementBlend,
            isMoving ? 1f : 0f,
            stateBlendSpeed * Time.deltaTime);

        float cadence = isRunning ? runCyclesPerSecond : walkCyclesPerSecond;
        if (isMoving)
            gaitPhase += Time.deltaTime * cadence * Mathf.PI * 2f;

        float swingDegrees = isRunning ? runLegSwing : walkLegSwing;
        float attackWeight = 0f;
        if (attackTimeRemaining > 0f)
        {
            attackTimeRemaining = Mathf.Max(0f, attackTimeRemaining - Time.deltaTime);
            float progress = 1f - attackTimeRemaining / Mathf.Max(0.05f, attackAnimationDuration);
            attackWeight = Mathf.Sin(progress * Mathf.PI);
        }
        float attackArmSwing = -attackArmSwingDegrees * attackWeight;
        float swingRadians = Mathf.Sin(gaitPhase) * swingDegrees * Mathf.Deg2Rad * movementBlend;
        float oppositeSwingRadians = -swingRadians;
        float leanDegrees = isRunning ? runLean : walkLean;

        float bounce = isMoving
            ? (isRunning ? 0.018f : 0.008f) +
              Mathf.Abs(Mathf.Sin(gaitPhase * 2f)) * (isRunning ? runBounceHeight : walkBounceHeight)
            : Mathf.Sin(Time.time * 1.8f) * 0.006f;

        if (visualRoot != null)
            visualRoot.localPosition = rootBasePosition + Vector3.up * bounce;

        if (torso != null)
        {
            float torsoLean = leanDegrees * movementBlend;
            float torsoSway = isMoving ? Mathf.Sin(gaitPhase) * 2.5f * movementBlend : Mathf.Sin(Time.time * 1.8f);
            torso.localPosition = torsoBasePosition;
            torso.localRotation = torsoBaseRotation * Quaternion.Euler(torsoLean, 0f, torsoSway);
        }

        if (head != null)
        {
            float counterLean = -(isRunning ? 3f : 1.5f) * movementBlend;
            float headSway = isMoving ? -Mathf.Sin(gaitPhase) * 2f * movementBlend : 0f;
            head.localPosition = headBasePosition;
            head.localRotation = headBaseRotation * Quaternion.Euler(counterLean, 0f, headSway);
        }

        // Rotate limb pivots, not the meshes, so the limbs swing from the shoulder/hip.
        if (leftLeg != null)
            leftLeg.localRotation = leftLegBaseRotation * Quaternion.Euler(swingRadians * Mathf.Rad2Deg, 0f, 0f);
        if (rightLeg != null)
            rightLeg.localRotation = rightLegBaseRotation * Quaternion.Euler(oppositeSwingRadians * Mathf.Rad2Deg, 0f, 0f);

        if (leftArm != null)
            leftArm.localRotation = leftArmBaseRotation * Quaternion.Euler(
                oppositeSwingRadians * Mathf.Rad2Deg * 0.68f + 16f * attackWeight, 0f, -4f * movementBlend);
        if (rightArm != null)
            rightArm.localRotation = rightArmBaseRotation * Quaternion.Euler(
                swingRadians * Mathf.Rad2Deg * 0.68f + attackArmSwing, 0f, 4f * movementBlend);
    }

    private void CacheBasePose()
    {
        if (basePoseCached)
            return;

        if (visualRoot != null) rootBasePosition = visualRoot.localPosition;
        if (torso != null)
        {
            torsoBasePosition = torso.localPosition;
            torsoBaseRotation = torso.localRotation;
        }
        if (head != null)
        {
            headBasePosition = head.localPosition;
            headBaseRotation = head.localRotation;
        }
        if (leftArm != null) leftArmBaseRotation = leftArm.localRotation;
        if (rightArm != null) rightArmBaseRotation = rightArm.localRotation;
        if (leftLeg != null) leftLegBaseRotation = leftLeg.localRotation;
        if (rightLeg != null) rightLegBaseRotation = rightLeg.localRotation;

        basePoseCached = visualRoot != null;
    }
}
