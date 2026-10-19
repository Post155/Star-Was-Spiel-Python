"""Erzeugt .meta-Dateien (stabile GUIDs), Szenen, Prefabs und Build-Settings des Unity-Projekts. Wiederholbar."""
import os, uuid, re, json
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = os.path.join(ROOT, "Assets")
def guid(rel): return uuid.uuid5(uuid.NAMESPACE_URL, "starwars-unity/" + rel).hex
def w(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", newline="\n").write(text)

MONO = "fileFormatVersion: 2\nguid: %s\nMonoImporter:\n  externalObjects: {}\n  serializedVersion: 2\n  defaultReferences: []\n  executionOrder: 0\n  icon: {instanceID: 0}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"
ASMDEF = "fileFormatVersion: 2\nguid: %s\nAssemblyDefinitionImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"
FOLDER = "fileFormatVersion: 2\nguid: %s\nfolderAsset: yes\nDefaultImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"
DEFAULT = "fileFormatVersion: 2\nguid: %s\nDefaultImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"
PREFAB = "fileFormatVersion: 2\nguid: %s\nPrefabImporter:\n  externalObjects: {}\n  userData: \n  assetBundleName: \n  assetBundleVariant: \n"

def meta_for(rel_from_root):
    g = guid(rel_from_root)
    if rel_from_root.endswith(".cs"): return MONO % g
    if rel_from_root.endswith(".asmdef"): return ASMDEF % g
    if rel_from_root.endswith(".prefab"): return PREFAB % g
    return DEFAULT % g

# 1) Metas für alle Skripte/asmdef/Szenen/Prefabs/Ordner (außer bereits vorhandenen)
for base, dirs, files in os.walk(A):
    rel_dir = os.path.relpath(base, ROOT).replace(os.sep, "/")
    if rel_dir != "Assets" and not os.path.exists(base + ".meta") and "Pixelarts" not in rel_dir:
        w(base + ".meta", FOLDER % guid(rel_dir))
    for f in files:
        if f.endswith(".meta"): continue
        rel = (rel_dir + "/" + f)
        if f.endswith((".cs", ".asmdef", ".unity", ".prefab")) and not os.path.exists(os.path.join(base, f) + ".meta"):
            w(os.path.join(base, f) + ".meta", meta_for(rel))

# 2) Prefabs (Pool-Prefabs: GameObject + Transform + SpriteRenderer)
POOLS = ["planets","stars1","stars2","filter","foreground","asteroids","lasers","torpedoes","enemies","hpbg","hpfill","etorp","elaser","player","players","explosions","fx","ghost","dbg"]
PREFAB_YAML = """%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!1 &{go}
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  serializedVersion: 6
  m_Component:
  - component: {{fileID: {tr}}}
  - component: {{fileID: {sr}}}
  m_Layer: 0
  m_Name: Pool_{name}
  m_TagString: Untagged
  m_Icon: {{fileID: 0}}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
--- !u!4 &{tr}
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go}}}
  serializedVersion: 2
  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
  m_LocalPosition: {{x: 0, y: 0, z: 0}}
  m_LocalScale: {{x: 1, y: 1, z: 1}}
  m_ConstrainProportionsScale: 0
  m_Children: []
  m_Father: {{fileID: 0}}
  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}
--- !u!212 &{sr}
SpriteRenderer:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: {go}}}
  m_Enabled: 1
  m_CastShadows: 0
  m_ReceiveShadows: 0
  m_DynamicOccludee: 1
  m_StaticShadowCaster: 0
  m_MotionVectors: 1
  m_LightProbeUsage: 1
  m_ReflectionProbeUsage: 1
  m_RayTracingMode: 0
  m_RayTraceProcedural: 0
  m_RenderingLayerMask: 1
  m_RendererPriority: 0
  m_Materials:
  - {{fileID: 10754, guid: 0000000000000000f000000000000000, type: 0}}
  m_StaticBatchInfo:
    firstSubMesh: 0
    subMeshCount: 0
  m_StaticBatchRoot: {{fileID: 0}}
  m_ProbeAnchor: {{fileID: 0}}
  m_LightProbeVolumeOverride: {{fileID: 0}}
  m_ScaleInLightmap: 1
  m_ReceiveGI: 1
  m_PreserveUVs: 0
  m_IgnoreNormalsForChartDetection: 0
  m_ImportantGI: 0
  m_StitchLightmapSeams: 1
  m_SelectedEditorRenderState: 0
  m_MinimumChartSize: 4
  m_AutoUVMaxDistance: 0.5
  m_AutoUVMaxAngle: 89
  m_LightmapParameters: {{fileID: 0}}
  m_SortingLayerID: 0
  m_SortingLayer: 0
  m_SortingOrder: 0
  m_Sprite: {{fileID: 0}}
  m_Color: {{r: 1, g: 1, b: 1, a: 1}}
  m_FlipX: 0
  m_FlipY: 0
  m_DrawMode: 0
  m_Size: {{x: 1, y: 1}}
  m_AdaptiveModeThreshold: 0.5
  m_SpriteTileMode: 0
  m_WasSpriteAssigned: 0
  m_MaskInteraction: 0
  m_SpriteSortPoint: 0
"""
for n in POOLS:
    p = os.path.join(A, "Resources", "Prefabs", "Pool_%s.prefab" % n)
    w(p, PREFAB_YAML.format(go=1000, tr=2000, sr=3000, name=n))
    w(p + ".meta", PREFAB % guid("Assets/Resources/Prefabs/Pool_%s.prefab" % n))
w(os.path.join(A, "Resources", "Prefabs.meta"), FOLDER % guid("Assets/Resources/Prefabs"))

# 3) Szenen
SCENES = ["MainMenu","FactionSelection","DifficultySelection","ShipSelection","Singleplayer","MultiplayerMenu","LocalPointsFight","LocalLastSurvivor","LanLobby","LanGame"]
boot_guid = guid("Assets/Scripts/Game/SceneBootstrap.cs")
SCENE_YAML = """%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!29 &1
OcclusionCullingSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 2
  m_OcclusionBakeSettings:
    smallestOccluder: 5
    smallestHole: 0.25
    backfaceThreshold: 100
  m_SceneGUID: 00000000000000000000000000000000
  m_OcclusionCullingData: {{fileID: 0}}
--- !u!104 &2
RenderSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 10
  m_Fog: 0
  m_AmbientMode: 3
  m_AmbientIntensity: 1
  m_DefaultReflectionMode: 0
  m_DefaultReflectionResolution: 128
  m_ReflectionBounces: 1
  m_ReflectionIntensity: 1
  m_CustomReflection: {{fileID: 0}}
  m_Sun: {{fileID: 0}}
--- !u!1 &10
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  serializedVersion: 6
  m_Component:
  - component: {{fileID: 11}}
  - component: {{fileID: 12}}
  - component: {{fileID: 13}}
  m_Layer: 0
  m_Name: Main Camera
  m_TagString: MainCamera
  m_Icon: {{fileID: 0}}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
--- !u!4 &11
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: 10}}
  serializedVersion: 2
  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
  m_LocalPosition: {{x: 0, y: 0, z: -10}}
  m_LocalScale: {{x: 1, y: 1, z: 1}}
  m_ConstrainProportionsScale: 0
  m_Children: []
  m_Father: {{fileID: 0}}
  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}
--- !u!20 &12
Camera:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: 10}}
  m_Enabled: 1
  serializedVersion: 2
  m_ClearFlags: 2
  m_BackGroundColor: {{r: 0, g: 0, b: 0, a: 0}}
  m_projectionMatrixMode: 1
  m_GateFitMode: 2
  m_FOVAxisMode: 0
  m_Iso: 200
  m_ShutterSpeed: 0.005
  m_Aperture: 16
  m_FocusDistance: 10
  m_FocalLength: 50
  m_BladeCount: 5
  m_Curvature: {{x: 2, y: 11}}
  m_BarrelClipping: 0.25
  m_Anamorphism: 0
  m_SensorSize: {{x: 36, y: 24}}
  m_LensShift: {{x: 0, y: 0}}
  m_NormalizedViewPortRect:
    serializedVersion: 2
    x: 0
    y: 0
    width: 1
    height: 1
  near clip plane: 0.3
  far clip plane: 1000
  field of view: 60
  orthographic: 1
  orthographic size: 5
  m_Depth: -1
  m_CullingMask:
    serializedVersion: 2
    m_Bits: 4294967295
  m_RenderingPath: -1
  m_TargetTexture: {{fileID: 0}}
  m_TargetDisplay: 0
  m_TargetEye: 3
  m_HDR: 1
  m_AllowMSAA: 1
  m_AllowDynamicResolution: 0
  m_ForceIntoRT: 0
  m_OcclusionCulling: 1
  m_StereoConvergence: 10
  m_StereoSeparation: 0.022
--- !u!81 &13
AudioListener:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: 10}}
  m_Enabled: 1
--- !u!1 &20
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  serializedVersion: 6
  m_Component:
  - component: {{fileID: 21}}
  - component: {{fileID: 22}}
  m_Layer: 0
  m_Name: SceneBootstrap
  m_TagString: Untagged
  m_Icon: {{fileID: 0}}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
--- !u!4 &21
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: 20}}
  serializedVersion: 2
  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
  m_LocalPosition: {{x: 0, y: 0, z: 0}}
  m_LocalScale: {{x: 1, y: 1, z: 1}}
  m_ConstrainProportionsScale: 0
  m_Children: []
  m_Father: {{fileID: 0}}
  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}
--- !u!114 &22
MonoBehaviour:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: 20}}
  m_Enabled: 1
  m_EditorHideFlags: 0
  m_Script: {{fileID: 11500000, guid: {boot}, type: 3}}
  m_Name: 
  m_EditorClassIdentifier: 
--- !u!1660057539 &9223372036854775807
SceneRoots:
  m_ObjectHideFlags: 0
  m_Roots:
  - {{fileID: 11}}
  - {{fileID: 21}}
"""
for s in SCENES:
    p = os.path.join(A, "Scenes", s + ".unity")
    w(p, SCENE_YAML.format(boot=boot_guid))
    w(p + ".meta", DEFAULT % guid("Assets/Scenes/%s.unity" % s))
w(os.path.join(A, "Scenes.meta"), FOLDER % guid("Assets/Scenes"))

# 4) Build Settings
rows = "".join("  - enabled: 1\n    path: Assets/Scenes/%s.unity\n    guid: %s\n" % (s, guid("Assets/Scenes/%s.unity" % s)) for s in SCENES)
w(os.path.join(ROOT, "ProjectSettings", "EditorBuildSettings.asset"),
  "%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!1045 &1\nEditorBuildSettings:\n  m_ObjectHideFlags: 0\n  serializedVersion: 2\n  m_Scenes:\n" + rows + "  m_configObjects: {}\n  m_UseUCBPForAssetBundles: 0\n")

# 5) Pakete
mp = os.path.join(ROOT, "Packages", "manifest.json")
m = json.load(open(mp))
m["dependencies"]["com.unity.ugui"] = "2.0.0"
m["dependencies"] = dict(sorted(m["dependencies"].items()))
json.dump(m, open(mp, "w"), indent=2); open(mp, "a").write("\n")
lp = os.path.join(ROOT, "Packages", "packages-lock.json")
if os.path.exists(lp): os.remove(lp)   # Unity löst die Abhängigkeiten beim Öffnen neu auf

# 6) ProjectSettings
ps = os.path.join(ROOT, "ProjectSettings", "ProjectSettings.asset")
t = open(ps).read()
t = t.replace("productName: Star-Was-Spiel-Python", "productName: Star Wars").replace("companyName: DefaultCompany", "companyName: StarWarsPort")
t = t.replace("  runInBackground: 0", "  runInBackground: 1")      # LAN-Host muss auch ohne Fokus weiterlaufen (zwei Instanzen auf einem PC)
t = t.replace("  defaultScreenWidth: 1920", "  defaultScreenWidth: 1280").replace("  defaultScreenHeight: 1080", "  defaultScreenHeight: 720")
t = t.replace("  fullscreenMode: 1", "  fullscreenMode: 3").replace("  resizableWindow: 0", "  resizableWindow: 1")
open(ps, "w", newline="\n").write(t)
print("fertig:", len(SCENES), "Szenen,", len(POOLS), "Prefabs")
