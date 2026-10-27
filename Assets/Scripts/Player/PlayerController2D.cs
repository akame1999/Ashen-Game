using Ashen.Combat;
using UnityEngine;

namespace Ashen.Player
{
    [RequireComponent(typeof(Rigidbody2D), typeof(Health))]
    public class PlayerController2D : MonoBehaviour
    {
        [Header("Movement")]
        public float moveSpeed = 7f;
        public float jumpVelocity = 15f;
        public float coyoteTime = 0.1f;
        public float jumpBuffer = 0.12f;
        public float fallGravityMultiplier = 1.8f;
        public float lowJumpMultiplier = 2.2f;

        [Header("Dash")]
        public float dashSpeed = 18f;
        public float dashDuration = 0.18f;
        public float dashCooldown = 0.6f;
        public float dashStamina = 25f;

        [Header("Attack")]
        public int lightDamage = 20;
        public float attackCooldown = 0.35f;
        public float attackStamina = 12f;
        public Vector2 attackOffset = new Vector2(0.9f, 0f);
        public Vector2 attackSize = new Vector2(1.4f, 1.1f);

        [Header("Stamina")]
        public float maxStamina = 100f;
        public float staminaRegen = 30f;

        public float Stamina { get; private set; }
        public Health Health { get; private set; }
        public bool Grounded { get; private set; }
        public bool IsDashing => _dashing;
        public bool IsStunned => Time.time < _stunUntil;
        public float LastAttackTime { get; private set; } = -10f;

        Rigidbody2D _rb;
        float _baseGravity;
        float _lastGrounded = -10f, _lastJumpPressed = -10f;
        float _dashEnd, _nextDash, _nextAttack, _stunUntil;
        float _dashDir = 1f;
        bool _grounded;
        bool _dashing;

        void Awake()
        {
            _rb = GetComponent<Rigidbody2D>();
            Health = GetComponent<Health>();
            _rb.freezeRotation = true;
            _rb.sleepMode = RigidbodySleepMode2D.NeverSleep;
            _rb.collisionDetectionMode = CollisionDetectionMode2D.Continuous;
            _rb.sharedMaterial = new PhysicsMaterial2D("NoFriction") { friction = 0f, bounciness = 0f };
            _baseGravity = _rb.gravityScale;
            Stamina = maxStamina;
            Health.Damaged += _ => _stunUntil = Time.time + 0.25f;
        }

        void Update()
        {
            if (Health.IsDead) return;

            if (Input.GetButtonDown("Jump")) _lastJumpPressed = Time.time;
            if (Input.GetKeyDown(KeyCode.LeftShift) || Input.GetKeyDown(KeyCode.K)) TryDash();
            if (Input.GetKeyDown(KeyCode.J) || Input.GetMouseButtonDown(0)) TryAttack();

            Stamina = Mathf.Min(maxStamina, Stamina + staminaRegen * Time.deltaTime);
        }

        void FixedUpdate()
        {
            if (Health.IsDead) { _rb.linearVelocity = new Vector2(0, _rb.linearVelocity.y); return; }

            Grounded = _grounded;
            if (_grounded) _lastGrounded = Time.time;
            _grounded = false; // re-set by OnCollisionStay2D during the next physics step

            if (_dashing)
            {
                if (Time.time >= _dashEnd) EndDash();
                else { _rb.linearVelocity = new Vector2(_dashDir * dashSpeed, 0f); return; }
            }

            if (Time.time < _stunUntil) return;

            float x = Input.GetAxisRaw("Horizontal");
            var v = _rb.linearVelocity;
            v.x = x * moveSpeed;
            if (x != 0) Face(Mathf.Sign(x));

            // jump with coyote time + input buffering
            if (Time.time - _lastJumpPressed <= jumpBuffer && Time.time - _lastGrounded <= coyoteTime)
            {
                v.y = jumpVelocity;
                _lastJumpPressed = -10f;
                _lastGrounded = -10f;
            }

            // snappier jump arc
            if (v.y < 0) v += Vector2.up * Physics2D.gravity.y * (fallGravityMultiplier - 1f) * Time.fixedDeltaTime;
            else if (v.y > 0 && !Input.GetButton("Jump")) v += Vector2.up * Physics2D.gravity.y * (lowJumpMultiplier - 1f) * Time.fixedDeltaTime;

            _rb.linearVelocity = v;
        }

        void OnCollisionStay2D(Collision2D c)
        {
            foreach (var p in c.contacts)
                if (p.normal.y > 0.5f) { _grounded = true; return; }
        }

        void Face(float dir) =>
            transform.localScale = new Vector3(dir * Mathf.Abs(transform.localScale.x), transform.localScale.y, 1f);

        void TryDash()
        {
            if (_dashing || Time.time < _nextDash || Stamina < dashStamina || Time.time < _stunUntil) return;
            Stamina -= dashStamina;
            _dashing = true;
            _dashEnd = Time.time + dashDuration;
            _nextDash = Time.time + dashCooldown;
            float x = Input.GetAxisRaw("Horizontal");
            _dashDir = x != 0 ? Mathf.Sign(x) : Mathf.Sign(transform.localScale.x);
            Face(_dashDir);
            _rb.gravityScale = 0f;
            Health.Invulnerable = true; // i-frames
        }

        void EndDash()
        {
            _dashing = false;
            _rb.gravityScale = _baseGravity;
            Health.Invulnerable = false;
        }

        void TryAttack()
        {
            if (_dashing || Time.time < _nextAttack || Stamina < attackStamina || Time.time < _stunUntil) return;
            Stamina -= attackStamina;
            _nextAttack = Time.time + attackCooldown;
            LastAttackTime = Time.time;
            MeleeAttack.Strike(transform, Health.team, attackOffset, attackSize, lightDamage, 7f);
            StartCoroutine(SwingFlash());
        }

        System.Collections.IEnumerator SwingFlash()
        {
            // placeholder swing visual until animations exist
            var go = new GameObject("SwingFx");
            go.transform.SetParent(transform, false);
            go.transform.localPosition = attackOffset;
            go.transform.localScale = new Vector3(attackSize.x / Mathf.Abs(transform.localScale.x), attackSize.y / Mathf.Abs(transform.localScale.y), 1f);
            var sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = Core.Placeholder.Square(new Color(1f, 1f, 1f, 0.35f));
            sr.sortingOrder = 5;
            yield return new WaitForSeconds(0.08f);
            Destroy(go);
        }

        void OnDrawGizmosSelected()
        {
            Gizmos.color = Color.red;
            float f = Mathf.Sign(transform.localScale.x == 0 ? 1 : transform.localScale.x);
            Gizmos.DrawWireCube(transform.position + new Vector3(attackOffset.x * f, attackOffset.y), attackSize);
        }
    }
}
