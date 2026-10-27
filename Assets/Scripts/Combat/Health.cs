using System;
using UnityEngine;

namespace Ashen.Combat
{
    public class Health : MonoBehaviour
    {
        public int team;                 // 0 = player, 1 = enemy
        public int maxHealth = 100;
        public float hitInvulnerability = 0.35f;

        public int Current { get; private set; }
        public bool Invulnerable { get; set; }   // set by dash for i-frames
        public bool IsDead { get; private set; }

        public event Action<Vector2> Damaged;   // passes knockback direction
        public event Action Died;

        float _hitUntil;

        void Awake() => Current = maxHealth;

        public bool TakeDamage(int amount, Vector2 sourcePosition, float knockback = 6f)
        {
            if (IsDead || Invulnerable || Time.time < _hitUntil) return false;

            Current = Mathf.Max(0, Current - amount);
            _hitUntil = Time.time + hitInvulnerability;

            var dir = ((Vector2)transform.position - sourcePosition);
            dir = new Vector2(Mathf.Sign(dir.x == 0 ? 1 : dir.x), 0.4f).normalized;

            var rb = GetComponent<Rigidbody2D>();
            if (rb != null) rb.linearVelocity = dir * knockback;

            Damaged?.Invoke(dir);
            if (Current <= 0)
            {
                IsDead = true;
                Died?.Invoke();
            }
            return true;
        }

        public void Revive()
        {
            IsDead = false;
            Current = maxHealth;
        }
    }
}
