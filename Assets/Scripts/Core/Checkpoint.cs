using Ashen.Player;
using Ashen.UI;
using UnityEngine;

namespace Ashen.Core
{
    /// <summary>Trigger zone: touching it makes this the player's respawn point.</summary>
    [RequireComponent(typeof(BoxCollider2D))]
    public class Checkpoint : MonoBehaviour
    {
        public Color inactiveColor = new Color(0.35f, 0.3f, 0.4f);
        public Color activeColor = new Color(1f, 0.55f, 0.15f);

        SpriteRenderer _sr;
        SimpleHUD _hud;
        static Checkpoint _current;

        void Awake()
        {
            GetComponent<BoxCollider2D>().isTrigger = true;
            _sr = GetComponentInChildren<SpriteRenderer>();
            Paint(inactiveColor);
        }

        void Start() => _hud = FindFirstObjectByType<SimpleHUD>();

        void OnTriggerEnter2D(Collider2D other)
        {
            if (_current == this || other.GetComponentInParent<PlayerController2D>() == null) return;
            if (_hud == null) return;

            if (_current != null) _current.Paint(_current.inactiveColor);
            _current = this;
            _hud.respawnPoint = transform;
            Paint(activeColor);
        }

        void OnDestroy() { if (_current == this) _current = null; }

        void Paint(Color c) { if (_sr != null) _sr.color = c; }
    }
}
