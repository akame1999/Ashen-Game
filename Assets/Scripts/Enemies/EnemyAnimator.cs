using Ashen.Core;
using UnityEngine;

namespace Ashen.Enemies
{
    [RequireComponent(typeof(EnemyAI))]
    public class EnemyAnimator : MonoBehaviour
    {
        public string resourcePath = "Sprites/Husk";
        SpriteAnimator _anim;
        EnemyAI _ai;

        void Awake()
        {
            _ai = GetComponent<EnemyAI>();
            _anim = gameObject.AddComponent<SpriteAnimator>();
            _anim.Init(resourcePath, GetComponentInChildren<SpriteRenderer>());
        }

        void Update()
        {
            switch (_ai.Pose)
            {
                case "walk": _anim.Play("run", 8f); break;
                case "windup": _anim.Hold("attack", 0); break;
                case "strike": _anim.Hold("attack", 1); break;
                case "hurt": _anim.Hold("hurt", 0); break;
                default: _anim.Play("idle", 3f); break;
            }
        }
    }
}
