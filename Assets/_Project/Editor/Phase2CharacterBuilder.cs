#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.Animations;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

/// <summary>
/// Builds an original stylized skinned character, Generic Avatar, Animator Controller,
/// and authored Idle/Walk/Run/Attack clips. All assets are generated locally by Unity.
/// </summary>
public static class Phase2CharacterBuilder
{
    private const string Root = "Assets/_Project/Characters/VeyrWanderer";
    private const string MeshFolder = Root + "/Meshes";
    private const string MaterialsFolder = Root + "/Materials";
    private const string AnimationsFolder = Root + "/Animations";
    private const string PrefabFolder = Root + "/Prefabs";
    private const string PrefabPath = PrefabFolder + "/VeyrWanderer.prefab";
    private const string AvatarPath = Root + "/VeyrWandererAvatar.asset";
    private const string ControllerPath = AnimationsFolder + "/VeyrWanderer.controller";

    private const string HipsPath = "Armature/Root/Hips";
    private const string SpinePath = HipsPath + "/Spine";
    private const string ChestPath = SpinePath + "/Chest";
    private const string NeckPath = ChestPath + "/Neck";
    private const string HeadPath = NeckPath + "/Head";
    private const string LeftUpperArmPath = ChestPath + "/LeftUpperArm";
    private const string LeftLowerArmPath = LeftUpperArmPath + "/LeftLowerArm";
    private const string RightUpperArmPath = ChestPath + "/RightUpperArm";
    private const string RightLowerArmPath = RightUpperArmPath + "/RightLowerArm";
    private const string LeftUpperLegPath = HipsPath + "/LeftUpperLeg";
    private const string LeftLowerLegPath = LeftUpperLegPath + "/LeftLowerLeg";
    private const string RightUpperLegPath = HipsPath + "/RightUpperLeg";
    private const string RightLowerLegPath = RightUpperLegPath + "/RightLowerLeg";

    [MenuItem("Tools/Code Lyoko/Phase 2/Build Rigged Character and Animations", true)]
    private static bool ValidateBuild() => CanEdit();

