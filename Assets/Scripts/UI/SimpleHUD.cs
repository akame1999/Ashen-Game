using Ashen.Core;
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
        bool _paused;

        void Awake() { _px = Texture2D.whiteTexture; }

        void OnDisable() { SetPaused(false); }   // never leave the game frozen

        void SetPaused(bool value)
        {
            _paused = value;
            Time.timeScale = value ? 0f : 1f;
        }

        void Update()
        {
            if (Input.GetKeyDown(KeyCode.Escape)) SetPaused(!_paused);

            if (Input.GetKeyDown(KeyCode.F9)) SaveGame.Clear();   // wipe save; takes effect next Play

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

            if (_paused) DrawPause();

            if (player.Health.IsDead)
            {
                var style = new GUIStyle(GUI.skin.label) { fontSize = 40, alignment = TextAnchor.MiddleCenter };
                GUI.Label(new Rect(0, Screen.height / 2f - 40, Screen.width, 80), "YOU DIED  -  press R", style);
            }
        }

        void DrawPause()
        {
            GUI.color = new Color(0, 0, 0, 0.7f);
            GUI.DrawTexture(new Rect(0, 0, Screen.width, Screen.height), _px);
            GUI.color = Color.white;

            var title = new GUIStyle(GUI.skin.label) { fontSize = 48, alignment = TextAnchor.MiddleCenter };
            GUI.Label(new Rect(0, Screen.height * 0.25f, Screen.width, 80), "PAUSED", title);

            var body = new GUIStyle(GUI.skin.label) { fontSize = 20, alignment = TextAnchor.UpperCenter };
            GUI.Label(new Rect(0, Screen.height * 0.25f + 90f, Screen.width, 200),
                "Move: A / D     Jump: Space     Attack: J     Dash: Shift / K\n" +
                "Respawn: R     Wipe save: F9\n\nEsc to resume", body);
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
