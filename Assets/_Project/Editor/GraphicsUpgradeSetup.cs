#if UNITY_EDITOR
using System;
using System.Collections;
using System.Collections.Generic;
using System.Reflection;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

public static class GraphicsUpgradeSetup
{
    private const string GraphicsPath = "Assets/_Project/Graphics";
    private const string MaterialsPath = GraphicsPath + "/Materials";
    private const string ProfilePath = GraphicsPath + "/Profiles/DarkFantasyPrototype.asset";
    private const string RootName = "GraphicsPassRoot";

    [MenuItem("Tools/Code Lyoko/Graphics/Apply Dark Fantasy Graphics Pass", true)]
    private static bool CanApply() => CanEdit();

    [MenuItem("Tools/Code Lyoko/Graphics/Apply Dark Fantasy Graphics Pass")]
    public static void Apply()
    {
        if (!CanEdit()) return;
        EnsureFolder("Assets", "_Project");
        EnsureFolder("Assets/_Project", "Graphics");
        EnsureFolder(GraphicsPath, "Materials");
        EnsureFolder(GraphicsPath, "Profiles");

        Material grout = Mat("Stone_Grout.mat", new Color(.035f, .043f, .052f));
        Material stoneA = Mat("Stone_Paving_A.mat", new Color(.19f, .205f, .22f));
        Material stoneB = Mat("Stone_Paving_B.mat", new Color(.225f, .225f, .235f));
        Material stoneC = Mat("Stone_Paving_C.mat", new Color(.145f, .16f, .18f));
        Material wall = Mat("Stone_RuinedWall.mat", new Color(.105f, .082f, .073f));
        Material trim = Mat("Stone_AgedTrim.mat", new Color(.30f, .205f, .12f));
        Material iron = Mat("Iron_Brazier.mat", new Color(.045f, .055f, .065f));
        Material rubbleA = Mat("Stone_Rubble_A.mat", new Color(.12f, .13f, .14f));
        Material rubbleB = Mat("Stone_Rubble_B.mat", new Color(.18f, .16f, .14f));
        Material rune = Mat("Rune_SpectralBlue.mat", new Color(.055f, .35f, .48f), new Color(.035f, .24f, .45f));
        Material flame = Mat("Flame_Amber.mat", new Color(1f, .22f, .035f), new Color(1f, .15f, .02f));

        Assign("TestFloor", grout);
        foreach (string n in new[] { "Wall_North", "Wall_South", "Wall_East", "Wall_West" }) Assign(n, wall);
        GameObject oldGrid = GameObject.Find("ArenaGrid");
        if (oldGrid != null) oldGrid.SetActive(false);
        GameObject previous = GameObject.Find(RootName);
        if (previous != null) DestroyImmediate(previous);

        GameObject root = new GameObject(RootName);
        BuildPaving(root.transform, stoneA, stoneB, stoneC, grout);
        BuildTrim(root.transform, trim);
        BuildPillars(root.transform, wall, trim);
        BuildBraziers(root.transform, iron, trim, flame);
        BuildRubble(root.transform, rubbleA, rubbleB);
        BuildRune(root.transform, rune);
        Lighting();
        CameraSetup();
        bool fx = PostFX(root);

        Scene scene = SceneManager.GetActiveScene();
        EditorSceneManager.MarkSceneDirty(scene);
        if (!string.IsNullOrEmpty(scene.path)) EditorSceneManager.SaveScene(scene);
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        Debug.Log("[Graphics Pass] Renderers created: " + root.GetComponentsInChildren<Renderer>(true).Length +
                  "; optional post-processing " + (fx ? "configured." : "unavailable; lighting/material changes applied."));
        EditorUtility.DisplayDialog("Dark-Fantasy Graphics Pass Applied",
            "Added stone paving, seams/cracks, ruined corner pillars, four braziers and warm lights, edge rubble, a spectral rune, darker lighting and fog.\n\n" +
            (fx ? "Configured optional URP bloom, vignette and color grading." : "URP post-processing was unavailable; the base graphics pass still applied.") +
            "\n\nPress Play to inspect the result. Props are procedural placeholders; replace them with final art later.", "OK");
    }

    [MenuItem("Tools/Code Lyoko/Graphics/Validate Graphics Pass", true)]
    private static bool CanValidate() => CanEdit();

