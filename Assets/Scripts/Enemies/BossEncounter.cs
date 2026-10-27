using Ashen.Combat;
using Ashen.Core;
using UnityEngine;

namespace Ashen.Enemies
{
    /// <summary>
    /// Turns an EnemyAI into a boss: a named health bar (see SimpleHUD) and a one-time
    /// enrage phase below a health threshold (faster, shorter wind-up, harder hits).
    /// </summary>
    [RequireComponent(typeof(EnemyAI), typeof(Health))]
    public class BossEncounter : MonoBehaviour
    {
        public string bossName = "The Hollow Warden";
        [Range(0.1f, 0.9f)] public float enrageAt = 0.5f;
        public float enrageSpeedMultiplier = 1.4f;
        public float enrageWindupMultiplier = 0.7f;
        public float enrageRecoverMultiplier = 0.7f;
        public float enrageDamageMultiplier = 1.3f;
        public float showBarDistance = 14f;

        /// <summary>The boss currently on screen (null when none).</summary>
        public static BossEncounter Active { get; private set; }
        /// <summary>True once any boss has been defeated this session.</summary>
        public static bool Defeated { get; private set; }

        public Health Health { get; private set; }
        public bool Enraged { get; private set; }
        public bool BarVisible { get; private set; }

        EnemyAI _ai;
        Transform _player;
        SpriteRenderer _sr;

        void Awake()
        {
            if (SaveGame.BossDefeated) { Destroy(gameObject); return; }   // already beaten in a previous session
            Health = GetComponent<Health>();
            _ai = GetComponent<EnemyAI>();
            _sr = GetComponentInChildren<SpriteRenderer>();
            Health.Damaged += OnDamaged;
            Health.Died += OnDied;
            Defeated = false;
            Active = this;
        }

        void Start()
        {
            var p = FindFirstObjectByType<Ashen.Player.PlayerController2D>();
            if (p != null) _player = p.transform;
        }

        void Update()
        {
            if (Health == null || _player == null || Health.IsDead) return;
            if (!BarVisible && Vector2.Distance(_player.position, transform.position) < showBarDistance)
                BarVisible = true;
        }

        void OnDamaged(Vector2 _)
        {
            BarVisible = true;
            if (!Enraged && Health.Current > 0 && Health.Current <= Health.maxHealth * enrageAt) Enrage();
        }

        void Enrage()
        {
            Enraged = true;
            _ai.chaseSpeed *= enrageSpeedMultiplier;
            _ai.patrolSpeed *= enrageSpeedMultiplier;
            _ai.windupTime *= enrageWindupMultiplier;
            _ai.recoverTime *= enrageRecoverMultiplier;
            _ai.damage = Mathf.RoundToInt(_ai.damage * enrageDamageMultiplier);
        }

        void OnDied()
        {
            Defeated = true;
            BarVisible = false;
            SaveGame.BossDefeated = true;
        }

        void OnDestroy()
        {
            if (Health != null) { Health.Damaged -= OnDamaged; Health.Died -= OnDied; }
            if (Active == this) Active = null;
        }
    }
}
