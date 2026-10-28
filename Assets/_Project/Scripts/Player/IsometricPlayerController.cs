using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

/// <summary>
/// Camera-relative movement for the isometric prototype.
/// CharacterController owns collision; visual animation is driven by PlayerLocomotionAnimator.
/// </summary>
[RequireComponent(typeof(CharacterController))]
public sealed class IsometricPlayerController : MonoBehaviour
{
    [Header("Movement speeds")]
    [SerializeField, Min(0.1f)] private float walkSpeed = 3f;
    [SerializeField, Min(0.1f)] private float runSpeed = 5f;

    [Header("Movement response")]
    [SerializeField, Min(0.1f)] private float acceleration = 18f;
    [SerializeField, Min(0.1f)] private float deceleration = 24f;
    [SerializeField, Min(1f)] private float turnSpeedDegrees = 720f;
    [SerializeField] private float gravity = -25f;

    [Header("References")]
    [SerializeField] private Transform movementCamera;
    [SerializeField] private PlayerLocomotionAnimator locomotionAnimator;

    private CharacterController characterController;
    private float verticalVelocity;
    private Vector3 horizontalVelocity;
    private Vector2 latestInput;
    private CombatHealth combatHealth;
    private Vector3 dodgeDirection;
    private float dodgeDistancePerSecond;
    private float dodgeTimeRemaining;
    private bool latestRunInput;

    public Transform MovementCamera
    {
        get => movementCamera;
        set => movementCamera = value;
    }

    public Vector2 CurrentInput => latestInput;
    public Vector3 HorizontalVelocity => horizontalVelocity;
    public float CurrentHorizontalSpeed => new Vector3(horizontalVelocity.x, 0f, horizontalVelocity.z).magnitude;
    public bool IsGrounded => characterController != null && characterController.isGrounded;
    public bool IsRunning => latestRunInput && CurrentHorizontalSpeed > walkSpeed * 0.9f;
    public bool IsDodging => dodgeTimeRemaining > 0f;

    /// <summary>Requests a dodge; Update applies it through the same CharacterController.Move as gravity.</summary>
    public bool BeginDodge(Vector3 direction, float distance, float duration)
    {
        if (IsDodging || distance <= 0f || duration <= 0f || direction.sqrMagnitude < 0.001f)
            return false;

        dodgeDirection = direction.normalized;
        dodgeDistancePerSecond = distance / duration;
        dodgeTimeRemaining = duration;
        horizontalVelocity = Vector3.zero;
        return true;
    }

    private void Awake()
    {
        characterController = GetComponent<CharacterController>();
        combatHealth = GetComponent<CombatHealth>();

        if (movementCamera == null && Camera.main != null)
            movementCamera = Camera.main.transform;

        if (locomotionAnimator == null)
            locomotionAnimator = GetComponent<PlayerLocomotionAnimator>();
    }

    private void Update()
    {
        float dt = Time.deltaTime;
        if (combatHealth != null && combatHealth.IsDefeated)
        {
            latestInput = Vector2.zero;
            latestRunInput = false;
            horizontalVelocity = Vector3.zero;
            dodgeTimeRemaining = 0f;
            if (characterController.isGrounded && verticalVelocity < 0f)
                verticalVelocity = -2f;
            verticalVelocity += gravity * dt;
            characterController.Move(Vector3.up * (verticalVelocity * dt));
            if (locomotionAnimator != null)
                locomotionAnimator.SetMovementState(false, false);
            return;
        }

        Vector2 input = ReadMovementInput();
        latestInput = input;
        bool hasInput = input.sqrMagnitude > 0.001f;
        latestRunInput = hasInput && ReadRunInput();

        Vector3 moveDirection = BuildCameraRelativeDirection(input);
        if (hasInput && moveDirection.sqrMagnitude > 0.001f)
        {
            Quaternion targetRotation = Quaternion.LookRotation(moveDirection, Vector3.up);
            transform.rotation = Quaternion.RotateTowards(
                transform.rotation,
                targetRotation,
                turnSpeedDegrees * dt);
        }

        float targetSpeed = latestRunInput ? runSpeed : walkSpeed;
        Vector3 targetHorizontalVelocity = hasInput ? moveDirection * targetSpeed : Vector3.zero;
        float response = hasInput ? acceleration : deceleration;
        horizontalVelocity = Vector3.MoveTowards(
            horizontalVelocity,
            targetHorizontalVelocity,
            response * dt);

        if (characterController.isGrounded && verticalVelocity < 0f)
            verticalVelocity = -2f;
        verticalVelocity += gravity * dt;

        bool wasDodging = dodgeTimeRemaining > 0f;
        Vector3 displacement;
        if (wasDodging)
        {
            float activeDodgeDelta = Mathf.Min(dt, dodgeTimeRemaining);
            displacement = dodgeDirection * dodgeDistancePerSecond * activeDodgeDelta;
            dodgeTimeRemaining = Mathf.Max(0f, dodgeTimeRemaining - dt);
        }
        else
        {
            displacement = horizontalVelocity * dt;
        }
        displacement.y = verticalVelocity * dt;

        CollisionFlags collisionFlags = characterController.Move(displacement);

        // Cancel a dodge that hits a wall; all movement still goes through one Move call per frame.
        if ((collisionFlags & CollisionFlags.Sides) != 0)
        {
            Vector3 actualHorizontal = characterController.velocity;
            actualHorizontal.y = 0f;
            if (actualHorizontal.sqrMagnitude < 0.0001f || wasDodging)
            {
                horizontalVelocity = Vector3.zero;
                if (wasDodging)
                    dodgeTimeRemaining = 0f;
            }
        }

        if (locomotionAnimator != null)
        {
            bool visualIsMoving = !wasDodging && CurrentHorizontalSpeed > 0.12f;
            locomotionAnimator.SetMovementState(visualIsMoving, !wasDodging && IsRunning);
        }
    }

    private Vector3 BuildCameraRelativeDirection(Vector2 input)
    {
        if (input.sqrMagnitude > 1f)
            input.Normalize();

        Transform cameraTransform = movementCamera;
        if (cameraTransform == null && Camera.main != null)
            cameraTransform = Camera.main.transform;

        if (cameraTransform == null)
            return new Vector3(input.x, 0f, input.y);

        Vector3 forward = cameraTransform.forward;
        Vector3 right = cameraTransform.right;
        forward.y = 0f;
        right.y = 0f;
        forward.Normalize();
        right.Normalize();

        Vector3 direction = forward * input.y + right * input.x;
        return direction.sqrMagnitude > 1f ? direction.normalized : direction;
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
        return Vector2.ClampMagnitude(
            new Vector2(Input.GetAxisRaw("Horizontal"), Input.GetAxisRaw("Vertical")), 1f);
#endif
    }

    private static bool ReadRunInput()
    {
#if ENABLE_INPUT_SYSTEM
        return Keyboard.current != null &&
               (Keyboard.current.leftShiftKey.isPressed || Keyboard.current.rightShiftKey.isPressed);
#else
        return Input.GetKey(KeyCode.LeftShift) || Input.GetKey(KeyCode.RightShift);
#endif
    }
}