    [MenuItem("Tools/Code Lyoko/Graphics/Validate Graphics Pass")]
    public static void Validate()
    {
        if (!CanEdit()) return;
        var ok = new List<string>();
        var bad = new List<string>();
        GameObject root = GameObject.Find(RootName);
        if (root == null) bad.Add("GraphicsPassRoot missing; run Apply Dark Fantasy Graphics Pass.");
        else
        {
            ok.Add("GraphicsPassRoot exists.");
            Count(root.transform, "FloorTile_", 49, "paving tiles", ok, bad);
            Count(root.transform, "RuinedPillar_", 4, "ruined pillar parts", ok, bad);
            Count(root.transform, "Brazier_", 4, "brazier parts", ok, bad);
            if (root.GetComponentInChildren<LineRenderer>(true) != null) ok.Add("Central rune exists.");
            else bad.Add("Central rune missing.");
        }
        GameObject floor = GameObject.Find("TestFloor");
        if (floor != null && floor.GetComponent<Collider>() != null) ok.Add("Original floor collider preserved.");
        else bad.Add("Original floor collider missing.");
        foreach (string n in new[] { "Wall_North", "Wall_South", "Wall_East", "Wall_West" })
        {
            GameObject wall = GameObject.Find(n);
            if (wall != null && wall.GetComponent<Collider>() != null) ok.Add(n + " collision preserved.");
            else bad.Add(n + " collider missing.");
        }
        if (Camera.main != null && Camera.main.orthographic) ok.Add("Orthographic Main Camera found.");
        else bad.Add("Main Camera missing or not orthographic.");
        foreach (string s in ok) Debug.Log("[Graphics PASS] " + s);
        foreach (string s in bad) Debug.LogError("[Graphics CHECK] " + s);
        EditorUtility.DisplayDialog("Graphics Pass Validation",
            "Checks passed: " + ok.Count + "\nChecks needing attention: " + bad.Count +
            "\n\nRead [Graphics PASS] / [Graphics CHECK] in Console. This is structural validation, not a quality/performance test.", "OK");
    }

    private static void BuildPaving(Transform root, Material a, Material b, Material c, Material grout)
    {
        const float spacing = 2.38f, slab = 2.28f;
        Material[] mats = { a, b, c };
        var rng = new System.Random(8317);
        for (int x = 0; x < 7; x++)
        for (int z = 0; z < 7; z++)
        {
            float px = (x - 3) * spacing, pz = (z - 3) * spacing;
            Create(root, "FloorTile_" + x + "_" + z, PrimitiveType.Cube,
                new Vector3(px, .025f, pz), new Vector3(slab, .075f + (float)rng.NextDouble() * .025f, slab),
                mats[(x * 3 + z * 5 + rng.Next(0, 3)) % mats.Length],
                new Vector3(0f, rng.Next(0, 4) * 90f, 0f));
        }
        for (int i = -3; i <= 3; i++)
        {
            float p = i * spacing;
            Create(root, "Grout_X_" + i, PrimitiveType.Cube, new Vector3(p, .062f, 0f), new Vector3(.035f, .006f, 16.55f), grout);
            Create(root, "Grout_Z_" + i, PrimitiveType.Cube, new Vector3(0f, .063f, p), new Vector3(16.55f, .006f, .035f), grout);
        }
        for (int i = 0; i < 17; i++)
        {
            float px = -6.6f + (float)rng.NextDouble() * 13.2f;
            float pz = -6.6f + (float)rng.NextDouble() * 13.2f;
            if (px * px + pz * pz < 3f) px += px >= 0f ? 2f : -2f;
            Create(root, "StoneCrack_" + i, PrimitiveType.Cube, new Vector3(px, .078f, pz),
                new Vector3(.20f + (float)rng.NextDouble() * .5f, .007f, .018f), grout,
                new Vector3(0f, (float)rng.NextDouble() * 180f, 0f));
        }
    }

