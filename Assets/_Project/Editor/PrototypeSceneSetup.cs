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

    [MenuItem("Tools/Code Lyoko/Create Prototype Scene", true)]
    private static bool ValidateCreatePrototypeScene()
    {
        return CanRunEditorSceneOperation();
    }

    [MenuItem("Tools/Code Lyoko/Create Prototype Scene")]
    public static void CreatePrototypeScene()
    {
        if (!CanRunEditorSceneOperation())
            return;
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

    [MenuItem("Tools/Code Lyoko/Upgrade Player Locomotion Placeholder", true)]
    private static bool ValidateUpgradePlayerLocomotionPlaceholder()
    {
        return CanRunEditorSceneOperation();
    }

    [MenuItem("Tools/Code Lyoko/Upgrade Player Locomotion Placeholder")]
    public static void UpgradePlayerLocomotionPlaceholder()
    {
        if (!CanRunEditorSceneOperation())
            return;
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

    [MenuItem("Tools/Code Lyoko/Improve Prototype Arena Visibility", true)]
    private static bool ValidateImprovePrototypeArenaVisibility()
    {
        return CanRunEditorSceneOperation();
    }

    [MenuItem("Tools/Code Lyoko/Improve Prototype Arena Visibility")]
    public static void ImprovePrototypeArenaVisibility()
    {
        if (!CanRunEditorSceneOperation())
            return;
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

        EnsureFolder("Assets", "_Project");
        EnsureFolder(Root, "Materials");

        Material ground = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeGround.mat", new Color(0.115f, 0.145f, 0.16f));
        Material wall = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeWalls.mat", new Color(0.30f, 0.19f, 0.12f));
        Material grid = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeGrid.mat", new Color(0.27f, 0.31f, 0.32f));
        Material boundary = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeBoundary.mat", new Color(0.72f, 0.36f, 0.12f));

        GameObject floor = GameObject.Find("TestFloor");
        if (floor != null)
        {
            floor.transform.position = Vector3.zero;
            floor.transform.localScale = new Vector3(1.8f, 1f, 1.8f);
            Renderer renderer = floor.GetComponent<Renderer>();
            if (renderer != null)
                renderer.sharedMaterial = ground;
        }

        const float halfExtent = 9f;
        const float wallHeight = 2.8f;
        const float wallThickness = 0.8f;
        SetWall("Wall_North", new Vector3(0f, wallHeight / 2f, halfExtent),
            new Vector3(halfExtent * 2f, wallHeight, wallThickness), wall);
        SetWall("Wall_South", new Vector3(0f, wallHeight / 2f, -halfExtent),
            new Vector3(halfExtent * 2f, wallHeight, wallThickness), wall);
        SetWall("Wall_East", new Vector3(halfExtent, wallHeight / 2f, 0f),
            new Vector3(wallThickness, wallHeight, halfExtent * 2f), wall);
        SetWall("Wall_West", new Vector3(-halfExtent, wallHeight / 2f, 0f),
            new Vector3(wallThickness, wallHeight, halfExtent * 2f), wall);

        GameObject oldGrid = GameObject.Find("ArenaGrid");
        if (oldGrid != null)
            Object.DestroyImmediate(oldGrid);

        GameObject gridRoot = new GameObject("ArenaGrid");
        // Draw subtle floor divisions to make camera/player movement perceptible.
        for (int coordinate = -6; coordinate <= 6; coordinate += 3)
        {
            CreateStrip(gridRoot.transform, "Grid_X_" + coordinate,
                new Vector3(0f, 0.018f, coordinate), new Vector3(17.0f, 0.018f, 0.035f), grid);
            CreateStrip(gridRoot.transform, "Grid_Z_" + coordinate,
                new Vector3(coordinate, 0.019f, 0f), new Vector3(0.035f, 0.018f, 17.0f), grid);
        }

        // Warm inner boundary markings help distinguish the playable area from the walls.
        const float line = 8.25f;
        const float boundaryLength = 16.5f;
        CreateStrip(gridRoot.transform, "Boundary_North",
            new Vector3(0f, 0.03f, line), new Vector3(boundaryLength, 0.025f, 0.10f), boundary);
        CreateStrip(gridRoot.transform, "Boundary_South",
            new Vector3(0f, 0.03f, -line), new Vector3(boundaryLength, 0.025f, 0.10f), boundary);
        CreateStrip(gridRoot.transform, "Boundary_East",
            new Vector3(line, 0.03f, 0f), new Vector3(0.10f, 0.025f, boundaryLength), boundary);
        CreateStrip(gridRoot.transform, "Boundary_West",
            new Vector3(-line, 0.03f, 0f), new Vector3(0.10f, 0.025f, boundaryLength), boundary);

        Camera camera = Camera.main;
        if (camera == null)
        {
            GameObject cameraObject = GameObject.Find("IsometricCamera");
            if (cameraObject != null)
                camera = cameraObject.GetComponent<Camera>();
        }

        if (camera != null)
        {
            camera.orthographic = true;
            camera.orthographicSize = 8.3f;
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.035f, 0.045f, 0.055f);
            camera.transform.position = player.transform.position + new Vector3(0f, 10f, -10f);
            camera.transform.rotation = Quaternion.Euler(45f, 0f, 0f);

            IsometricCameraFollow follow = camera.GetComponent<IsometricCameraFollow>();
            if (follow != null)
            {
                SerializedObject serializedFollow = new SerializedObject(follow);
                SerializedProperty offset = serializedFollow.FindProperty("offset");
                SerializedProperty pitch = serializedFollow.FindProperty("pitch");
                SerializedProperty size = serializedFollow.FindProperty("orthographicSize");
                if (offset != null) offset.vector3Value = new Vector3(0f, 10f, -10f);
                if (pitch != null) pitch.floatValue = 45f;
                if (size != null) size.floatValue = 8.3f;
                serializedFollow.ApplyModifiedPropertiesWithoutUndo();
                follow.Target = player.transform;
            }
        }

        PlayerLocomotionAnimator locomotion = player.GetComponent<PlayerLocomotionAnimator>();
        if (locomotion != null)
        {
            SerializedObject serializedLocomotion = new SerializedObject(locomotion);
            SetFloat(serializedLocomotion, "walkCyclesPerSecond", 2.0f);
            SetFloat(serializedLocomotion, "runCyclesPerSecond", 3.1f);
            SetFloat(serializedLocomotion, "walkLegSwing", 46f);
            SetFloat(serializedLocomotion, "runLegSwing", 62f);
            SetFloat(serializedLocomotion, "walkLean", 8f);
            SetFloat(serializedLocomotion, "runLean", 15f);
            SetFloat(serializedLocomotion, "walkBounceHeight", 0.08f);
            SetFloat(serializedLocomotion, "runBounceHeight", 0.15f);
            SetFloat(serializedLocomotion, "stateBlendSpeed", 10f);
            serializedLocomotion.ApplyModifiedPropertiesWithoutUndo();
        }

        EditorSceneManager.MarkSceneDirty(SceneManager.GetActiveScene());
        EditorSceneManager.SaveScene(SceneManager.GetActiveScene());
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();

        EditorUtility.DisplayDialog(
            "Prototype Arena Improved",
            "Updated the arena framing, contrast, floor grid and boundary markings. Increased walk/run motion for easier visual testing.\n\n" +
            "Press Play, move with WASD or arrow keys, then hold Shift to run.",
            "OK");
    }

    private static bool CanRunEditorSceneOperation()
    {
        // These commands create/delete objects and write scene/assets; Unity forbids that while playing.
        return !EditorApplication.isPlayingOrWillChangePlaymode && !EditorApplication.isCompiling;
    }

    private static void SetFloat(SerializedObject serializedObject, string propertyName, float value)
    {
        SerializedProperty property = serializedObject.FindProperty(propertyName);
        if (property != null)
            property.floatValue = value;
    }

    private static void SetWall(string objectName, Vector3 position, Vector3 scale, Material material)
    {
        GameObject wall = GameObject.Find(objectName);
        if (wall == null)
        {
            wall = GameObject.CreatePrimitive(PrimitiveType.Cube);
            wall.name = objectName;
        }

        wall.transform.position = position;
        wall.transform.localScale = scale;
        Renderer renderer = wall.GetComponent<Renderer>();
        if (renderer != null)
            renderer.sharedMaterial = material;
    }

    private static void CreateStrip(
        Transform parent, string objectName, Vector3 position, Vector3 scale, Material material)
    {
        GameObject strip = GameObject.CreatePrimitive(PrimitiveType.Cube);
        strip.name = objectName;
        strip.transform.SetParent(parent, false);
        strip.transform.localPosition = position;
        strip.transform.localScale = scale;
        Renderer renderer = strip.GetComponent<Renderer>();
        if (renderer != null)
            renderer.sharedMaterial = material;

        Collider collider = strip.GetComponent<Collider>();
        if (collider != null)
            Object.DestroyImmediate(collider);
    }

    [MenuItem("Tools/Code Lyoko/Repair Prototype Materials", true)]
    private static bool ValidateRepairPrototypeMaterials()
    {
        return !EditorApplication.isPlayingOrWillChangePlaymode && !EditorApplication.isCompiling;
    }

    [MenuItem("Tools/Code Lyoko/Repair Prototype Materials")]
    public static void RepairPrototypeMaterials()
    {
        if (EditorApplication.isPlayingOrWillChangePlaymode || EditorApplication.isCompiling)
            return;

        EnsureFolder("Assets", "_Project");
        EnsureFolder(Root, "Materials");

        Material ground = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeGround.mat", new Color(0.115f, 0.145f, 0.16f));
        Material wall = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeWalls.mat", new Color(0.30f, 0.19f, 0.12f));
        Material player = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypePlayer.mat", new Color(0.55f, 0.20f, 0.075f));
        Material armor = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeArmor.mat", new Color(0.13f, 0.09f, 0.075f));
        Material skin = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeSkin.mat", new Color(0.62f, 0.43f, 0.29f));
        Material details = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeDetails.mat", new Color(0.035f, 0.025f, 0.02f));
        Material enemy = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeEnemy.mat", new Color(0.48f, 0.075f, 0.055f));
        Material enemyDetails = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeEnemyDetails.mat", new Color(1f, 0.48f, 0.08f));
        Material grid = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeGrid.mat", new Color(0.20f, 0.27f, 0.29f));
        Material boundary = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeBoundary.mat", new Color(0.90f, 0.40f, 0.10f));

        AssignMaterial("TestFloor", ground);
        AssignMaterial("Wall_North", wall);
        AssignMaterial("Wall_South", wall);
        AssignMaterial("Wall_East", wall);
        AssignMaterial("Wall_West", wall);

        GameObject gridRoot = GameObject.Find("ArenaGrid");
        if (gridRoot != null)
        {
            foreach (Renderer renderer in gridRoot.GetComponentsInChildren<Renderer>())
            {
                if (renderer.gameObject.name.StartsWith("Boundary_"))
                    renderer.sharedMaterial = boundary;
                else
                    renderer.sharedMaterial = grid;
                EditorUtility.SetDirty(renderer);
            }
        }

        GameObject playerObject = GameObject.FindGameObjectWithTag("Player");
        if (playerObject == null)
            playerObject = GameObject.Find("Player");
        if (playerObject != null)
        {
            foreach (Renderer renderer in playerObject.GetComponentsInChildren<Renderer>(true))
            {
                string objectName = renderer.gameObject.name;
                if (objectName == "Head")
                    renderer.sharedMaterial = skin;
                else if (objectName.StartsWith("Eye_"))
                    renderer.sharedMaterial = details;
                else if (objectName.Contains("Arm") || objectName.Contains("Leg") || objectName == "Belt")
                    renderer.sharedMaterial = armor;
                else if (objectName == "Torso" || objectName == "Player" || objectName == "Capsule")
                    renderer.sharedMaterial = player;
                EditorUtility.SetDirty(renderer);
            }
        }

        GameObject enemyObject = GameObject.Find("TrainingEnemy");
        if (enemyObject != null)
        {
            foreach (Renderer renderer in enemyObject.GetComponentsInChildren<Renderer>(true))
            {
                if (renderer.gameObject.name.StartsWith("Eye_"))
                    renderer.sharedMaterial = enemyDetails;
                else
                    renderer.sharedMaterial = enemy;
                EditorUtility.SetDirty(renderer);
            }
        }

        Camera camera = Camera.main;
        if (camera != null)
        {
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.035f, 0.045f, 0.055f);
        }

        Scene scene = SceneManager.GetActiveScene();
        EditorSceneManager.MarkSceneDirty(scene);
        if (!string.IsNullOrEmpty(scene.path))
            EditorSceneManager.SaveScene(scene);
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();

        EditorUtility.DisplayDialog(
            "Prototype Materials Repaired",
            "Reassigned supported URP materials to the floor, walls, mannequin, enemy and grid.\n\n" +
            "Magenta error-shader visuals should now be replaced by the intended prototype colors. Press Play to check.",
            "OK");
    }

    private static void AssignMaterial(string objectName, Material material)
    {
        GameObject target = GameObject.Find(objectName);
        if (target == null)
            return;

        Renderer renderer = target.GetComponent<Renderer>();
        if (renderer != null)
        {
            renderer.sharedMaterial = material;
            EditorUtility.SetDirty(renderer);
        }
    }

    [MenuItem("Tools/Code Lyoko/Setup Combat Prototype", true)]
    private static bool ValidateSetupCombatPrototype()
    {
        return !EditorApplication.isPlayingOrWillChangePlaymode && !EditorApplication.isCompiling;
    }

    [MenuItem("Tools/Code Lyoko/Setup Combat Prototype")]
    public static void SetupCombatPrototype()
    {
        if (EditorApplication.isPlayingOrWillChangePlaymode || EditorApplication.isCompiling)
            return;

        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player == null)
            player = GameObject.Find("Player");

        if (player == null)
        {
            EditorUtility.DisplayDialog("Player Not Found",
                "Open Prototype_Scene.unity first, then run this command again.", "OK");
            return;
        }

        EnsureFolder("Assets", "_Project");
        EnsureFolder(Root, "Materials");

        Material enemyMaterial = CreateOrLoadMaterial(
            MaterialsFolder + "/PrototypeEnemy.mat", new Color(0.55f, 0.12f, 0.085f));

        CombatHealth playerHealth = player.GetComponent<CombatHealth>();
        if (playerHealth == null)
            playerHealth = player.AddComponent<CombatHealth>();
        if (player.GetComponent<CombatHitFeedback>() == null)
            player.AddComponent<CombatHitFeedback>();

        PlayerMeleeCombat combat = player.GetComponent<PlayerMeleeCombat>();
        if (combat == null)
            combat = player.AddComponent<PlayerMeleeCombat>();

        CombatTestHUD hud = player.GetComponent<CombatTestHUD>();
        if (hud == null)
            hud = player.AddComponent<CombatTestHUD>();

        GameObject enemy = GameObject.Find("TrainingEnemy");
        if (enemy == null)
        {
            enemy = new GameObject("TrainingEnemy");
            enemy.transform.position = player.transform.position + new Vector3(0f, 0f, 5.5f);
            enemy.transform.rotation = Quaternion.identity;

            CharacterController enemyController = enemy.AddComponent<CharacterController>();
            enemyController.height = 2f;
            enemyController.radius = 0.42f;
            enemyController.center = Vector3.zero;
            enemyController.stepOffset = 0.25f;
            enemyController.slopeLimit = 45f;

            GameObject enemyVisual = GameObject.CreatePrimitive(PrimitiveType.Capsule);
            enemyVisual.name = "EnemyVisual";
            enemyVisual.transform.SetParent(enemy.transform, false);
            enemyVisual.transform.localPosition = Vector3.zero;
            enemyVisual.transform.localRotation = Quaternion.identity;
            enemyVisual.transform.localScale = new Vector3(0.88f, 0.95f, 0.88f);
            Renderer enemyRenderer = enemyVisual.GetComponent<Renderer>();
            if (enemyRenderer != null)
                enemyRenderer.sharedMaterial = enemyMaterial;
            Collider enemyCollider = enemyVisual.GetComponent<Collider>();
            if (enemyCollider != null)
                Object.DestroyImmediate(enemyCollider);

            // Distinctive, simple eyes help identify the enemy in the elevated camera.
            Material eyeMaterial = CreateOrLoadMaterial(
                MaterialsFolder + "/PrototypeEnemyDetails.mat", new Color(0.95f, 0.56f, 0.16f));
            CreateEnemyEye(enemyVisual.transform, "Eye_L", new Vector3(-0.095f, 0.48f, 0.265f), eyeMaterial);
            CreateEnemyEye(enemyVisual.transform, "Eye_R", new Vector3(0.095f, 0.48f, 0.265f), eyeMaterial);
        }

        CombatHealth enemyHealth = enemy.GetComponent<CombatHealth>();
        if (enemyHealth == null)
            enemyHealth = enemy.AddComponent<CombatHealth>();
        if (enemy.GetComponent<CombatHitFeedback>() == null)
            enemy.AddComponent<CombatHitFeedback>();
        TrainingEnemyAI enemyAI = enemy.GetComponent<TrainingEnemyAI>();
        if (enemyAI == null)
            enemyAI = enemy.AddComponent<TrainingEnemyAI>();
        enemyAI.SetTarget(player.transform);

        Scene scene = SceneManager.GetActiveScene();
        EditorSceneManager.MarkSceneDirty(scene);
        if (!string.IsNullOrEmpty(scene.path))
            EditorSceneManager.SaveScene(scene);

        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();

        EditorUtility.DisplayDialog(
            "Combat Prototype Ready",
            "Added player health, melee attack, dodge, an enemy that approaches and telegraphs attacks, and a combat HUD.\n\n" +
            "Play: J or left-click = attack; Space = dodge; WASD/arrows = move; hold Shift = run.\n" +
            "Defeat the training enemy by attacking it, and dodge its telegraphed strikes.",
            "OK");
    }

    private static void CreateEnemyEye(Transform parent, string objectName, Vector3 localPosition, Material material)
    {
        GameObject eye = GameObject.CreatePrimitive(PrimitiveType.Sphere);
        eye.name = objectName;
        eye.transform.SetParent(parent, false);
        eye.transform.localPosition = localPosition;
        eye.transform.localScale = new Vector3(0.065f, 0.065f, 0.035f);
        Renderer renderer = eye.GetComponent<Renderer>();
        if (renderer != null)
            renderer.sharedMaterial = material;
        Collider collider = eye.GetComponent<Collider>();
        if (collider != null)
            Object.DestroyImmediate(collider);
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
        Shader shader = FindPrototypeShader();
        Material existing = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (existing != null)
        {
            // Old prototype materials may have retained an unsupported shader, which renders magenta.
            if (shader != null &&
                (existing.shader == null ||
                 existing.shader.name == "Hidden/InternalErrorShader" ||
                 !existing.shader.isSupported ||
                 (shader.name.StartsWith("Universal Render Pipeline/") &&
                  !existing.shader.name.StartsWith("Universal Render Pipeline/"))))
            {
                existing.shader = shader;
            }

            SetMaterialColor(existing, color);
            EditorUtility.SetDirty(existing);
            return existing;
        }

        if (shader == null)
        {
            Debug.LogWarning("No supported shader was found. Check that Universal Render Pipeline is installed and active.");
            return null;
        }

        Material material = new Material(shader);
        SetMaterialColor(material, color);
        AssetDatabase.CreateAsset(material, path);
        return material;
    }

    private static Shader FindPrototypeShader()
    {
        string[] candidates =
        {
            "Universal Render Pipeline/Lit",
            "Universal Render Pipeline/Simple Lit",
            "Universal Render Pipeline/Unlit",
            "Standard"
        };

        foreach (string candidate in candidates)
        {
            Shader shader = Shader.Find(candidate);
            if (shader != null && shader.isSupported)
                return shader;
        }

        return null;
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
