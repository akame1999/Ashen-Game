#if UNITY_EDITOR
using Ashen.Combat;
using Ashen.Core;
using Ashen.Enemies;
using Ashen.Player;
using Ashen.UI;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Ashen.EditorTools
{
    public static class StarterSceneBuilder
    {
        const string ScenePath = "Assets/Scenes/Main.unity";

        [MenuItem("Ashen/Build Starter Scene")]
        public static void Build()
        {
            // make sure character sprites are imported with the pixel-art settings
            AssetDatabase.ImportAsset("Assets/Resources/Sprites", ImportAssetOptions.ImportRecursive | ImportAssetOptions.ForceUpdate);
            AssetDatabase.ImportAsset("Assets/Resources/Backgrounds", ImportAssetOptions.ImportRecursive | ImportAssetOptions.ForceUpdate);
            AssetDatabase.ImportAsset("Assets/Resources/Environment", ImportAssetOptions.ImportRecursive | ImportAssetOptions.ForceUpdate);

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var camGo = new GameObject("Main Camera") { tag = "MainCamera" };
            var cam = camGo.AddComponent<Camera>();
            cam.orthographic = true; cam.orthographicSize = 6f;
            cam.backgroundColor = new Color(0.05f, 0.04f, 0.07f);
            cam.clearFlags = CameraClearFlags.SolidColor;
            camGo.transform.position = new Vector3(0, 2, -10);
            camGo.AddComponent<AudioListener>();
            var follow = camGo.AddComponent<CameraFollow>();

            var bg = new GameObject("Background").transform;
            Layer(bg, "Sky",  "Backgrounds/sky",  -20, 1f,    1f,   0f, true);
            Layer(bg, "Far",  "Backgrounds/far",  -15, 0.92f, 0.8f, -4.5f, false);
            Layer(bg, "Mid",  "Backgrounds/mid",  -10, 0.75f, 0.6f, -4.5f, false);
            Layer(bg, "Near", "Backgrounds/near", -5,  0.45f, 0.4f, -4.5f, false);

            Ground("Floor", new Vector2(0, -1), new Vector2(40, 2), "Environment/ground");
            Ground("WallL", new Vector2(-20, 4), new Vector2(2, 12));
            Ground("WallR", new Vector2(20, 4), new Vector2(2, 12));
            Ground("PlatformA", new Vector2(-6, 2.3f), new Vector2(5, 1f), "Environment/platform");
            Ground("PlatformB", new Vector2(5, 4.3f), new Vector2(5, 1f), "Environment/platform");

            var respawn = new GameObject("Respawn").transform;
            respawn.position = new Vector3(-14, 1.2f, 0);

            var player = Actor("Player", respawn.position, new Vector2(0.9f, 1.6f));
            var pc = player.AddComponent<PlayerController2D>();
            player.AddComponent<PlayerAnimator>();
            player.GetComponent<Health>().team = 0;
            follow.target = player.transform;

            AddCheckpoint("Checkpoint A", new Vector2(0, 0.6f));
            AddCheckpoint("Checkpoint B", new Vector2(14, 0.6f));

            Enemy("Husk A", new Vector2(2, 1.2f));
            Enemy("Husk B", new Vector2(10, 5.4f));

            var hud = new GameObject("HUD").AddComponent<SimpleHUD>();
            hud.player = pc; hud.respawnPoint = respawn;

            System.IO.Directory.CreateDirectory("Assets/Scenes");
            EditorSceneManager.SaveScene(scene, ScenePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            Debug.Log("Ashen: starter scene built at " + ScenePath);
        }

        static void Layer(Transform parent, string name, string path, int order, float follow, float vFollow, float baseY, bool pin)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var l = go.AddComponent<ParallaxLayer>();
            l.resourcePath = path; l.sortingOrder = order; l.follow = follow;
            l.verticalFollow = vFollow; l.baseY = baseY; l.pinToCamera = pin;
        }

        // Solid geometry. With a 9-sliced tile sprite it is drawn tiled at its real size; otherwise a flat placeholder.
        static void Ground(string name, Vector2 pos, Vector2 size, string tilePath = null)
        {
            var go = new GameObject(name);
            go.transform.position = pos;
            var sr = go.AddComponent<SpriteRenderer>();
            var tile = tilePath != null ? Resources.Load<Sprite>(tilePath) : null;
            if (tile != null)
            {
                sr.sprite = tile;
                sr.drawMode = SpriteDrawMode.Sliced;
                sr.tileMode = SpriteTileMode.Continuous;
                sr.size = size;
                sr.sortingOrder = 0;
            }
            else
            {
                go.transform.localScale = new Vector3(size.x, size.y, 1);
                go.AddComponent<PlaceholderVisual>().color = new Color(0.22f, 0.2f, 0.26f);
            }
            var col = go.AddComponent<BoxCollider2D>();
            if (tile != null) col.size = size;
        }

        // Root = physics (collider, rigidbody, health). Child "Visual" = sprite, feet aligned to the collider bottom.
        static GameObject Actor(string name, Vector2 pos, Vector2 colliderSize)
        {
            var go = new GameObject(name);
            go.transform.position = pos;
            go.AddComponent<BoxCollider2D>().size = colliderSize;
            var rb = go.AddComponent<Rigidbody2D>();
            rb.gravityScale = 3f;
            go.AddComponent<Health>();

            var vis = new GameObject("Visual");
            vis.transform.SetParent(go.transform, false);
            vis.transform.localPosition = new Vector3(0, -colliderSize.y / 2f, 0);
            vis.AddComponent<SpriteRenderer>().sortingOrder = 2;
            return go;
        }

        // Thin trigger pillar; touching it moves the respawn point here.
        static void AddCheckpoint(string name, Vector2 pos)
        {
            var go = new GameObject(name);
            go.transform.position = pos;
            var col = go.AddComponent<BoxCollider2D>();
            col.size = new Vector2(1.2f, 2.4f);
            col.offset = new Vector2(0, 0.6f);
            go.AddComponent<Ashen.Core.Checkpoint>();

            var vis = new GameObject("Visual");
            vis.transform.SetParent(go.transform, false);
            var sr = vis.AddComponent<SpriteRenderer>();
            var pillar = Resources.Load<Sprite>("Environment/checkpoint");
            if (pillar != null)
            {
                vis.transform.localPosition = new Vector3(0, -0.6f, 0);   // sprite pivot = bottom centre, base on the floor
                sr.sprite = pillar;
            }
            else
            {
                vis.transform.localPosition = new Vector3(0, 0.6f, 0);
                vis.transform.localScale = new Vector3(0.3f, 1.8f, 1f);
                sr.sprite = Placeholder.Square(Color.white);
            }
            sr.sortingOrder = 1;

            // Flame in the brazier, lit while this is the active checkpoint (see Checkpoint.cs)
            var flame = new GameObject("Flame");
            flame.transform.SetParent(go.transform, false);
            flame.transform.localPosition = new Vector3(0, pillar != null ? 1.1f : 1.6f, 0);
            flame.transform.localScale = new Vector3(0.35f, 0.5f, 1f);
            var fsr = flame.AddComponent<SpriteRenderer>();
            fsr.sprite = Placeholder.Square(new Color(1f, 0.6f, 0.15f));
            fsr.sortingOrder = 2;
        }

        static void Enemy(string name, Vector2 pos)
        {
            var go = Actor(name, pos, new Vector2(0.9f, 1.6f));
            var h = go.GetComponent<Health>(); h.team = 1; h.maxHealth = 60;
            go.AddComponent<EnemyAI>();
            go.AddComponent<EnemyAnimator>();
        }
    }
}
#endif