    [MenuItem("Tools/Code Lyoko/Phase 2/Build Rigged Character and Animations")]
    public static void BuildRiggedCharacterAndAnimations()
    {
        if (!CanEdit()) return;
        EnsureFolders();

        Material armor = CreateMaterial(MaterialsFolder + "/Wanderer_Armor.mat", new Color(0.13f, 0.16f, 0.19f));
        Material cloth = CreateMaterial(MaterialsFolder + "/Wanderer_Cloak.mat", new Color(0.08f, 0.19f, 0.22f));
        Material leather = CreateMaterial(MaterialsFolder + "/Wanderer_Leather.mat", new Color(0.18f, 0.105f, 0.065f));
        Material skin = CreateMaterial(MaterialsFolder + "/Wanderer_Skin.mat", new Color(0.52f, 0.34f, 0.23f));
        Material brass = CreateMaterial(MaterialsFolder + "/Wanderer_Brass.mat", new Color(0.62f, 0.39f, 0.12f));
        Material dark = CreateMaterial(MaterialsFolder + "/Wanderer_Details.mat", new Color(0.025f, 0.032f, 0.04f));

        AnimationClip idle = CreateIdleClip();
        AnimationClip walk = CreateWalkClip();
        AnimationClip run = CreateRunClip();
        AnimationClip attack = CreateAttackClip();
        AnimatorController controller = CreateController(idle, walk, run, attack);

        GameObject character = new GameObject("VeyrWanderer");
        GameObject armature = new GameObject("Armature");
        armature.transform.SetParent(character.transform, false);

        // Bone positions are kept near the actual joint centres. Mesh-part positions below
        // are expressed in character space and converted into each bone's local space by AddPart.
        Transform rootBone = CreateBone("Root", armature.transform, Vector3.zero);
        Transform hips = CreateBone("Hips", rootBone, new Vector3(0f, 0.06f, 0f));
        Transform spine = CreateBone("Spine", hips, new Vector3(0f, 0.10f, 0f));
        Transform chest = CreateBone("Chest", spine, new Vector3(0f, 0.13f, 0f));
        Transform neck = CreateBone("Neck", chest, new Vector3(0f, 0.18f, 0f));
        Transform head = CreateBone("Head", neck, new Vector3(0f, 0.15f, 0f));

        Transform leftUpperArm = CreateBone("LeftUpperArm", chest, new Vector3(-0.24f, 0.11f, 0f));
        Transform leftLowerArm = CreateBone("LeftLowerArm", leftUpperArm, new Vector3(-0.06f, -0.22f, 0f));
        Transform leftHand = CreateBone("LeftHand", leftLowerArm, new Vector3(-0.04f, -0.20f, 0f));
        Transform rightUpperArm = CreateBone("RightUpperArm", chest, new Vector3(0.24f, 0.11f, 0f));
        Transform rightLowerArm = CreateBone("RightLowerArm", rightUpperArm, new Vector3(0.06f, -0.22f, 0f));
        Transform rightHand = CreateBone("RightHand", rightLowerArm, new Vector3(0.04f, -0.20f, 0f));

        Transform leftUpperLeg = CreateBone("LeftUpperLeg", hips, new Vector3(-0.12f, -0.14f, 0f));
        Transform leftLowerLeg = CreateBone("LeftLowerLeg", leftUpperLeg, new Vector3(0f, -0.35f, 0f));
        Transform leftFoot = CreateBone("LeftFoot", leftLowerLeg, new Vector3(0f, -0.32f, 0.06f));
        Transform rightUpperLeg = CreateBone("RightUpperLeg", hips, new Vector3(0.12f, -0.14f, 0f));
        Transform rightLowerLeg = CreateBone("RightLowerLeg", rightUpperLeg, new Vector3(0f, -0.35f, 0f));
        Transform rightFoot = CreateBone("RightFoot", rightLowerLeg, new Vector3(0f, -0.32f, 0.06f));

        // Core: overlapping volumes so seams are hidden from the elevated camera.
        AddPart(character, "Pelvis", PrimitiveType.Cube, hips, new Vector3(0f, 0.02f, 0f), new Vector3(0.34f, 0.20f, 0.24f), leather);
        AddPart(character, "Torso", PrimitiveType.Capsule, chest, new Vector3(0f, 0.28f, 0f), new Vector3(0.34f, 0.23f, 0.23f), cloth);
        AddPart(character, "Breastplate", PrimitiveType.Cube, chest, new Vector3(0f, 0.29f, 0.045f), new Vector3(0.33f, 0.25f, 0.235f), armor);
        AddPart(character, "ChestTrim", PrimitiveType.Cube, chest, new Vector3(0f, 0.29f, 0.17f), new Vector3(0.055f, 0.23f, 0.025f), brass);
        AddPart(character, "BackCloak", PrimitiveType.Cube, chest, new Vector3(0f, 0.17f, -0.145f), new Vector3(0.35f, 0.40f, 0.07f), cloth);
        AddPart(character, "Neck", PrimitiveType.Capsule, neck, new Vector3(0f, 0.52f, 0f), new Vector3(0.11f, 0.08f, 0.11f), skin);
        AddPart(character, "Head", PrimitiveType.Sphere, head, new Vector3(0f, 0.72f, 0f), new Vector3(0.25f, 0.28f, 0.225f), skin);
        AddPart(character, "HairCap", PrimitiveType.Sphere, head, new Vector3(0f, 0.82f, -0.025f), new Vector3(0.255f, 0.12f, 0.225f), armor);
        AddPart(character, "Eye_L", PrimitiveType.Sphere, head, new Vector3(-0.072f, 0.74f, 0.108f), new Vector3(0.04f, 0.04f, 0.025f), dark);
        AddPart(character, "Eye_R", PrimitiveType.Sphere, head, new Vector3(0.072f, 0.74f, 0.108f), new Vector3(0.04f, 0.04f, 0.025f), dark);

        // Arms: shoulder cap overlaps torso; upper arm, forearm and glove overlap at joints.
        AddPart(character, "Shoulder_L", PrimitiveType.Sphere, leftUpperArm, new Vector3(-0.245f, 0.39f, 0f), new Vector3(0.18f, 0.14f, 0.18f), brass);
        AddPart(character, "UpperArm_L", PrimitiveType.Capsule, leftUpperArm, new Vector3(-0.29f, 0.27f, 0f), new Vector3(0.12f, 0.16f, 0.12f), armor);
        AddPart(character, "Forearm_L", PrimitiveType.Capsule, leftLowerArm, new Vector3(-0.33f, 0.07f, 0f), new Vector3(0.105f, 0.15f, 0.105f), leather);
        AddPart(character, "Glove_L", PrimitiveType.Sphere, leftHand, new Vector3(-0.35f, -0.04f, 0.005f), new Vector3(0.105f, 0.11f, 0.105f), leather);
        AddPart(character, "Shoulder_R", PrimitiveType.Sphere, rightUpperArm, new Vector3(0.245f, 0.39f, 0f), new Vector3(0.18f, 0.14f, 0.18f), brass);
        AddPart(character, "UpperArm_R", PrimitiveType.Capsule, rightUpperArm, new Vector3(0.29f, 0.27f, 0f), new Vector3(0.12f, 0.16f, 0.12f), armor);
        AddPart(character, "Forearm_R", PrimitiveType.Capsule, rightLowerArm, new Vector3(0.33f, 0.07f, 0f), new Vector3(0.105f, 0.15f, 0.105f), leather);
        AddPart(character, "Glove_R", PrimitiveType.Sphere, rightHand, new Vector3(0.35f, -0.04f, 0.005f), new Vector3(0.105f, 0.11f, 0.105f), leather);

        // Legs: upper and lower sections deliberately overlap; boots sit at the bottom.
        AddPart(character, "Thigh_L", PrimitiveType.Capsule, leftUpperLeg, new Vector3(-0.12f, -0.24f, 0f), new Vector3(0.14f, 0.20f, 0.14f), leather);
        AddPart(character, "Shin_L", PrimitiveType.Capsule, leftLowerLeg, new Vector3(-0.12f, -0.55f, 0f), new Vector3(0.115f, 0.19f, 0.115f), armor);
        AddPart(character, "Boot_L", PrimitiveType.Cube, leftFoot, new Vector3(-0.12f, -0.82f, 0.08f), new Vector3(0.17f, 0.085f, 0.28f), leather);
        AddPart(character, "KneeGuard_L", PrimitiveType.Sphere, leftLowerLeg, new Vector3(-0.12f, -0.44f, 0.08f), new Vector3(0.11f, 0.10f, 0.05f), brass);
        AddPart(character, "Thigh_R", PrimitiveType.Capsule, rightUpperLeg, new Vector3(0.12f, -0.24f, 0f), new Vector3(0.14f, 0.20f, 0.14f), leather);
        AddPart(character, "Shin_R", PrimitiveType.Capsule, rightLowerLeg, new Vector3(0.12f, -0.55f, 0f), new Vector3(0.115f, 0.19f, 0.115f), armor);
        AddPart(character, "Boot_R", PrimitiveType.Cube, rightFoot, new Vector3(0.12f, -0.82f, 0.08f), new Vector3(0.17f, 0.085f, 0.28f), leather);
        AddPart(character, "KneeGuard_R", PrimitiveType.Sphere, rightLowerLeg, new Vector3(0.12f, -0.44f, 0.08f), new Vector3(0.11f, 0.10f, 0.05f), brass);

        Animator animator = character.AddComponent<Animator>();
        animator.applyRootMotion = false;
        animator.runtimeAnimatorController = controller;

        Avatar generatedAvatar = AvatarBuilder.BuildGenericAvatar(character, "");
        generatedAvatar.name = "VeyrWandererAvatar";
        generatedAvatar.hideFlags = HideFlags.None;
        if (AssetDatabase.LoadAssetAtPath<Avatar>(AvatarPath) != null)
            AssetDatabase.DeleteAsset(AvatarPath);
        AssetDatabase.CreateAsset(generatedAvatar, AvatarPath);
        animator.avatar = AssetDatabase.LoadAssetAtPath<Avatar>(AvatarPath);

        GameObject savedPrefab = PrefabUtility.SaveAsPrefabAsset(character, PrefabPath);
        UnityEngine.Object.DestroyImmediate(character);
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();

        if (savedPrefab == null)
        {
            EditorUtility.DisplayDialog("Phase 2 Build Failed", "Unity could not save the character prefab. Check the Console.", "OK");
            return;
        }

        AttachCharacterToPlayer(savedPrefab);
        Debug.Log("Phase 2 character generated at " + PrefabPath +
                  " with bone-attached mesh parts, a Generic Avatar, and keyframed Idle/Walk/Run/Attack clips.");
        EditorUtility.DisplayDialog(
            "Phase 2 Character Built",
            "Generated the Veyr Wanderer articulated character with corrected bone locations and overlapping limb segments, plus a Generic Avatar, Animator Controller, and Idle/Walk/Run/Attack clips.\n\n" +
            "Attached it to Player if that object was found in the open scene. Check the character in Game view, then run Validate Character Rig.",
            "OK");
    }

