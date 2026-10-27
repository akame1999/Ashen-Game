using UnityEngine;

namespace Ashen.Combat
{
    /// <summary>Shared melee hit check used by the player and enemies.</summary>
    public static class MeleeAttack
    {
        public static int Strike(Transform attacker, int team, Vector2 offset, Vector2 size,
                                 int damage, float knockback)
        {
            float facing = Mathf.Sign(attacker.localScale.x == 0 ? 1 : attacker.localScale.x);
            Vector2 centre = (Vector2)attacker.position + new Vector2(offset.x * facing, offset.y);

            int hits = 0;
            foreach (var col in Physics2D.OverlapBoxAll(centre, size, 0f))
            {
                var h = col.GetComponentInParent<Health>();
                if (h == null || h.team == team || h.IsDead) continue;
                if (h.TakeDamage(damage, attacker.position, knockback)) hits++;
            }
            return hits;
        }
    }
}
