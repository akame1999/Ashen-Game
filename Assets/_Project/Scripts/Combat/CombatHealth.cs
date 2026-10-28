using UnityEngine;

/// <summary>
/// Small reusable health component for the first combat prototype.
/// </summary>
[DisallowMultipleComponent]
public sealed class CombatHealth : MonoBehaviour
{
    [SerializeField, Min(1f)] private float maxHealth = 100f;
    [SerializeField] private float currentHealth = 100f;

    private float invulnerabilityRemaining;
    private bool defeated;

    public float MaxHealth => maxHealth;
    public float CurrentHealth => currentHealth;
    public bool IsDefeated => defeated;
    public bool IsInvulnerable => invulnerabilityRemaining > 0f;

    private void Awake()
    {
        maxHealth = Mathf.Max(1f, maxHealth);
        currentHealth = Mathf.Clamp(currentHealth <= 0f ? maxHealth : currentHealth, 0f, maxHealth);
        defeated = currentHealth <= 0f;
    }

    private void Update()
    {
        if (invulnerabilityRemaining > 0f)
            invulnerabilityRemaining = Mathf.Max(0f, invulnerabilityRemaining - Time.deltaTime);
    }

    public bool TakeDamage(float amount)
    {
        if (defeated || IsInvulnerable || amount <= 0f)
            return false;

        currentHealth = Mathf.Max(0f, currentHealth - amount);
        if (currentHealth <= 0f)
        {
            defeated = true;
            TrainingEnemyAI enemyAI = GetComponent<TrainingEnemyAI>();
            if (enemyAI != null)
                enemyAI.enabled = false;
        }

        return true;
    }

    public void GrantInvulnerability(float seconds)
    {
        invulnerabilityRemaining = Mathf.Max(invulnerabilityRemaining, Mathf.Max(0f, seconds));
    }

    public void ResetHealth()
    {
        currentHealth = maxHealth;
        defeated = false;
        invulnerabilityRemaining = 0f;
    }
}