    private static void BuildTrim(Transform root, Material mat)
    {
        const float edge = 8.45f, length = 16.8f;
        Create(root, "PerimeterTrim_N", PrimitiveType.Cube, new Vector3(0f, .085f, edge), new Vector3(length, .09f, .16f), mat);
        Create(root, "PerimeterTrim_S", PrimitiveType.Cube, new Vector3(0f, .085f, -edge), new Vector3(length, .09f, .16f), mat);
        Create(root, "PerimeterTrim_E", PrimitiveType.Cube, new Vector3(edge, .085f, 0f), new Vector3(.16f, .09f, length), mat);
        Create(root, "PerimeterTrim_W", PrimitiveType.Cube, new Vector3(-edge, .085f, 0f), new Vector3(.16f, .09f, length), mat);
    }

    private static void BuildPillars(Transform root, Material stone, Material trim)
    {
        foreach (float x in new[] { -7.75f, 7.75f })
        foreach (float z in new[] { -7.75f, 7.75f })
        {
            string id = (x < 0f ? "W" : "E") + (z < 0f ? "S" : "N");
            Create(root, "RuinedPillar_" + id + "_Base", PrimitiveType.Cube, new Vector3(x, .25f, z), new Vector3(1.18f, .46f, 1.18f), trim);
            Create(root, "RuinedPillar_" + id + "_Shaft", PrimitiveType.Cube, new Vector3(x, 1.48f, z), new Vector3(.78f, 2.10f, .78f), stone);
            Create(root, "RuinedPillar_" + id + "_Band", PrimitiveType.Cube, new Vector3(x, .72f, z), new Vector3(.91f, .20f, .91f), trim);
            Create(root, "RuinedPillar_" + id + "_Capital", PrimitiveType.Cube, new Vector3(x, 2.62f, z), new Vector3(1.10f, .28f, 1.10f), trim);
            Create(root, "RuinedPillar_" + id + "_BrokenTop", PrimitiveType.Cube,
                new Vector3(x + (x < 0f ? .14f : -.12f), 2.88f, z - .08f), new Vector3(.74f, .15f, .86f),
                stone, new Vector3(0f, 0f, x < 0f ? 8f : -6f));
        }
    }

    private static void BuildBraziers(Transform root, Material iron, Material trim, Material flame)
    {
        Vector3[] positions = { new Vector3(0f, 0f, -7.75f), new Vector3(0f, 0f, 7.75f),
            new Vector3(-7.75f, 0f, 0f), new Vector3(7.75f, 0f, 0f) };
        for (int i = 0; i < positions.Length; i++)
        {
            Vector3 p = positions[i]; string id = "Brazier_" + i;
            Create(root, id + "_Base", PrimitiveType.Cube, p + Vector3.up * .20f, new Vector3(.58f, .40f, .58f), trim);
            Create(root, id + "_Stem", PrimitiveType.Cylinder, p + Vector3.up * .62f, new Vector3(.16f, .30f, .16f), iron);
            Create(root, id + "_Bowl", PrimitiveType.Sphere, p + Vector3.up * .98f, new Vector3(.38f, .19f, .38f), iron);
            Create(root, id + "_Flame", PrimitiveType.Sphere, p + Vector3.up * 1.20f, new Vector3(.16f, .27f, .16f), flame);
            GameObject go = new GameObject(id + "_Light"); go.transform.SetParent(root, false); go.transform.localPosition = p + Vector3.up * 1.35f;
            Light light = go.AddComponent<Light>(); light.type = LightType.Point; light.color = new Color(1f, .43f, .16f);
            light.intensity = 2f; light.range = 5.5f; light.shadows = LightShadows.None;
        }
    }

    private static void BuildRubble(Transform root, Material a, Material b)
    {
        var rng = new System.Random(9124);
        for (int i = 0; i < 22; i++)
        {
            double angle = rng.NextDouble() * Math.PI * 2.0;
            float radius = 6.8f + (float)rng.NextDouble();
            Vector3 p = new Vector3(Mathf.Cos((float)angle) * radius, .11f, Mathf.Sin((float)angle) * radius);
            Vector3 size = new Vector3(.14f + (float)rng.NextDouble() * .28f, .10f + (float)rng.NextDouble() * .17f,
                .13f + (float)rng.NextDouble() * .27f);
            Create(root, "Rubble_" + i, PrimitiveType.Sphere, p, size, i % 2 == 0 ? a : b,
                new Vector3((float)rng.NextDouble() * 30f, (float)rng.NextDouble() * 180f, (float)rng.NextDouble() * 30f));
        }
    }

