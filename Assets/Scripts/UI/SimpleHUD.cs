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

            if (player.Health.IsDead)
            {
                var style = new GUIStyle(GUI.skin.label) { fontSize = 40, alignment = TextAnchor.MiddleCenter };
                GUI.Label(new Rect(0, Screen.height / 2f - 40, Screen.width, 80), "YOU DIED  -  press R", style);
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