    [MenuItem("Tools/Code Lyoko/Phase 2/Attach Character to Player", true)]
    private static bool ValidateAttach() => CanEdit();

    [MenuItem("Tools/Code Lyoko/Phase 2/Attach Character to Player")]
    public static void AttachCharacterCommand()
    {
        if (!CanEdit()) return;
        GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
        if (prefab == null)
        {
            EditorUtility.DisplayDialog("Character Asset Not Found",
                "Run Tools > Code Lyoko > Phase 2 > Build Rigged Character and Animations first.", "OK");
            return;
        }
        AttachCharacterToPlayer(prefab);
    }

    [MenuItem("Tools/Code Lyoko/Phase 2/Validate Character Rig", true)]
    private static bool ValidateRigMenu() => CanEdit();

    [MenuItem("Tools/Code Lyoko/Phase 2/Validate Character Rig")]
    public static void ValidateCharacterRig()
    {
        if (!CanEdit()) return;
        List<string> passed = new List<string>();
        List<string> failed = new List<string>();

        GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(PrefabPath);
        if (prefab == null)
        {
            failed.Add("Character prefab not found. Run the Phase 2 build command.");
        }
        else
        {
            passed.Add("Veyr Wanderer prefab exists.");
            Animator animator = prefab.GetComponent<Animator>();
            if (animator == null) failed.Add("Prefab root is missing Animator.");
            else
            {
                passed.Add("Animator component exists.");
                if (animator.runtimeAnimatorController != null) passed.Add("Animator Controller is assigned.");
                else failed.Add("Animator Controller is missing.");
                if (animator.avatar != null && animator.avatar.isValid && !animator.avatar.isHuman)
                    passed.Add("Valid Generic Avatar is assigned.");
                else failed.Add("Generic Avatar is missing or invalid.");
                if (animator.runtimeAnimatorController is AnimatorController controller)
                {
                    bool speed = false, attack = false;
                    foreach (AnimatorControllerParameter p in controller.parameters)
                    {
                        if (p.name == "MoveSpeed" && p.type == AnimatorControllerParameterType.Float) speed = true;
                        if (p.name == "Attack" && p.type == AnimatorControllerParameterType.Trigger) attack = true;
                    }
                    if (speed) passed.Add("MoveSpeed float parameter exists."); else failed.Add("MoveSpeed parameter missing.");
                    if (attack) passed.Add("Attack trigger exists."); else failed.Add("Attack trigger missing.");
                }
            }

            Transform armature = prefab.transform.Find("Armature");
            if (armature != null)
                passed.Add("Armature hierarchy exists.");
            else
                failed.Add("Armature hierarchy is missing.");

            MeshRenderer[] renderers = prefab.GetComponentsInChildren<MeshRenderer>(true);
            int missingMeshes = 0;
            int partsOutsideArmature = 0;
            foreach (MeshRenderer renderer in renderers)
            {
                MeshFilter filter = renderer.GetComponent<MeshFilter>();
                if (filter == null || filter.sharedMesh == null)
                    missingMeshes++;

                if (armature == null || !renderer.transform.IsChildOf(armature))
                    partsOutsideArmature++;
            }

            if (renderers.Length >= 20)
                passed.Add("Character mesh parts found: " + renderers.Length + ".");
            else
                failed.Add("Expected a full character assembled from bone-attached mesh parts; found " + renderers.Length + ".");

            if (missingMeshes == 0 && renderers.Length > 0)
                passed.Add("All character mesh parts have valid meshes.");
            else if (renderers.Length > 0)
                failed.Add(missingMeshes + " character mesh part(s) have missing MeshFilters or meshes.");

            if (partsOutsideArmature == 0 && renderers.Length > 0)
                passed.Add("All character mesh parts are attached within the bone hierarchy.");
            else if (renderers.Length > 0)
                failed.Add(partsOutsideArmature + " mesh part(s) are not parented to the character armature.");
        }

        foreach (string clipName in new[] { "Idle.anim", "Walk.anim", "Run.anim", "Attack.anim" })
        {
            AnimationClip clip = AssetDatabase.LoadAssetAtPath<AnimationClip>(AnimationsFolder + "/" + clipName);
            if (clip != null && AnimationUtility.GetCurveBindings(clip).Length > 0)
                passed.Add(clipName + " has animation curves.");
            else failed.Add(clipName + " is missing or has no animation curves.");
        }

        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player == null) player = GameObject.Find("Player");
        if (player == null) failed.Add("Player not found in active scene.");
        else
        {
            Animator attached = player.GetComponentInChildren<Animator>();
            if (attached != null && attached.runtimeAnimatorController != null)
                passed.Add("Animated character is attached under Player.");
            else failed.Add("Character Animator not attached to Player.");
        }

