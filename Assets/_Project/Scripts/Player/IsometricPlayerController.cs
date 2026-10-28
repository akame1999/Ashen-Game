using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

/// <summary>
/// Camera-relative movement for the isometric prototype.
/// A separate PlayerLocomotionAnimator drives the character's Animator Blend Tree.
/// </summary>
[RequireComponent(typeof(CharacterController))]
public sealed class IsometricPlayerController : MonoBehaviour
{
    [Header("Movement")]
    [SerializeField, Min(0.1f)] private float walkSpeed = 3f;
    [SerializeField, Min(0.1f)] private float runSpeed = 5f;
    [SerializeField, Min(1f)] private float turnSpeedDegrees = 720f;
    [SerializeField] private float gravity = -25f;

    [Header("References")]
    [SerializeField] private Transform movementCamera;
    [SerializeField] private PlayerLocomotionAnimator locomotionAnimator;

    private CharacterController characterController;
    private float verticalVelocity;

    private void Awake()
    {
        characterController = GetComponent<CharacterController>();

        if (movementCamera == null && Camera.main != null)
            movementCamera = Camera.main.transform;

        if (locomotionAnimator == null)
            locomotionAnimator = GetComponent<PlayerLocomotionAnimator>();
    }

    private void Update()
    {
        Vector2 input = ReadMovementInput();
        Vector3 moveDirection = BuildCameraRelativeDirection(input);
        bool hasMovementInput = input.sqrMagnitude > 0.001f && moveDirection.sqrMagnitude > 0.001f;
        bool isRunning = hasMovementInput && ReadRunInput();
        float currentSpeed = isRunning ? runSpeed : walkSpeed;

        if (hasMovementInput)
        {
            Quaternion targetRotation = Quaternion.LookRotation(moveDirection, Vector3.up);
            transform.rotation = Quaternion.RotateTowards(
                transform.rotation,
                targetRotation,
                turnSpeedDegrees * Time.deltaTime);
        }

        if (characterController.isGrounded && verticalVelocity < 0f)
            verticalVelocity = -2f;

        verticalVelocity += gravity * Time.deltaTime;

        Vector3 velocity = moveDirection * currentSpeed;
        velocity.y = verticalVelocity;
        characterController.Move(velocity * Time.deltaTime);

        if (locomotionAnimator != null)
            locomotionAnimator.SetMovementState(hasMovementInput, isRunning);
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