    private static void BuildRune(Transform root, Material mat)
    {
        GameObject go = new GameObject("CentralSpectralRune"); go.transform.SetParent(root, false);
        go.transform.localPosition = new Vector3(0f, .09f, 0f);
        LineRenderer line = go.AddComponent<LineRenderer>();
        line.useWorldSpace = false; line.loop = true; line.positionCount = 65; line.startWidth = .035f; line.endWidth = .035f;
        line.numCapVertices = 2; line.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        line.receiveShadows = false; line.sharedMaterial = mat;
        for (int i = 0; i < 65; i++)
        {
            float angle = i / 64f * Mathf.PI * 2f;
            line.SetPosition(i, new Vector3(Mathf.Cos(angle) * 1.05f, 0f, Mathf.Sin(angle) * 1.05f));
        }
        for (int i = 0; i < 8; i++)
        {
            float angle = i * 45f; Vector3 p = Quaternion.Euler(0f, angle, 0f) * Vector3.forward * 1.23f;
            Create(root, "RuneMark_" + i, PrimitiveType.Cube, new Vector3(p.x, .09f, p.z),
                new Vector3(.12f, .025f, .035f), mat, new Vector3(0f, angle, 0f));
        }
        GameObject lightObject = new GameObject("Rune_FillLight");
        lightObject.transform.SetParent(root, false); lightObject.transform.localPosition = new Vector3(0f, .7f, 0f);
        Light spectral = lightObject.AddComponent<Light>(); spectral.type = LightType.Point; spectral.color = new Color(.12f, .42f, .8f);
        spectral.intensity = .7f; spectral.range = 4.2f; spectral.shadows = LightShadows.None;
    }

    private static void Lighting()
    {
        GameObject go = GameObject.Find("Directional Light");
        if (go == null) go = new GameObject("Directional Light");
        go.transform.rotation = Quaternion.Euler(48f, -34f, 0f);
        Light key = go.GetComponent<Light>(); if (key == null) key = go.AddComponent<Light>();
        key.type = LightType.Directional; key.color = new Color(.73f, .80f, 1f); key.intensity = 1.05f;
        key.shadows = LightShadows.Soft; key.shadowStrength = .78f; key.shadowBias = .05f; key.shadowNormalBias = .35f;
        RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Trilight;
        RenderSettings.ambientSkyColor = new Color(.16f, .20f, .28f);
        RenderSettings.ambientEquatorColor = new Color(.10f, .12f, .15f);
        RenderSettings.ambientGroundColor = new Color(.035f, .032f, .03f);
        RenderSettings.ambientIntensity = 1f; RenderSettings.reflectionIntensity = .42f;
        RenderSettings.fog = true; RenderSettings.fogMode = FogMode.Linear;
        RenderSettings.fogColor = new Color(.075f, .085f, .11f);
        RenderSettings.fogStartDistance = 16f; RenderSettings.fogEndDistance = 34f;
    }

    private static void CameraSetup()
    {
        Camera camera = Camera.main;
        if (camera == null) { GameObject go = GameObject.Find("IsometricCamera"); if (go != null) camera = go.GetComponent<Camera>(); }
        if (camera == null) { Debug.LogWarning("[Graphics Pass] Camera not found; skipped camera settings."); return; }
        camera.orthographic = true; camera.allowHDR = true; camera.allowMSAA = true;
        camera.backgroundColor = new Color(.035f, .045f, .065f); camera.clearFlags = CameraClearFlags.SolidColor;
    }