        foreach (string line in passed) Debug.Log("[Phase 2 PASS] " + line);
        foreach (string line in failed) Debug.LogError("[Phase 2 CHECK] " + line);
        EditorUtility.DisplayDialog("Phase 2 Rig Validation",
            "Checks passed: " + passed.Count + "\nChecks needing attention: " + failed.Count +
            "\n\nFull report is in Console. Structural checks do not prove the animations look correct in Play mode.", "OK");
    }

    private static void AttachCharacterToPlayer(GameObject prefab)
    {
        GameObject player = GameObject.FindGameObjectWithTag("Player");
        if (player == null) player = GameObject.Find("Player");
        if (player == null)
        {
            Debug.LogWarning("Player was not found. The Veyr Wanderer prefab was built but not attached.");
            return;
        }

        for (int i = player.transform.childCount - 1; i >= 0; i--)
            UnityEngine.Object.DestroyImmediate(player.transform.GetChild(i).gameObject);

        GameObject instance = PrefabUtility.InstantiatePrefab(prefab) as GameObject;
        if (instance == null)
        {
            Debug.LogError("Could not instantiate the Veyr Wanderer prefab.");
            return;
        }
        instance.name = "VeyrWanderer";
        instance.transform.SetParent(player.transform, false);
        instance.transform.localPosition = new Vector3(0f, -0.13f, 0f);
        instance.transform.localRotation = Quaternion.identity;
        instance.transform.localScale = Vector3.one;

        Animator animator = instance.GetComponent<Animator>();
        if (animator != null)
        {
            animator.applyRootMotion = false;
            PlayerLocomotionAnimator bridge = player.GetComponent<PlayerLocomotionAnimator>();
            if (bridge == null) bridge = player.AddComponent<PlayerLocomotionAnimator>();
            bridge.CharacterAnimator = animator;
        }

        IsometricPlayerController movement = player.GetComponent<IsometricPlayerController>();
        if (movement == null) movement = player.AddComponent<IsometricPlayerController>();
        if (Camera.main != null) movement.MovementCamera = Camera.main.transform;

        Scene scene = SceneManager.GetActiveScene();
        EditorSceneManager.MarkSceneDirty(scene);
        if (!string.IsNullOrEmpty(scene.path)) EditorSceneManager.SaveScene(scene);
        AssetDatabase.SaveAssets();
    }

    private static Transform CreateBone(string name, Transform parent, Vector3 position)
    {
        GameObject bone = new GameObject(name);
        bone.transform.SetParent(parent, false);
        bone.transform.localPosition = position;
        bone.transform.localRotation = Quaternion.identity;
        bone.transform.localScale = Vector3.one;
        return bone.transform;
    }

    private static void AddPart(GameObject character, string partName, PrimitiveType primitiveType,
        Transform bone, Vector3 characterLocalPosition, Vector3 localScale, Material material)
    {
        if (character == null || bone == null)
            throw new ArgumentNullException(bone == null ? nameof(bone) : nameof(character));

        // Build the visible mesh directly under its controlling bone. This rigid-segment
        // approach is robust for the stylized prototype and avoids the broken bind-pose
        // results from the previous generated SkinnedMeshRenderer implementation.
        GameObject part = GameObject.CreatePrimitive(primitiveType);
        part.name = partName;
        part.transform.SetParent(bone, false);

        Vector3 desiredWorldPosition = character.transform.TransformPoint(characterLocalPosition);
        part.transform.localPosition = bone.InverseTransformPoint(desiredWorldPosition);
        part.transform.localRotation = Quaternion.identity;
        part.transform.localScale = localScale;

        Renderer renderer = part.GetComponent<Renderer>();
        if (renderer != null)
            renderer.sharedMaterial = material;

        Collider collider = part.GetComponent<Collider>();
        if (collider != null)
            UnityEngine.Object.DestroyImmediate(collider);
    }

    private static AnimationClip CreateIdleClip()
    {
        AnimationClip clip = PrepareClip("Idle.anim", "VeyrWanderer_Idle", 2f, true);
        AddCurve(clip, ChestPath, "localEulerAnglesRaw.x",
            new Keyframe(0f, 0f), new Keyframe(0.5f, 1.8f), new Keyframe(1f, 0f),
            new Keyframe(1.5f, -1.2f), new Keyframe(2f, 0f));
        AddCurve(clip, HeadPath, "localEulerAnglesRaw.y",
            new Keyframe(0f, -1f), new Keyframe(0.5f, 1.5f), new Keyframe(1f, -1f),
            new Keyframe(1.5f, 0.5f), new Keyframe(2f, -1f));
        AddCurve(clip, HipsPath, "m_LocalPosition.y",
            new Keyframe(0f, -0.10f), new Keyframe(0.5f, -0.085f), new Keyframe(1f, -0.10f),
            new Keyframe(1.5f, -0.09f), new Keyframe(2f, -0.10f));
        SaveClip(clip);
        return clip;
    }

    private static AnimationClip CreateWalkClip()
    {
        AnimationClip clip = PrepareClip("Walk.anim", "VeyrWanderer_Walk", 0.8f, true);
        AddGaitCurves(clip, 0.8f, 25f, 20f, 14f, 4f);
        SaveClip(clip);
        return clip;
    }

    private static AnimationClip CreateRunClip()
    {
        AnimationClip clip = PrepareClip("Run.anim", "VeyrWanderer_Run", 0.48f, true);
        AddGaitCurves(clip, 0.48f, 42f, 38f, 28f, 9f);
        SaveClip(clip);
        return clip;
    }

    private static AnimationClip CreateAttackClip()
    {
        const float duration = 0.42f;
        AnimationClip clip = PrepareClip("Attack.anim", "VeyrWanderer_Attack", duration, false);
        AddCurve(clip, RightUpperArmPath, "localEulerAnglesRaw.x",
            new Keyframe(0f, 0f), new Keyframe(0.09f, -35f), new Keyframe(0.17f, -82f),
            new Keyframe(0.28f, -38f), new Keyframe(duration, 0f));
        AddCurve(clip, RightLowerArmPath, "localEulerAnglesRaw.x",
            new Keyframe(0f, 0f), new Keyframe(0.09f, -8f), new Keyframe(0.17f, -32f),
            new Keyframe(0.28f, -10f), new Keyframe(duration, 0f));
        AddCurve(clip, ChestPath, "localEulerAnglesRaw.y",
            new Keyframe(0f, 0f), new Keyframe(0.09f, -12f), new Keyframe(0.17f, 24f),
            new Keyframe(0.28f, 6f), new Keyframe(duration, 0f));
        AddCurve(clip, LeftUpperArmPath, "localEulerAnglesRaw.x",
            new Keyframe(0f, 0f), new Keyframe(0.09f, 12f), new Keyframe(0.17f, 28f),
            new Keyframe(0.28f, 8f), new Keyframe(duration, 0f));
        SaveClip(clip);
        return clip;
    }

    private static void AddGaitCurves(AnimationClip clip, float duration, float legSwing,
        float kneeBend, float armSwing, float torsoLean)
    {
        float q = duration * 0.25f, h = duration * 0.5f, tq = duration * 0.75f;
        AddCurve(clip, LeftUpperLegPath, "localEulerAnglesRaw.x",
            new Keyframe(0f, legSwing), new Keyframe(q, 0f), new Keyframe(h, -legSwing),
            new Keyframe(tq, 0f), new Keyframe(duration, legSwing));
        AddCurve(clip, RightUpperLegPath, "localEulerAnglesRaw.x",
            new Keyframe(0f, -legSwing), new Keyframe(q, 0f), new Keyframe(h, legSwing),
            new Keyframe(tq, 0f), new Keyframe(duration, -legSwing));
        AddCurve(clip, LeftLowerLegPath, "localEulerAnglesRaw.x",
            new Keyframe(0f, 0f), new Keyframe(q, kneeBend), new Keyframe(h, 4f),
            new Keyframe(tq, kneeBend * 0.35f), new Keyframe(duration, 0f));
        AddCurve(clip, RightLowerLegPath, "localEulerAnglesRaw.x",
            new Keyframe(0f, 4f), new Keyframe(q, kneeBend * 0.35f), new Keyframe(h, 0f),
            new Keyframe(tq, kneeBend), new Keyframe(duration, 4f));
        AddCurve(clip, LeftUpperArmPath, "localEulerAnglesRaw.x",
            new Keyframe(0f, -armSwing), new Keyframe(q, 0f), new Keyframe(h, armSwing),
            new Keyframe(tq, 0f), new Keyframe(duration, -armSwing));
        AddCurve(clip, RightUpperArmPath, "localEulerAnglesRaw.x",
            new Keyframe(0f, armSwing), new Keyframe(q, 0f), new Keyframe(h, -armSwing),
            new Keyframe(tq, 0f), new Keyframe(duration, armSwing));
        AddCurve(clip, ChestPath, "localEulerAnglesRaw.x",
            new Keyframe(0f, torsoLean), new Keyframe(q, torsoLean + 2f), new Keyframe(h, torsoLean),
            new Keyframe(tq, torsoLean - 2f), new Keyframe(duration, torsoLean));
        AddCurve(clip, HipsPath, "localEulerAnglesRaw.y",
            new Keyframe(0f, -3f), new Keyframe(q, 2f), new Keyframe(h, 3f),
            new Keyframe(tq, -2f), new Keyframe(duration, -3f));
        AddCurve(clip, HipsPath, "m_LocalPosition.y",
            new Keyframe(0f, -0.10f), new Keyframe(q, -0.065f), new Keyframe(h, -0.10f),
            new Keyframe(tq, -0.065f), new Keyframe(duration, -0.10f));
    }

    private static AnimationClip PrepareClip(string fileName, string clipName, float duration, bool loop)
    {
        string path = AnimationsFolder + "/" + fileName;
        AnimationClip clip = AssetDatabase.LoadAssetAtPath<AnimationClip>(path);
        if (clip == null) clip = new AnimationClip();
        clip.name = clipName;
        clip.frameRate = 30f;
        clip.legacy = false;
        clip.ClearCurves();
        AnimationClipSettings settings = AnimationUtility.GetAnimationClipSettings(clip);
        settings.loopTime = loop;
        settings.loopBlend = loop;
        settings.stopTime = duration;
        AnimationUtility.SetAnimationClipSettings(clip, settings);
        return clip;
    }

    private static void AddCurve(AnimationClip clip, string path, string property, params Keyframe[] keys)
    {
        AnimationUtility.SetEditorCurve(clip,
            EditorCurveBinding.FloatCurve(path, typeof(Transform), property),
            new AnimationCurve(keys));
    }

    private static void SaveClip(AnimationClip clip)
    {
        string path = AnimationsFolder + "/" + clip.name.Replace("VeyrWanderer_", "") + ".anim";
        if (AssetDatabase.Contains(clip)) EditorUtility.SetDirty(clip);
        else AssetDatabase.CreateAsset(clip, path);
    }

    private static AnimatorController CreateController(AnimationClip idle, AnimationClip walk, AnimationClip run, AnimationClip attack)
    {
        if (idle == null || walk == null || run == null || attack == null)
            throw new InvalidOperationException("Phase 2 could not create all four animation clips.");

        // Replace the controller deterministically so stale sub-assets/transitions cannot accumulate.
        if (AssetDatabase.LoadAssetAtPath<AnimatorController>(ControllerPath) != null)
            AssetDatabase.DeleteAsset(ControllerPath);

        AnimatorController controller = AnimatorController.CreateAnimatorControllerAtPath(ControllerPath);
        if (controller == null)
            throw new InvalidOperationException("Unity failed to create Animator Controller at " + ControllerPath);

        controller.AddParameter("MoveSpeed", AnimatorControllerParameterType.Float);
        controller.AddParameter("Attack", AnimatorControllerParameterType.Trigger);

        if (controller.layers == null || controller.layers.Length == 0 || controller.layers[0].stateMachine == null)
            throw new InvalidOperationException("The generated Animator Controller has no base state machine.");

        AnimatorStateMachine machine = controller.layers[0].stateMachine;

        // Unity versions/templates can produce a controller whose state machine has no default state.
        // Never dereference machine.defaultState until we confirm it exists.
        AnimatorState locomotion = null;
        foreach (ChildAnimatorState child in machine.states)
        {
            if (child.state != null &&
                (child.state.name == "Locomotion" || child.state == machine.defaultState))
            {
                locomotion = child.state;
                break;
            }
        }

        if (locomotion == null)
            locomotion = machine.AddState("Locomotion", new Vector3(80f, 70f, 0f));
        else
            locomotion.name = "Locomotion";

        machine.defaultState = locomotion;

        BlendTree tree = new BlendTree
        {
            name = "Locomotion Blend Tree",
            blendType = BlendTreeType.Simple1D,
            blendParameter = "MoveSpeed",
            useAutomaticThresholds = false
        };
        tree.children = new[]
        {
            new ChildMotion { motion = idle, threshold = 0f, timeScale = 1f },
            new ChildMotion { motion = walk, threshold = 0.5f, timeScale = 1f },
            new ChildMotion { motion = run, threshold = 1f, timeScale = 1f }
        };

        AssetDatabase.AddObjectToAsset(tree, controller);
        locomotion.motion = tree;

        AnimatorState attackState = machine.AddState("Attack", new Vector3(330f, 70f, 0f));
        attackState.motion = attack;

        AnimatorStateTransition enterAttack = machine.AddAnyStateTransition(attackState);
        enterAttack.AddCondition(AnimatorConditionMode.If, 0f, "Attack");
        enterAttack.hasExitTime = false;
        enterAttack.duration = 0.04f;
        enterAttack.canTransitionToSelf = false;
        enterAttack.interruptionSource = TransitionInterruptionSource.None;

        AnimatorStateTransition exitAttack = attackState.AddTransition(locomotion);
        exitAttack.hasExitTime = true;
        exitAttack.exitTime = 0.96f;
        exitAttack.duration = 0.08f;
        exitAttack.hasFixedDuration = true;

        EditorUtility.SetDirty(machine);
        EditorUtility.SetDirty(controller);
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();

        AnimatorController savedController = AssetDatabase.LoadAssetAtPath<AnimatorController>(ControllerPath);
        if (savedController == null)
            throw new InvalidOperationException("Animator Controller was not saved correctly at " + ControllerPath);

        return savedController;
    }

    private static Material CreateMaterial(string path, Color color)
    {
        Shader shader = FindShader();
        Material material = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (material == null)
        {
            if (shader == null)
            {
                Debug.LogError("Could not find a supported shader while creating " + path);
                return null;
            }
            material = new Material(shader);
            material.name = System.IO.Path.GetFileNameWithoutExtension(path);
            SetMaterialColor(material, color);
            AssetDatabase.CreateAsset(material, path);
            return material;
        }

        if (shader != null && (material.shader == null || material.shader.name == "Hidden/InternalErrorShader" ||
            !material.shader.isSupported || !material.shader.name.StartsWith("Universal Render Pipeline/")))
            material.shader = shader;
        SetMaterialColor(material, color);
        EditorUtility.SetDirty(material);
        return material;
    }

    private static Shader FindShader()
    {
        foreach (string name in new[] {
            "Universal Render Pipeline/Lit",
            "Universal Render Pipeline/Simple Lit",
            "Universal Render Pipeline/Unlit",
            "Standard"
        })
        {
            Shader shader = Shader.Find(name);
            if (shader != null && shader.isSupported) return shader;
        }
        return null;
    }

    private static void SetMaterialColor(Material material, Color color)
    {
        if (material == null) return;
        if (material.HasProperty("_BaseColor")) material.SetColor("_BaseColor", color);
        if (material.HasProperty("_Color")) material.SetColor("_Color", color);
    }

    private static bool CanEdit()
    {
        return !EditorApplication.isPlayingOrWillChangePlaymode && !EditorApplication.isCompiling;
    }

    private static void EnsureFolders()
    {
        EnsureFolder("Assets", "_Project");
        EnsureFolder("Assets/_Project", "Characters");
        EnsureFolder("Assets/_Project/Characters", "VeyrWanderer");
        EnsureFolder(Root, "Meshes");
        EnsureFolder(Root, "Materials");
        EnsureFolder(Root, "Animations");
        EnsureFolder(Root, "Prefabs");
    }

    private static void EnsureFolder(string parent, string name)
    {
        string path = parent + "/" + name;
        if (!AssetDatabase.IsValidFolder(path)) AssetDatabase.CreateFolder(parent, name);
    }
}
#endif
