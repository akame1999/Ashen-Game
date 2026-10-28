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
    [SerializeField, Min(0.1f)] private float walkCyclesPerSecond = 1.7f;
    [SerializeField, Min(0.1f)] private float runCyclesPerSecond = 2.6f;
    [SerializeField, Range(0f, 60f)] private float walkLegSwing = 30f;
    [SerializeField, Range(0f, 70f)] private float runLegSwing = 43f;
    [SerializeField, Range(0f, 20f)] private float walkLean = 5f;
    [SerializeField, Range(0f, 25f)] private float runLean = 11f;
    [SerializeField, Min(0f)] private float walkBounceHeight = 0.055f;
    [SerializeField, Min(0f)] private float runBounceHeight = 0.11f;
    [SerializeField, Min(0f)] private float stateBlendSpeed = 8f;

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

    public void SetMovementState(bool moving, bool running)
    {
        isMoving = moving;
        isRunning = moving && running;
    }

    private void Awake()
    {
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
            leftArm.localRotation = leftArmBaseRotation * Quaternion.Euler(oppositeSwingRadians * Mathf.Rad2Deg * 0.68f, 0f, -4f * movementBlend);
        if (rightArm != null)
            rightArm.localRotation = rightArmBaseRotation * Quaternion.Euler(swingRadians * Mathf.Rad2Deg * 0.68f, 0f, 4f * movementBlend);
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