    // Optional post-processing is configured through reflection so the scene tool can still compile
    // if URP's optional volume types are unavailable while Package Manager is recovering.
    private static bool PostFX(GameObject root)
    {
        Type volumeType = FindType("UnityEngine.Rendering.Volume");
        Type profileType = FindType("UnityEngine.Rendering.VolumeProfile");
        if (volumeType == null || profileType == null) { Debug.LogWarning("[Graphics Pass] Volume API unavailable; using lighting-only pass."); return false; }

        ScriptableObject profile = AssetDatabase.LoadAssetAtPath<ScriptableObject>(ProfilePath);
        if (profile == null)
        {
            profile = ScriptableObject.CreateInstance(profileType) as ScriptableObject;
            if (profile == null) return false;
            profile.name = "DarkFantasyPrototype"; AssetDatabase.CreateAsset(profile, ProfilePath);
        }
        else
        {
            PropertyInfo prop = profileType.GetProperty("components");
            IList list = prop != null ? prop.GetValue(profile) as IList : null;
            if (list != null)
            {
                for (int i = list.Count - 1; i >= 0; i--)
                {
                    UnityEngine.Object obj = list[i] as UnityEngine.Object; list.RemoveAt(i);
                    if (obj != null) UnityEngine.Object.DestroyImmediate(obj, true);
                }
            }
        }

        bool added = false;
        added |= AddOverride(profile, profileType, "UnityEngine.Rendering.Universal.Bloom",
            new Dictionary<string, object> { { "intensity", .55f }, { "threshold", 1.15f }, { "scatter", .60f } });
        added |= AddOverride(profile, profileType, "UnityEngine.Rendering.Universal.Vignette",
            new Dictionary<string, object> { { "intensity", .23f }, { "smoothness", .60f }, { "roundness", .78f } });
        added |= AddOverride(profile, profileType, "UnityEngine.Rendering.Universal.ColorAdjustments",
            new Dictionary<string, object> { { "postExposure", -.12f }, { "contrast", 11f }, { "saturation", -12f } });
        if (!added) { Debug.LogWarning("[Graphics Pass] No URP overrides available; lighting-only pass applied."); AssetDatabase.SaveAssets(); return false; }

        Transform existing = root.transform.Find("GlobalVisualVolume");
        GameObject volumeGo = existing != null ? existing.gameObject : new GameObject("GlobalVisualVolume");
        if (volumeGo.transform.parent != root.transform) volumeGo.transform.SetParent(root.transform, false);
        Component volume = volumeGo.GetComponent(volumeType); if (volume == null) volume = volumeGo.AddComponent(volumeType);
        SetProp(volume, "isGlobal", true); SetProp(volume, "priority", 10f); SetProp(volume, "sharedProfile", profile);

        Camera camera = Camera.main;
        if (camera == null) { GameObject go = GameObject.Find("IsometricCamera"); if (go != null) camera = go.GetComponent<Camera>(); }
        Type cameraData = FindType("UnityEngine.Rendering.Universal.UniversalAdditionalCameraData");
        if (camera != null && cameraData != null)
        {
            Component data = camera.GetComponent(cameraData); if (data == null) data = camera.gameObject.AddComponent(cameraData);
            SetProp(data, "renderPostProcessing", true);
        }
        EditorUtility.SetDirty(profile); EditorUtility.SetDirty(volume); AssetDatabase.SaveAssets();
        return true;
    }

    private static bool AddOverride(ScriptableObject profile, Type profileType, string typeName, Dictionary<string, object> values)
    {
        Type type = FindType(typeName);
        if (type == null) { Debug.LogWarning("[Graphics Pass] Optional effect unavailable: " + typeName); return false; }
        MethodInfo add = profileType.GetMethod("Add", BindingFlags.Instance | BindingFlags.Public, null, new[] { typeof(Type), typeof(bool) }, null);
        if (add == null) return false;
        object component = add.Invoke(profile, new object[] { type, true }); if (component == null) return false;
        foreach (var item in values) SetParameter(component, item.Key, item.Value);
        EditorUtility.SetDirty((UnityEngine.Object)component); return true;
    }

    private static void SetParameter(object component, string name, object value)
    {
        Type type = component.GetType(); object parameter = null;
        FieldInfo field = type.GetField(name, BindingFlags.Instance | BindingFlags.Public);
        if (field != null) parameter = field.GetValue(component);
        if (parameter == null) { PropertyInfo p = type.GetProperty(name, BindingFlags.Instance | BindingFlags.Public); if (p != null) parameter = p.GetValue(component); }
        if (parameter == null) return;
        PropertyInfo state = parameter.GetType().GetProperty("overrideState");
        if (state != null && state.CanWrite) state.SetValue(parameter, true);
        PropertyInfo val = parameter.GetType().GetProperty("value");
        if (val != null && val.CanWrite) { try { val.SetValue(parameter, Convert.ChangeType(value, val.PropertyType)); } catch (Exception) { } }
    }

