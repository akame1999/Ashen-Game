using Ashen.Enemies;
using Ashen.Player;
using UnityEngine;

namespace Ashen.UI
{
    /// <summary>Temporary IMGUI HUD: health + stamina bars and a respawn prompt.</summary>
    public class SimpleHUD : MonoBehaviour
    {
        public PlayerController2D player;
        public Transform respawnPoint;
        Texture2D _px;

        void Awake() { _px = Texture2D.whiteTexture; }

        void Update()
        {
            if (player != null && player.Health.IsDead && Input.GetKeyDown(KeyCode.R))
            {
                player.Health.Revive();
                if (respawnPoint != null) player.transform.position = respawnPoint.position;
            }
        }

        void OnGUI()
        {
            if (player == null) return;
            Bar(new Rect(20, 20, 260, 18), (float)player.Health.Current / player.Health.maxHealth, new Color(0.75f, 0.12f, 0.12f));
            Bar(new Rect(20, 44, 200, 12), player.Stamina / player.maxStamina, new Color(0.25f, 0.7f, 0.3f));

            DrawBoss();

            if (player.Health.IsDead)
            {
                var style = new GUIStyle(GUI.skin.label) { fontSize = 40, alignment = TextAnchor.MiddleCenter };
                GUI.Label(new Rect(0, Screen.height / 2f - 40, Screen.width, 80), "YOU DIED  -  press R", style);
            }
        }

        void DrawBoss()
        {
            var boss = BossEncounter.Active;
            if (boss != null && boss.BarVisible && !boss.Health.IsDead)
            {
                float w = Mathf.Min(Screen.width * 0.6f, 640f);
                var r = new Rect((Screen.width - w) / 2f, Screen.height - 60f, w, 16f);
                Bar(r, (float)boss.Health.Current / boss.Health.maxHealth,
                    boss.Enraged ? new Color(0.9f, 0.3f, 0.1f) : new Color(0.6f, 0.1f, 0.15f));
                var name = new GUIStyle(GUI.skin.label) { fontSize = 18, alignment = TextAnchor.MiddleCenter };
                GUI.Label(new Rect(r.x, r.y - 26f, r.width, 24f), boss.bossName, name);
            }

            if (BossEncounter.Defeated)
            {
                var style = new GUIStyle(GUI.skin.label) { fontSize = 48, alignment = TextAnchor.MiddleCenter };
                GUI.Label(new Rect(0, Screen.height * 0.3f, Screen.width, 80), "FOE FELLED", style);
            }
        }

        void Bar(Rect r, float t, Color c)
        {
            GUI.color = new Color(0, 0, 0, 0.6f); GUI.DrawTexture(r, _px);
            GUI.color = c; GUI.DrawTexture(new Rect(r.x, r.y, r.width * Mathf.Clamp01(t), r.height), _px);
            GUI.color = Color.white;
        }
    }
}
