using Ashen.Player;
using Ashen.UI;
using UnityEngine;

namespace Ashen.Core
{
    /// <summary>Trigger zone: touching it makes this the player's respawn point.</summary>
    [RequireComponent(typeof(BoxCollider2D))]
    public class Checkpoint : MonoBehaviour
    {
        public Color inactiveColor = new Color(0.7f, 0.68f, 0.78f);
        public Color activeColor = new Color(1f, 0.85f, 0.65f);

        SpriteRenderer _sr;
        Transform _flame;
        SimpleHUD _hud;
        static Checkpoint _current;

        void Awake()
        {
            GetComponent<BoxCollider2D>().isTrigger = true;
            var visual = transform.Find("Visual");
            _sr = visual != null ? visual.GetComponent<SpriteRenderer>() : GetComponentInChildren<SpriteRenderer>();
            _flame = transform.Find("Flame");
            Paint(inactiveColor, false);
        }

        void Start() => _hud = FindFirstObjectByType<SimpleHUD>();

        void OnTriggerEnter2D(Collider2D other)
        {
            if (_current == this || other.GetComponentInParent<PlayerController2D>() == null) return;
            if (_hud == null) return;

            if (_current != null) _current.Paint(_current.inactiveColor, false);
            _current = this;
            _hud.respawnPoint = transform;
            Paint(activeColor, true);
        }

        void OnDestroy() { if (_current == this) _current = null; }

        void Paint(Color c, bool lit)
        {
            if (_sr != null) _sr.color = c;
            if (_flame != null) _flame.gameObject.SetActive(lit);
        }
    }
}
