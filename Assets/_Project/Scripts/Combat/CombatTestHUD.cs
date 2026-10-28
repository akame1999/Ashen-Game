using UnityEngine;

/// <summary>
/// Temporary screen-space HUD for the combat prototype.
/// Replace with a proper Canvas UI in a later milestone.
/// </summary>
public sealed class CombatTestHUD : MonoBehaviour
{
    private CombatHealth playerHealth;
    private CombatHealth enemyHealth;
    private GUIStyle labelStyle;
    private GUIStyle titleStyle;
    private GUIStyle boxStyle;

    private void Awake()
    {
        playerHealth = GetComponent<CombatHealth>();
        FindEnemyHealth();
    }

    private void Update()
    {
        if (enemyHealth == null || enemyHealth.IsDefeated)
            FindEnemyHealth();
    }

    private void OnGUI()
    {
        if (playerHealth == null)
            playerHealth = GetComponent<CombatHealth>();
        if (playerHealth == null)
            return;

        EnsureStyles();

        float width = Mathf.Min(370f, Screen.width - 32f);
        Rect box = new Rect(16f, 16f, width, enemyHealth != null ? 164f : 112f);
        GUI.Box(box, GUIContent.none, boxStyle);
        GUI.Label(new Rect(30f, 26f, width - 24f, 24f), "COMBAT TEST", titleStyle);
        DrawHealthBar(new Rect(30f, 57f, width - 28f, 18f),
            "PLAYER", playerHealth.CurrentHealth, playerHealth.MaxHealth, new Color(0.2f, 0.78f, 0.42f));

        if (enemyHealth != null)
        {
            string enemyLabel = enemyHealth.IsDefeated ? "ENEMY — DEFEATED" : "ENEMY";
            DrawHealthBar(new Rect(30f, 82f, width - 28f, 18f),
                enemyLabel, enemyHealth.CurrentHealth, enemyHealth.MaxHealth, new Color(0.88f, 0.25f, 0.16f));
        }

        GUI.Label(new Rect(30f, 109f, width - 28f, 19f),
            "WASD move   Shift run   J/Left Click attack", labelStyle);
        GUI.Label(new Rect(30f, 130f, width - 28f, 19f),
            "Space dodge   Avoid the enemy's orange wind-up", labelStyle);
    }

    private void DrawHealthBar(Rect rect, string label, float current, float maximum, Color fill)
    {
        GUI.color = new Color(0.05f, 0.06f, 0.07f, 0.95f);
        GUI.Box(rect, GUIContent.none);
        GUI.color = fill;
        float fraction = maximum > 0f ? Mathf.Clamp01(current / maximum) : 0f;
        GUI.DrawTexture(new Rect(rect.x + 2f, rect.y + 2f,
            Mathf.Max(0f, (rect.width - 4f) * fraction), rect.height - 4f), Texture2D.whiteTexture);
        GUI.color = Color.white;
        GUI.Label(new Rect(rect.x + 5f, rect.y - 1f, rect.width - 8f, rect.height + 3f),
            label + "  " + Mathf.CeilToInt(current) + "/" + Mathf.CeilToInt(maximum), labelStyle);
    }

    private void EnsureStyles()
    {
        if (labelStyle != null) return;

        labelStyle = new GUIStyle(GUI.skin.label)
        {
            fontSize = 12,
            fontStyle = FontStyle.Bold,
            normal = { textColor = Color.white }
        };
        titleStyle = new GUIStyle(labelStyle) { fontSize = 15 };
        boxStyle = new GUIStyle(GUI.skin.box)
        {
            normal = { background = MakePixel(new Color(0.025f, 0.035f, 0.045f, 0.92f)) }
        };
    }

    private void FindEnemyHealth()
    {
        TrainingEnemyAI enemy = FindFirstObjectByType<TrainingEnemyAI>();
        enemyHealth = enemy != null ? enemy.Health : null;
    }

    private static Texture2D MakePixel(Color color)
    {
        Texture2D pixel = new Texture2D(1, 1);
        pixel.hideFlags = HideFlags.HideAndDontSave;
        pixel.SetPixel(0, 0, color);
        pixel.Apply();
        return pixel;
    }

    private void OnDestroy()
    {
        if (boxStyle != null && boxStyle.normal.background != null)
            Destroy(boxStyle.normal.background);
    }
}
