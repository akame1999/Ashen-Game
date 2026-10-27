using Ashen.Core;
using UnityEngine;

namespace Ashen.Player
{
    [RequireComponent(typeof(PlayerController2D))]
    public class PlayerAnimator : MonoBehaviour
    {
        public string resourcePath = "Sprites/Player";

        SpriteAnimator _anim;
        PlayerController2D _p;
        Rigidbody2D _rb;
        SpriteRenderer _sr;
        float _seenAttack = -10f;

        void Awake()
        {
            _p = GetComponent<PlayerController2D>();
            _rb = GetComponent<Rigidbody2D>();
            _sr = GetComponentInChildren<SpriteRenderer>();
            _anim = gameObject.AddComponent<SpriteAnimator>();
            _anim.Init(resourcePath, _sr);
        }

        void Update()
        {
            if (_p.Health.IsDead) { _anim.Hold("hurt", 0); _sr.color = new Color(0.5f, 0.5f, 0.5f, 1f); return; }
            _sr.color = Color.white;

            if (_p.LastAttackTime != _seenAttack) { _seenAttack = _p.LastAttackTime; _anim.Restart(); }

            var v = _rb.linearVelocity;
            if (Time.time - _p.LastAttackTime < 0.3f) _anim.Play("attack", 10f, false);
            else if (_p.IsDashing) _anim.Hold("dash", 0);
            else if (_p.IsStunned) _anim.Hold("hurt", 0);
            else if (!_p.Grounded) _anim.Hold(v.y > 0.5f ? "jump" : "fall", 0);
            else if (Mathf.Abs(v.x) > 0.5f) _anim.Play("run", 12f);
            else _anim.Play("idle", 3f);
        }
    }
}
