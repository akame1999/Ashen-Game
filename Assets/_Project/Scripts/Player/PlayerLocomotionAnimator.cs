using UnityEngine;

/// <summary>
/// Bridges player movement to the Animator's MoveSpeed blend-tree parameter.
/// The authored placeholder tree uses 0 = idle, 0.5 = walk, and 1 = run.
/// </summary>
[DisallowMultipleComponent]
public sealed class PlayerLocomotionAnimator : MonoBehaviour
{
    [SerializeField] private Animator characterAnimator;
    [SerializeField, Min(0f)] private float dampingTime = 0.12f;

    private static readonly int MoveSpeedHash = Animator.StringToHash("MoveSpeed");
    private bool hasMoveSpeedParameter;

    public Animator CharacterAnimator
    {
        get => characterAnimator;
        set
        {
            characterAnimator = value;
            CacheAnimatorParameter();
        }
    }

    private void Awake()
    {
        if (characterAnimator == null)
            characterAnimator = GetComponentInChildren<Animator>();

        CacheAnimatorParameter();
    }

    public void SetMovementState(bool isMoving, bool isRunning)
    {
        if (characterAnimator == null || !hasMoveSpeedParameter)
            return;

        float targetSpeed = !isMoving ? 0f : (isRunning ? 1f : 0.5f);
        characterAnimator.SetFloat(MoveSpeedHash, targetSpeed, dampingTime, Time.deltaTime);
    }

    private void CacheAnimatorParameter()
    {
        hasMoveSpeedParameter = false;

        if (characterAnimator == null || characterAnimator.runtimeAnimatorController == null)
            return;

        foreach (AnimatorControllerParameter parameter in characterAnimator.parameters)
        {
            if (parameter.nameHash == MoveSpeedHash &&
                parameter.type == AnimatorControllerParameterType.Float)
            {
                hasMoveSpeedParameter = true;
                break;
            }
        }
    }
}
