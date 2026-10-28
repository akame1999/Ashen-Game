#if UNITY_EDITOR
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// Builds the greybox movement scene and creates a replaceable locomotion Animator Blend Tree.
/// Menus: Tools > Code Lyoko > Create Prototype Scene / Setup Player Locomotion Animations.
/// </summary>
public static class PrototypeSceneSetup
{
    private const string Root = "Assets/_Project";
    private const string ScenesFolder = Root + "/Scenes";
    private const string MaterialsFolder = Root + "/Materials";
    private const string AnimationsFolder = Root + "/Animations";
    private const string ScenePath = ScenesFolder + "/Prototype_Scene.unity";
    private const string AnimatorControllerPath = AnimationsFolder + "/Player_Locomotion.controller";

    [MenuItem("Tools/Code Lyoko/Create Prototype Scene")]
    public static void CreatePrototypeScene()
    {
        EnsureFolder("Assets", "_Project");
        EnsureFolder(Root, "Scenes");
        EnsureFolder(Root, "Materials");
        EnsureFolder(Root, "Animations");

        AnimatorController locomotionController = CreateOrUpdateLocomotionAssets();

        Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

        Material groundMaterial = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeGround.mat",
            new Color(0.24f, 0.27f, 0.29f));
        Material wallMaterial = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeWalls.mat",
            new Color(0.12f, 0.15f, 0.17f));
        Material playerMaterial = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypePlayer.mat",
            new Color(0.55f, 0.28f, 0.12f));

        GameObject floor = GameObject.CreatePrimitive(PrimitiveType.Plane);
        floor.name = "TestFloor";
        floor.transform.position = Vector3.zero;
        floor.transform.localScale = new Vector3(4f, 1f, 4f);
        floor.GetComponent<Renderer>().sharedMaterial = groundMaterial;

        const float halfExtent = 20f;
        const float wallHeight = 3f;
        const float wallThickness = 0.8f;

        CreateWall("Wall_North", new Vector3(0f, wallHeight / 2f, halfExtent),
            new Vector3(halfExtent * 2f, wallHeight, wallThickness), wallMaterial);
        CreateWall("Wall_South", new Vector3(0f, wallHeight / 2f, -halfExtent),
            new Vector3(halfExtent * 2f, wallHeight, wallThickness), wallMaterial);
        CreateWall("Wall_East", new Vector3(halfExtent, wallHeight / 2f, 0f),
            new Vector3(wallThickness, wallHeight, halfExtent * 2f), wallMaterial);
        CreateWall("Wall_West", new Vector3(-halfExtent, wallHeight / 2f, 0f),
            new Vector3(wallThickness, wallHeight, halfExtent * 2f), wallMaterial);

        GameObject player = CreatePlayer(playerMaterial, locomotionController);

        GameObject cameraObject = new GameObject("IsometricCamera");
        cameraObject.tag = "MainCamera";
        Camera camera = cameraObject.AddComponent<Camera>();
        camera.clearFlags = CameraClearFlags.Skybox;
        camera.nearClipPlane = 0.1f;
        camera.farClipPlane = 300f;
        camera.orthographic = true;
        camera.orthographicSize = 10f;
        cameraObject.transform.position = player.transform.position + new Vector3(0f, 12f, -12f);
        cameraObject.transform.rotation = Quaternion.Euler(45f, 0f, 0f);
        IsometricCameraFollow follow = cameraObject.AddComponent<IsometricCameraFollow>();
        follow.Target = player.transform;

        GameObject lightObject = new GameObject("Directional Light");
        Light directionalLight = lightObject.AddComponent<Light>();
        directionalLight.type = LightType.Directional;
        directionalLight.intensity = 1.25f;
        lightObject.transform.rotation = Quaternion.Euler(50f, -30f, 0f);

        RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Trilight;
        RenderSettings.ambientSkyColor = new Color(0.42f, 0.45f, 0.5f);
        RenderSettings.ambientEquatorColor = new Color(0.27f, 0.28f, 0.3f);
        RenderSettings.ambientGroundColor = new Color(0.12f, 0.12f, 0.13f);

        EditorSceneManager.MarkSceneDirty(scene);
        if (!EditorSceneManager.SaveScene(scene, ScenePath))
        {
            Debug.LogError("Could not save prototype scene to " + ScenePath);
            return;
        }

        List<EditorBuildSettingsScene> buildScenes = new List<EditorBuildSettingsScene>(EditorBuildSettings.scenes);
        for (int i = buildScenes.Count - 1; i >= 0; i--)
        {
            if (buildScenes[i].path == ScenePath)
                buildScenes.RemoveAt(i);
        }
        buildScenes.Insert(0, new EditorBuildSettingsScene(ScenePath, true));
        EditorBuildSettings.scenes = buildScenes.ToArray();

        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        Debug.Log("Prototype scene created: " + ScenePath +
                  ". Press Play; use WASD/arrows to walk and hold Shift to run.");
        EditorUtility.DisplayDialog(
            "Prototype Scene Created",
            "Created the greybox arena and configured a locomotion Blend Tree.\n\n" +
            "Open the Game tab and press Play. WASD or arrow keys move; hold Shift to run.\n" +
            "The capsule uses placeholder squash/bob clips that can later be replaced with character animations.",
            "OK");
    }

    [MenuItem("Tools/Code Lyoko/Setup Player Locomotion Animations")]
    public static void SetupPlayerLocomotionAnimations()
    {
        EnsureFolder("Assets", "_Project");
        EnsureFolder(Root, "Animations");

        AnimatorController locomotionController = CreateOrUpdateLocomotionAssets();
        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player == null)
            player = GameObject.Find("Player");

        if (player == null)
        {
            EditorUtility.DisplayDialog(
                "Player Not Found",
                "Open Prototype_Scene.unity first, then run this command again.",
                "OK");
            return;
        }

        Transform visualTransform = player.transform.Find("PlayerVisual");
        if (visualTransform == null)
        {
            Renderer oldRenderer = player.GetComponent<Renderer>();
            Material existingMaterial = oldRenderer != null ? oldRenderer.sharedMaterial : null;

            GameObject visual = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            visual.name = "PlayerVisual";
            visual.transform.SetParent(player.transform, false);
            visual.transform.localPosition = Vector3.zero;
            visual.transform.localRotation = Quaternion.identity;
            visual.transform.localScale = Vector3.one;

            Renderer visualRenderer = visual.GetComponent<Renderer>();
            if (existingMaterial != null)
                visualRenderer.sharedMaterial = existingMaterial;

            Collider visualCollider = visual.GetComponent<Collider>();
            if (visualCollider != null)
                Object.DestroyImmediate(visualCollider);

            if (oldRenderer != null)
                Object.DestroyImmediate(oldRenderer);
            MeshFilter oldMeshFilter = player.GetComponent<MeshFilter>();
            if (oldMeshFilter != null)
                Object.DestroyImmediate(oldMeshFilter);

            visualTransform = visual.transform;
        }

        Animator animator = visualTransform.GetComponent<Animator>();
        if (animator == null)
            animator = visualTransform.gameObject.AddComponent<Animator>();

        animator.runtimeAnimatorController = locomotionController;
        animator.applyRootMotion = false;
        animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;

        PlayerLocomotionAnimator locomotion = player.GetComponent<PlayerLocomotionAnimator>();
        if (locomotion == null)
            locomotion = player.AddComponent<PlayerLocomotionAnimator>();
        locomotion.CharacterAnimator = animator;

        IsometricPlayerController movement = player.GetComponent<IsometricPlayerController>();
        if (movement == null)
            movement = player.AddComponent<IsometricPlayerController>();

        Scene scene = SceneManager.GetActiveScene();
        EditorSceneManager.MarkSceneDirty(scene);
        if (!string.IsNullOrEmpty(scene.path))
            EditorSceneManager.SaveScene(scene);

        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        EditorUtility.DisplayDialog(
            "Locomotion Animations Configured",
            "The Player now has an Animator Blend Tree with Idle, Walk and Run placeholder clips.\n\n" +
            "WASD/arrows = walk; hold Shift = run. These capsule animations are placeholders; replace the clips when importing a rigged character.",
            "OK");
    }

    private static GameObject CreatePlayer(Material playerMaterial, AnimatorController locomotionController)
    {
        GameObject player = new GameObject("Player");
        player.tag = "Player";
        player.transform.position = new Vector3(0f, 1f, 0f);

        GameObject visual = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        visual.name = "PlayerVisual";
        visual.transform.SetParent(player.transform, false);
        visual.transform.localPosition = Vector3.zero;
        visual.transform.localRotation = Quaternion.identity;
        visual.transform.localScale = Vector3.one;
        visual.GetComponent<Renderer>().sharedMaterial = playerMaterial;
        Collider visualCollider = visual.GetComponent<Collider>();
        if (visualCollider != null)
            Object.DestroyImmediate(visualCollider);

        Animator animator = visual.AddComponent<Animator>();
        animator.runtimeAnimatorController = locomotionController;
        animator.applyRootMotion = false;
        animator.cullingMode = AnimatorCullingMode.AlwaysAnimate;

        CharacterController controller = player.AddComponent<CharacterController>();
        controller.height = 2f;
        controller.radius = 0.45f;
        controller.center = Vector3.zero;
        controller.stepOffset = 0.3f;
        controller.slopeLimit = 45f;

        PlayerLocomotionAnimator locomotion = player.AddComponent<PlayerLocomotionAnimator>();
        locomotion.CharacterAnimator = animator;
        player.AddComponent<IsometricPlayerController>();
        return player;
    }

    private static AnimatorController CreateOrUpdateLocomotionAssets()
    {
        AnimationClip idleClip = CreateOrUpdateClip(
            AnimationsFolder + "/Player_Idle.anim", "Player_Idle", 1.6f, 0.012f, 1.008f);
        AnimationClip walkClip = CreateOrUpdateClip(
            AnimationsFolder + "/Player_Walk.anim", "Player_Walk", 0.52f, 0.045f, 0.98f);
        AnimationClip runClip = CreateOrUpdateClip(
            AnimationsFolder + "/Player_Run.anim", "Player_Run", 0.38f, 0.075f, 0.955f);

        AnimatorController controller = AssetDatabase.LoadAssetAtPath<AnimatorController>(AnimatorControllerPath);
        if (controller == null)
            controller = AnimatorController.CreateAnimatorControllerAtPath(AnimatorControllerPath);

        bool hasMoveSpeed = false;
        foreach (AnimatorControllerParameter parameter in controller.parameters)
        {
            if (parameter.name == "MoveSpeed" && parameter.type == AnimatorControllerParameterType.Float)
            {
                hasMoveSpeed = true;
                break;
            }
        }
        if (!hasMoveSpeed)
            controller.AddParameter("MoveSpeed", AnimatorControllerParameterType.Float);

        AnimatorStateMachine stateMachine = controller.layers[0].stateMachine;
        AnimatorState locomotionState = null;
        foreach (ChildAnimatorState childState in stateMachine.states)
        {
            if (childState.state.name == "Locomotion")
            {
                locomotionState = childState.state;
                break;
            }
        }
        if (locomotionState == null)
            locomotionState = stateMachine.AddState("Locomotion");

        BlendTree tree = locomotionState.motion as BlendTree;
        if (tree == null)
        {
            tree = new BlendTree
            {
                name = "Locomotion Blend Tree",
                blendType = BlendTreeType.Simple1D,
                blendParameter = "MoveSpeed",
                useAutomaticThresholds = false
            };
            AssetDatabase.AddObjectToAsset(tree, controller);
        }

        tree.blendType = BlendTreeType.Simple1D;
        tree.blendParameter = "MoveSpeed";
        tree.useAutomaticThresholds = false;
        tree.children = new[]
        {
            new ChildMotion { motion = idleClip, threshold = 0f, timeScale = 1f },
            new ChildMotion { motion = walkClip, threshold = 0.5f, timeScale = 1f },
            new ChildMotion { motion = runClip, threshold = 1f, timeScale = 1f }
        };
        locomotionState.motion = tree;
        EditorUtility.SetDirty(tree);
        EditorUtility.SetDirty(controller);
        AssetDatabase.SaveAssets();
        return controller;
    }

    private static AnimationClip CreateOrUpdateClip(
        string path, string clipName, float cycleSeconds, float bobHeight, float squashScale)
    {
        AnimationClip clip = AssetDatabase.LoadAssetAtPath<AnimationClip>(path);
        if (clip == null)
        {
            clip = new AnimationClip { name = clipName, frameRate = 30f };
            AssetDatabase.CreateAsset(clip, path);
        }

        clip.ClearCurves();
        float mid = cycleSeconds * 0.5f;
        float quarter = cycleSeconds * 0.25f;
        float threeQuarter = cycleSeconds * 0.75f;

        clip.SetCurve(string.Empty, typeof(Transform), "localPosition.y",
            new AnimationCurve(
                new Keyframe(0f, 0f),
                new Keyframe(quarter, bobHeight),
                new Keyframe(mid, 0f),
                new Keyframe(threeQuarter, bobHeight * 0.2f),
                new Keyframe(cycleSeconds, 0f)));

        clip.SetCurve(string.Empty, typeof(Transform), "localScale.y",
            new AnimationCurve(
                new Keyframe(0f, 1f),
                new Keyframe(quarter, squashScale),
                new Keyframe(mid, 1f),
                new Keyframe(threeQuarter, 0.992f),
                new Keyframe(cycleSeconds, 1f)));

        AnimationClipSettings settings = AnimationUtility.GetAnimationClipSettings(clip);
        settings.loopTime = true;
        settings.loopBlend = false;
        AnimationUtility.SetAnimationClipSettings(clip, settings);
        clip.wrapMode = WrapMode.Loop;
        EditorUtility.SetDirty(clip);
        return clip;
    }

    private static void CreateWall(string objectName, Vector3 position, Vector3 scale, Material material)
    {
        GameObject wall = GameObject.CreatePrimitive(PrimitiveType.Cube);
        wall.name = objectName;
        wall.transform.position = position;
        wall.transform.localScale = scale;
        wall.GetComponent<Renderer>().sharedMaterial = material;
    }

    private static Material CreateOrLoadMaterial(string path, Color color)
    {
        Material existing = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (existing != null)
        {
            SetMaterialColor(existing, color);
            EditorUtility.SetDirty(existing);
            return existing;
        }

        Shader shader = Shader.Find("Universal Render Pipeline/Lit");
        if (shader == null)
            shader = Shader.Find("Standard");

        if (shader == null)
        {
            Debug.LogWarning("No compatible shader found; using Unity's default primitive material.");
            return null;
        }

        Material material = new Material(shader);
        SetMaterialColor(material, color);
        AssetDatabase.CreateAsset(material, path);
        return material;
    }

    private static void SetMaterialColor(Material material, Color color)
    {
        if (material == null)
            return;

        if (material.HasProperty("_BaseColor"))
            material.SetColor("_BaseColor", color);
        if (material.HasProperty("_Color"))
            material.SetColor("_Color", color);
    }

    private static void EnsureFolder(string parent, string folderName)
    {
        string path = parent + "/" + folderName;
        if (!AssetDatabase.IsValidFolder(path))
            AssetDatabase.CreateFolder(parent, folderName);
    }
}
#endif
