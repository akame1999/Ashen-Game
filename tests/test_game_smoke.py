"""Headless smoke tests for the Ashen Veil Pygame prototype."""
import os
import sys
import unittest
from pathlib import Path

# Configure SDL before importing/initializing Pygame, allowing CI without a display.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

GAME_DIR = Path(__file__).resolve().parents[1] / "AshenVeil_Python"
sys.path.insert(0, str(GAME_DIR))

import pygame
import main as game_module


class AshenVeilSmokeTests(unittest.TestCase):
    def setUp(self):
        self.game = game_module.Game()
        self.game.mode = "playing"

    def tearDown(self):
        pygame.quit()

    def test_killing_enemy_rewards_soul_charge_without_crashing(self):
        enemy = next(
            enemy for enemy in self.game.enemies
            if not enemy.boss and not enemy.archer
        )
        enemy.hp = 1
        before = self.game.player.soul_charge

        result = enemy.hurt(10, 1, self.game)

        self.assertTrue(result)
        self.assertTrue(enemy.dead)
        self.assertEqual(
            self.game.player.soul_charge,
            min(self.game.player.soul_max, before + 18),
        )

    def test_side_scroller_can_render_a_frame_headlessly(self):
        self.game.render()
        self.assertEqual(self.game.canvas.get_size(), (game_module.W, game_module.H))

    def test_source_uses_player_soul_limit_for_rewards(self):
        self.assertTrue(hasattr(self.game.player, "soul_max"))
        self.assertFalse(hasattr(self.game, "soul_max"))


if __name__ == "__main__":
    unittest.main()
