using UnityEngine;
#if ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

/// <summary>
/// Phase 1 debug HUD. Toggle with F1 while in Play mode.
/// Displays movement/input, grounding and camera-follow diagnostics.
/// </summary>
[DisallowMultipleComponent]
public sealed class PrototypeDebugOverlay : MonoBehaviour
{
    [SerializeField] private bool visibleOnStart = true;

    private bool visible;
    private IsometricPlayerController movement;
    private CharacterController characterController;
    private PlayerLocomotionAnimator locomotion;
    private GUIStyle titleStyle;
    private GUIStyle textStyle;
    private Texture2D backgroundTexture;

    private void Awake()
    {
        visible = visibleOnStart;
        movement = GetComponent<IsometricPlayerController>();
        characterController = GetComponent<CharacterController>();
        locomotion = GetComponent<PlayerLocomotionAnimator>();
    }

    private void Update()
    {
        if (ReadTogglePressed())
            visible = !visible;
    }

    private void OnGUI()
    {
        if (!visible)
            return;

        EnsureStyles();

        float width = Mathf.Min(350f, Screen.width - 28f);
        const float panelHeight = 178f;
        Rect panel = new Rect(Mathf.Max(14f, Screen.width - width - 14f), 14f, width, panelHeight);
        GUI.color = Color.white;
        GUI.Box(panel, GUIContent.none, new GUIStyle(GUI.skin.box)
        {
            normal = { background = backgroundTexture }
        });

        float x = panel.x + 12f;
        float lineY = panel.y + 10f;
        float textWidth = width - 24f;
        GUI.Label(new Rect(x, lineY, textWidth, 23f), "PHASE 1 DEBUG  [F1 to hide]", titleStyle);
        lineY += 27f;

        if (movement == null)
            movement = GetComponent<IsometricPlayerController>();
        if (characterController == null)
            characterController = GetComponent<CharacterController>();

        Vector2 input = movement != null ? movement.CurrentInput : Vector2.zero;
        float speed = movement != null ? movement.CurrentHorizontalSpeed : 0f;
        bool grounded = movement != null && movement.IsGrounded;

        DrawLine(x, ref lineY, textWidth, $"Input: X {input.x,5:0.00}   Y {input.y,5:0.00}");
        DrawLine(x, ref lineY, textWidth, $"Speed: {speed:0.00} m/s   Mode: {(movement != null && movement.IsRunning ? "RUN" : speed > 0.12f ? "WALK" : "IDLE")}");
        DrawLine(x, ref lineY, textWidth, $"Grounded: {(grounded ? "YES" : "NO")}   Collision: {(characterController != null ? "CharacterController" : "MISSING")}");
        DrawLine(x, ref lineY, textWidth, $"Position: {transform.position.x:0.0}, {transform.position.y:0.0}, {transform.position.z:0.0}");

        Camera mainCamera = Camera.main;
        IsometricCameraFollow follow = mainCamera != null ? mainCamera.GetComponent<IsometricCameraFollow>() : null;
        DrawLine(x, ref lineY, textWidth,
            $"Camera: {(mainCamera == null ? "MISSING" : mainCamera.orthographic ? "ORTHOGRAPHIC" : "PERSPECTIVE")} / {(follow != null && follow.Target == transform ? "FOLLOWING" : "CHECK FOLLOW")}");

        if (locomotion == null)
            locomotion = GetComponent<PlayerLocomotionAnimator>();
        DrawLine(x, ref lineY, textWidth, $"Animator driver: {(locomotion != null ? "READY" : "NOT FOUND")}");
    }

    private void DrawLine(float x, ref float y, float width, string message)
    {
        GUI.Label(new Rect(x, y, width, 19f), message, textStyle);
        y += 21f;
    }

    private void EnsureStyles()
    {
        if (titleStyle != null)
            return;

        backgroundTexture = new Texture2D(1, 1);
        backgroundTexture.hideFlags = HideFlags.HideAndDontSave;
        backgroundTexture.SetPixel(0, 0, new Color(0.025f, 0.035f, 0.045f, 0.92f));
        backgroundTexture.Apply();

        titleStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 14,
            fontStyle = FontStyle.Bold,
            normal = { textColor = new Color(0.40f, 0.88f, 1f) }
        };
        textStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 11,
            normal = { textColor = Color.white }
        };
    }

    private static bool ReadTogglePressed()
    {
#if ENABLE_INPUT_SYSTEM
        return Keyboard.current != null && Keyboard.current.f1Key.wasPressedThisFrame;
#else
        return Input.GetKeyDown(KeyCode.F1);
#endif
    }

    private void OnDestroy()
    {
        if (backgroundTexture != null)
        {
            if (Application.isPlaying)
                Destroy(backgroundTexture);
            else
                DestroyImmediate(backgroundTexture);
        }
    }
}