    private static void SetProp(object target, string name, object value)
    {
        if (target == null) return;
        PropertyInfo p = target.GetType().GetProperty(name, BindingFlags.Instance | BindingFlags.Public);
        if (p == null || !p.CanWrite) return;
        try { p.SetValue(target, value); } catch (Exception e) { Debug.LogWarning("[Graphics Pass] Could not set " + name + ": " + e.Message); }
    }

    private static Type FindType(string fullName)
    {
        Type t = Type.GetType(fullName + ", Unity.RenderPipelines.Core.Runtime", false) ??
                 Type.GetType(fullName + ", Unity.RenderPipelines.Universal.Runtime", false);
        if (t != null) return t;
        foreach (Assembly assembly in AppDomain.CurrentDomain.GetAssemblies()) { t = assembly.GetType(fullName, false); if (t != null) return t; }
        return null;
    }

    private static Material Mat(string filename, Color color, Color? emission = null)
    {
        string path = MaterialsPath + "/" + filename;
        Shader shader = SupportedShader();
        Material m = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (m == null)
        {
            if (shader == null) { Debug.LogError("[Graphics Pass] No supported shader for " + path); return null; }
            m = new Material(shader); m.name = System.IO.Path.GetFileNameWithoutExtension(filename); AssetDatabase.CreateAsset(m, path);
        }
        else if (shader != null && (m.shader == null || m.shader.name == "Hidden/InternalErrorShader" ||
                 !m.shader.isSupported || !m.shader.name.StartsWith("Universal Render Pipeline/"))) m.shader = shader;
        if (m.HasProperty("_BaseColor")) m.SetColor("_BaseColor", color);
        if (m.HasProperty("_Color")) m.SetColor("_Color", color);
        if (emission.HasValue && m.HasProperty("_EmissionColor")) { m.EnableKeyword("_EMISSION"); m.SetColor("_EmissionColor", emission.Value); }
        else if (m.HasProperty("_EmissionColor")) { m.DisableKeyword("_EMISSION"); m.SetColor("_EmissionColor", Color.black); }
        EditorUtility.SetDirty(m); return m;
    }

    private static Shader SupportedShader()
    {
        foreach (string n in new[] { "Universal Render Pipeline/Lit", "Universal Render Pipeline/Simple Lit", "Universal Render Pipeline/Unlit", "Standard" })
        { Shader s = Shader.Find(n); if (s != null && s.isSupported) return s; }
        return null;
    }

    private static void Assign(string name, Material mat)
    {
        if (mat == null) return; GameObject go = GameObject.Find(name); if (go == null) return;
        Renderer r = go.GetComponent<Renderer>(); if (r != null) { r.sharedMaterial = mat; EditorUtility.SetDirty(r); }
    }

    private static void Create(Transform root, string name, PrimitiveType primitive, Vector3 pos, Vector3 scale, Material mat, Vector3? rotation = null)
    {
        GameObject go = GameObject.CreatePrimitive(primitive); go.name = name; go.transform.SetParent(root, false);
        go.transform.localPosition = pos; go.transform.localRotation = Quaternion.Euler(rotation ?? Vector3.zero); go.transform.localScale = scale;
        Renderer r = go.GetComponent<Renderer>(); if (r != null && mat != null) r.sharedMaterial = mat;
        Collider c = go.GetComponent<Collider>(); if (c != null) UnityEngine.Object.DestroyImmediate(c);
    }

    private static void Count(Transform root, string prefix, int minimum, string label, List<string> ok, List<string> bad)
    {
        int n = 0; foreach (Transform child in root.GetComponentsInChildren<Transform>(true))
            if (child != root && child.name.StartsWith(prefix, StringComparison.Ordinal)) n++;
        if (n >= minimum) ok.Add(label + " found: " + n + "."); else bad.Add("Expected at least " + minimum + " " + label + "; found " + n + ".");
    }

    private static void EnsureFolder(string parent, string name)
    { string path = parent + "/" + name; if (!AssetDatabase.IsValidFolder(path)) AssetDatabase.CreateFolder(parent, name); }

    private static bool CanEdit() => !EditorApplication.isPlayingOrWillChangePlaymode && !EditorApplication.isCompiling;
}
#endif
