using Ashen.Combat;
using UnityEngine;

namespace Ashen.Enemies
{
    /// <summary>Souls-like enemy: patrol, chase, telegraphed wind-up, strike, recover.</summary>
    [RequireComponent(typeof(Rigidbody2D), typeof(Health))]
    [DefaultExecutionOrder(10)]
    public class EnemyAI : MonoBehaviour
    {
        enum State { Patrol, Chase, Windup, Strike, Recover, Dead }

        public float patrolSpeed = 2f, chaseSpeed = 4f;
        public float patrolRange = 4f;
        public float aggroRange = 7f, attackRange = 1.6f;
        public float windupTime = 0.55f, strikeTime = 0.12f, recoverTime = 0.8f;
        public int damage = 18;
        public Vector2 attackOffset = new Vector2(0.9f, 0f);
        public Vector2 attackSize = new Vector2(1.4f, 1.1f);

        public string Pose => _state switch
        {
            State.Windup => "windup",
            State.Strike => "strike",
            State.Patrol => "walk",
            State.Chase => "walk",
            State.Dead => "hurt",
            _ => "idle"
        };

        Rigidbody2D _rb;
        Health _health;
        SpriteRenderer _sr;
        Color _baseColor;
        Transform _target;
        Health _targetHealth;
        Vector2 _origin;
        State _state = State.Patrol;
        float _stateEnd;
        int _dir = 1;

        void Awake()
        {
            _rb = GetComponent<Rigidbody2D>();
            _health = GetComponent<Health>();
            _sr = GetComponentInChildren<SpriteRenderer>();
            _baseColor = _sr != null ? _sr.color : Color.white;
            _rb.freezeRotation = true;
            _rb.sleepMode = RigidbodySleepMode2D.NeverSleep;
            _origin = transform.position;
            _health.team = 1;
            _health.Died += OnDied;
        }

        void Start()
        {
            var p = FindFirstObjectByType<Player.PlayerController2D>();
            if (p != null) { _target = p.transform; _targetHealth = p.GetComponent<Health>(); }
        }

        void FixedUpdate()
        {
            if (_state == State.Dead) return;

            float dist = _target != null ? Vector2.Distance(_target.position, transform.position) : float.MaxValue;
            bool playerDead = _targetHealth != null && _targetHealth.IsDead;
            var v = _rb.linearVelocity;

            switch (_state)
            {
                case State.Patrol:
                    Tint(_baseColor);
                    if (transform.position.x > _origin.x + patrolRange) _dir = -1;
                    else if (transform.position.x < _origin.x - patrolRange) _dir = 1;
                    v.x = _dir * patrolSpeed;
                    Face(_dir);
                    if (!playerDead && dist < aggroRange) _state = State.Chase;
                    break;

                case State.Chase:
                    Tint(_baseColor);
                    if (playerDead || dist > aggroRange * 1.5f) { _state = State.Patrol; break; }
                    _dir = _target.position.x > transform.position.x ? 1 : -1;
                    Face(_dir);
                    v.x = _dir * chaseSpeed;
                    if (dist < attackRange) Enter(State.Windup, windupTime);
                    break;

                case State.Windup:
                    v.x = 0;
                    Tint(Color.yellow); // telegraph
                    if (Time.time >= _stateEnd)
                    {
                        Enter(State.Strike, strikeTime);
                        Tint(Color.red);
                        MeleeAttack.Strike(transform, 1, attackOffset, attackSize, damage, 9f);
                    }
                    break;

                case State.Strike:
                    v.x = 0;
                    if (Time.time >= _stateEnd) Enter(State.Recover, recoverTime);
                    break;

                case State.Recover:
                    v.x = 0;
                    Tint(_baseColor * 0.7f);
                    if (Time.time >= _stateEnd) _state = State.Chase;
                    break;
            }
            _rb.linearVelocity = v;
        }

        void Enter(State s, float duration) { _state = s; _stateEnd = Time.time + duration; }
        void Face(int d) => transform.localScale = new Vector3(d * Mathf.Abs(transform.localScale.x), transform.localScale.y, 1f);
        void Tint(Color c) { if (_sr != null) _sr.color = new Color(c.r, c.g, c.b, 1f); }

        void OnDied()
        {
            _state = State.Dead;
            _rb.linearVelocity = Vector2.zero;
            foreach (var c in GetComponentsInChildren<Collider2D>()) c.enabled = false;
            _rb.simulated = false;
            Destroy(gameObject, 1.5f);
            if (_sr != null) _sr.color = new Color(0.2f, 0.2f, 0.2f, 0.5f);
        }
    }
}
