#if UNITY_EDITOR
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// Creates the greybox scene and a stylized primitive mannequin with visible procedural gait.
/// Menu: Tools > Code Lyoko > Create Prototype Scene / Upgrade Player Locomotion Placeholder.
/// </summary>
public static class PrototypeSceneSetup
{
    private const string Root = "Assets/_Project";
    private const string ScenesFolder = Root + "/Scenes";
    private const string MaterialsFolder = Root + "/Materials";
    private const string ScenePath = ScenesFolder + "/Prototype_Scene.unity";

    [MenuItem("Tools/Code Lyoko/Create Prototype Scene")]
    public static void CreatePrototypeScene()
    {
        EnsureFolder("Assets", "_Project");
        EnsureFolder(Root, "Scenes");
        EnsureFolder(Root, "Materials");

        Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

        Material groundMaterial = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeGround.mat", new Color(0.24f, 0.27f, 0.29f));
        Material wallMaterial = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeWalls.mat", new Color(0.12f, 0.15f, 0.17f));
        Material playerMaterial = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypePlayer.mat", new Color(0.55f, 0.28f, 0.12f));
        Material armorMaterial = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeArmor.mat", new Color(0.18f, 0.12f, 0.10f));
        Material skinMaterial = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeSkin.mat", new Color(0.62f, 0.43f, 0.29f));
        Material detailMaterial = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeDetails.mat", new Color(0.045f, 0.035f, 0.03f));

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

        GameObject player = CreatePlayer(playerMaterial, armorMaterial, skinMaterial, detailMaterial);

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
                  ". WASD/arrows walk, hold Shift to run.");
        EditorUtility.DisplayDialog(
            "Prototype Scene Created",
            "Created a stylized mannequin with visible arm and leg swings, walk/run cadence, body bounce, a bounded arena and a follow camera.\n\n" +
            "Open the Game tab and press Play. WASD or arrow keys move; hold Shift to run.",
            "OK");
    }

    [MenuItem("Tools/Code Lyoko/Upgrade Player Locomotion Placeholder")]
    public static void UpgradePlayerLocomotionPlaceholder()
    {
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

        // Clear stale Missing (Mono Script) components left by earlier prototype iterations.
        // In particular, this keeps a broken old animation component from lingering on the Player.
        GameObjectUtility.RemoveMonoBehavioursWithMissingScript(player);

        EnsureFolder("Assets", "_Project");
        EnsureFolder(Root, "Materials");

        Transform oldVisualRoot = player.transform.Find("PlayerVisualRoot");
        Material body = FindOrCreateMaterialFromExisting(
            player, MaterialsFolder + "/PrototypePlayer.mat", new Color(0.55f, 0.28f, 0.12f));
        Material armor = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeArmor.mat", new Color(0.18f, 0.12f, 0.10f));
        Material skin = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeSkin.mat", new Color(0.62f, 0.43f, 0.29f));
        Material details = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeDetails.mat", new Color(0.045f, 0.035f, 0.03f));

        if (oldVisualRoot != null)
            Object.DestroyImmediate(oldVisualRoot.gameObject);

        // Remove old direct visual children such as the single capsule; keep the Player root and controller.
        for (int i = player.transform.childCount - 1; i >= 0; i--)
        {
            Transform child = player.transform.GetChild(i);
            Object.DestroyImmediate(child.gameObject);
        }

        BuildHumanoidVisual(player, body, armor, skin, details);

        Scene scene = SceneManager.GetActiveScene();
        EditorSceneManager.MarkSceneDirty(scene);
        if (!string.IsNullOrEmpty(scene.path))
            EditorSceneManager.SaveScene(scene);

        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        EditorUtility.DisplayDialog(
            "Locomotion Placeholder Upgraded",
            "Replaced the single capsule with a stylized primitive mannequin. Arms and legs swing during movement; hold Shift to run faster with a longer, quicker stride.\n\n" +
            "This is still a prototype mannequin. A rigged character with authored animations will come later.",
            "OK");
    }

    private static GameObject CreatePlayer(
        Material bodyMaterial, Material armorMaterial, Material skinMaterial, Material detailMaterial)
    {
        GameObject player = new GameObject("Player");
        player.tag = "Player";
        player.transform.position = new Vector3(0f, 1f, 0f);

        CharacterController controller = player.AddComponent<CharacterController>();
        controller.height = 2f;
        controller.radius = 0.45f;
        controller.center = Vector3.zero;
        controller.stepOffset = 0.3f;
        controller.slopeLimit = 45f;

        BuildHumanoidVisual(player, bodyMaterial, armorMaterial, skinMaterial, detailMaterial);
        player.AddComponent<IsometricPlayerController>();
        return player;
    }

    private static void BuildHumanoidVisual(
        GameObject player, Material bodyMaterial, Material armorMaterial, Material skinMaterial, Material detailMaterial)
    {
        GameObject visual = new GameObject("PlayerVisualRoot");
        visual.transform.SetParent(player.transform, false);
        visual.transform.localPosition = Vector3.zero;
        visual.transform.localRotation = Quaternion.identity;

        Transform torso = CreateVisualPrimitive(
            PrimitiveType.Capsule, "Torso", visual.transform,
            new Vector3(0f, 0.26f, 0f), new Vector3(0.34f, 0.42f, 0.23f), bodyMaterial);
        Transform head = CreateVisualPrimitive(
            PrimitiveType.Sphere, "Head", visual.transform,
            new Vector3(0f, 0.88f, 0f), new Vector3(0.34f, 0.34f, 0.34f), skinMaterial);

        CreateVisualPrimitive(
            PrimitiveType.Cube, "Belt", visual.transform,
            new Vector3(0f, -0.055f, 0.015f), new Vector3(0.43f, 0.11f, 0.27f), armorMaterial);

        // Simple face marks on the forward (+Z) side help the silhouette read from the game camera.
        CreateVisualPrimitive(
            PrimitiveType.Sphere, "Eye_L", visual.transform,
            new Vector3(-0.075f, 0.91f, 0.148f), new Vector3(0.045f, 0.045f, 0.025f), detailMaterial);
        CreateVisualPrimitive(
            PrimitiveType.Sphere, "Eye_R", visual.transform,
            new Vector3(0.075f, 0.91f, 0.148f), new Vector3(0.045f, 0.045f, 0.025f), detailMaterial);

        Transform leftArm = CreateLimbPivot("LeftArmPivot", visual.transform, new Vector3(-0.38f, 0.53f, 0f));
        CreateVisualPrimitive(
            PrimitiveType.Capsule, "LeftArm", leftArm,
            new Vector3(0f, -0.25f, 0f), new Vector3(0.13f, 0.28f, 0.13f), armorMaterial);

        Transform rightArm = CreateLimbPivot("RightArmPivot", visual.transform, new Vector3(0.38f, 0.53f, 0f));
        CreateVisualPrimitive(
            PrimitiveType.Capsule, "RightArm", rightArm,
            new Vector3(0f, -0.25f, 0f), new Vector3(0.13f, 0.28f, 0.13f), armorMaterial);

        Transform leftLeg = CreateLimbPivot("LeftLegPivot", visual.transform, new Vector3(-0.17f, -0.25f, 0f));
        CreateVisualPrimitive(
            PrimitiveType.Capsule, "LeftLeg", leftLeg,
            new Vector3(0f, -0.35f, 0f), new Vector3(0.16f, 0.39f, 0.16f), armorMaterial);

        Transform rightLeg = CreateLimbPivot("RightLegPivot", visual.transform, new Vector3(0.17f, -0.25f, 0f));
        CreateVisualPrimitive(
            PrimitiveType.Capsule, "RightLeg", rightLeg,
            new Vector3(0f, -0.35f, 0f), new Vector3(0.16f, 0.39f, 0.16f), armorMaterial);

        PlayerLocomotionAnimator locomotion = player.GetComponent<PlayerLocomotionAnimator>();
        if (locomotion == null)
            locomotion = player.AddComponent<PlayerLocomotionAnimator>();
        locomotion.ConfigureRig(visual.transform, torso, head, leftArm, rightArm, leftLeg, rightLeg);
    }

    private static Transform CreateLimbPivot(string objectName, Transform parent, Vector3 localPosition)
    {
        GameObject pivot = new GameObject(objectName);
        pivot.transform.SetParent(parent, false);
        pivot.transform.localPosition = localPosition;
        pivot.transform.localRotation = Quaternion.identity;
        return pivot.transform;
    }

    private static Transform CreateVisualPrimitive(
        PrimitiveType type, string objectName, Transform parent,
        Vector3 localPosition, Vector3 localScale, Material material)
    {
        GameObject visual = GameObject.CreatePrimitive(type);
        visual.name = objectName;
        visual.transform.SetParent(parent, false);
        visual.transform.localPosition = localPosition;
        visual.transform.localRotation = Quaternion.identity;
        visual.transform.localScale = localScale;

        Renderer renderer = visual.GetComponent<Renderer>();
        if (renderer != null)
            renderer.sharedMaterial = material;

        Collider collider = visual.GetComponent<Collider>();
        if (collider != null)
            Object.DestroyImmediate(collider);

        return visual.transform;
    }

    private static Material FindOrCreateMaterialFromExisting(GameObject player, string path, Color fallbackColor)
    {
        Transform visualRoot = player.transform.Find("PlayerVisualRoot");
        Renderer renderer = visualRoot != null ? visualRoot.GetComponentInChildren<Renderer>() : player.GetComponentInChildren<Renderer>();
        if (renderer != null && renderer.sharedMaterial != null)
            return renderer.sharedMaterial;

        return CreateOrLoadMaterial(path, fallbackColor);
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
