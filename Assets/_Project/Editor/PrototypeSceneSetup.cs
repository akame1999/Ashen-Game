#if UNITY_EDITOR
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// Creates a disposable greybox scene for the first movement milestone.
/// Menu: Tools > Code Lyoko > Create Prototype Scene.
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

        GameObject player = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        player.name = "Player";
        player.tag = "Player";
        player.transform.position = new Vector3(0f, 1f, 0f);
        player.GetComponent<Renderer>().sharedMaterial = playerMaterial;
        Object.DestroyImmediate(player.GetComponent<CapsuleCollider>());

        CharacterController controller = player.AddComponent<CharacterController>();
        controller.height = 2f;
        controller.radius = 0.45f;
        controller.center = Vector3.zero;
        controller.stepOffset = 0.3f;
        controller.slopeLimit = 45f;

        player.AddComponent<IsometricPlayerController>();

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
                  ". Press Play and move with WASD or the arrow keys.");
        EditorUtility.DisplayDialog(
            "Prototype Scene Created",
            "Created a greybox arena with a player capsule, camera-follow, perimeter walls and lighting.\n\n" +
            "Open the Game tab and press Play. Move with WASD or the arrow keys.",
            "OK");
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
