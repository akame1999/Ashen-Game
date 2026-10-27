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

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var camGo = new GameObject("Main Camera") { tag = "MainCamera" };
            var cam = camGo.AddComponent<Camera>();
            cam.orthographic = true; cam.orthographicSize = 6f;
            cam.backgroundColor = new Color(0.05f, 0.04f, 0.07f);
            cam.clearFlags = CameraClearFlags.SolidColor;
            camGo.transform.position = new Vector3(0, 2, -10);
            camGo.AddComponent<AudioListener>();
            var follow = camGo.AddComponent<CameraFollow>();

            Ground("Floor", new Vector2(0, -1), new Vector2(40, 2));
            Ground("WallL", new Vector2(-20, 4), new Vector2(2, 12));
            Ground("WallR", new Vector2(20, 4), new Vector2(2, 12));
            Ground("PlatformA", new Vector2(-6, 2.5f), new Vector2(5, 0.6f));
            Ground("PlatformB", new Vector2(5, 4.5f), new Vector2(5, 0.6f));

            var respawn = new GameObject("Respawn").transform;
            respawn.position = new Vector3(-14, 1.2f, 0);

            var player = Actor("Player", respawn.position, new Vector2(0.9f, 1.6f));
            var pc = player.AddComponent<PlayerController2D>();
            player.AddComponent<PlayerAnimator>();
            player.GetComponent<Health>().team = 0;
            follow.target = player.transform;

            Enemy("Husk A", new Vector2(2, 1.2f));
            Enemy("Husk B", new Vector2(10, 5.4f));

            var hud = new GameObject("HUD").AddComponent<SimpleHUD>();
            hud.player = pc; hud.respawnPoint = respawn;

            System.IO.Directory.CreateDirectory("Assets/Scenes");
            EditorSceneManager.SaveScene(scene, ScenePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            Debug.Log("Ashen: starter scene built at " + ScenePath);
        }

        static void Ground(string name, Vector2 pos, Vector2 size)
        {
            var go = new GameObject(name);
            go.transform.position = pos;
            go.transform.localScale = new Vector3(size.x, size.y, 1);
            go.AddComponent<SpriteRenderer>();
            go.AddComponent<PlaceholderVisual>().color = new Color(0.22f, 0.2f, 0.26f);
            go.AddComponent<BoxCollider2D>();
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
