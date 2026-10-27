using UnityEngine;

namespace Ashen.Core
{
    /// <summary>Minimal persistence (PlayerPrefs): last checkpoint and whether the boss is dead. F9 wipes it.</summary>
    public static class SaveGame
    {
        const string CheckpointKey = "ashen.checkpoint";
        const string BossKey = "ashen.bossDefeated";

        public static string CheckpointName
        {
            get => PlayerPrefs.GetString(CheckpointKey, "");
            set { PlayerPrefs.SetString(CheckpointKey, value ?? ""); PlayerPrefs.Save(); }
        }

        public static bool BossDefeated
        {
            get => PlayerPrefs.GetInt(BossKey, 0) == 1;
            set { PlayerPrefs.SetInt(BossKey, value ? 1 : 0); PlayerPrefs.Save(); }
        }

        public static void Clear()
        {
            PlayerPrefs.DeleteKey(CheckpointKey);
            PlayerPrefs.DeleteKey(BossKey);
            PlayerPrefs.Save();
        }
    }
}
