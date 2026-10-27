using System.Collections.Generic;
using System.Linq;
using UnityEngine;

namespace Ashen.Core
{
    /// <summary>Plays frame-by-frame clips from Resources. Files are named "<clip>_<n>.png" (e.g. run_0).</summary>
    public class SpriteAnimator : MonoBehaviour
    {
        readonly Dictionary<string, Sprite[]> _clips = new Dictionary<string, Sprite[]>();
        SpriteRenderer _sr;
        string _current;
        float _timer;

        public void Init(string resourcePath, SpriteRenderer sr)
        {
            _sr = sr;
            var all = Resources.LoadAll<Sprite>(resourcePath);
            foreach (var g in all.GroupBy(s => ClipName(s.name)))
                _clips[g.Key] = g.OrderBy(s => s.name, System.StringComparer.Ordinal).ToArray();
            if (_clips.Count == 0) Debug.LogWarning("SpriteAnimator: no sprites found at Resources/" + resourcePath);
        }

        static string ClipName(string n)
        {
            int i = n.LastIndexOf('_');
            return i > 0 ? n.Substring(0, i) : n;
        }

        public void Play(string clip, float fps, bool loop = true)
        {
            if (_sr == null || !_clips.TryGetValue(clip, out var frames) || frames.Length == 0) return;
            if (clip != _current) { _current = clip; _timer = 0f; }
            else _timer += Time.deltaTime;
            int i = (int)(_timer * fps);
            i = loop ? i % frames.Length : Mathf.Min(i, frames.Length - 1);
            _sr.sprite = frames[i];
        }

        public void Hold(string clip, int index)
        {
            if (_sr == null || !_clips.TryGetValue(clip, out var frames) || frames.Length == 0) return;
            _current = clip;
            _sr.sprite = frames[Mathf.Clamp(index, 0, frames.Length - 1)];
        }

        public void Restart() => _current = null;
    }
}
