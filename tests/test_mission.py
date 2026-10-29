import math
import unittest

from app.mission import (
    CYCLE_DURATION,
    DRONE_PAD,
    HELI_PAD,
    MEETING,
    OFFSET,
    STAGES,
    Mission,
    sample,
)


class MissionTests(unittest.TestCase):
    def test_frame_rate_independence(self):
        positions = []
        for fps in (24, 30, 60, 144):
            mission = Mission()
            for _ in range(fps * 24):
                mission.advance(1 / fps)
            positions.append(mission.pose)
        for pose in positions:
            self.assertEqual(pose.stage_index, 5)
            self.assertLess(math.dist(pose.helicopter, positions[0].helicopter), 1e-10)
            self.assertLess(math.dist(pose.drone, positions[0].drone), 1e-10)

    def test_pause_resume_and_reset(self):
        mission = Mission()
        mission.advance(15)
        before = mission.pose
        mission.paused = True
        mission.advance(200)
        self.assertEqual(mission.pose, before)
        mission.paused = False
        mission.advance(1)
        self.assertEqual(mission.time, 16)
        mission.reset()
        self.assertEqual(mission.pose.helicopter, HELI_PAD)
        self.assertEqual(mission.pose.drone, DRONE_PAD)

    def test_drone_waits_for_helicopter(self):
        for t in (0, 2, 5, 7, 10.99):
            self.assertEqual(sample(t).drone, DRONE_PAD)
        self.assertGreater(sample(12).drone[1], DRONE_PAD[1])
        self.assertEqual(sample(12).helicopter, MEETING)

    def test_inspection_before_departure(self):
        for t in (14, 15, 17, 19.99):
            pose = sample(t)
            self.assertEqual(pose.helicopter, MEETING)
            self.assertAlmostEqual(
                math.dist(pose.drone, pose.helicopter), math.sqrt(sum(v * v for v in OFFSET))
            )
        self.assertNotEqual(sample(15).drone, sample(17).drone)
        self.assertNotEqual(sample(21).helicopter, MEETING)

    def test_escort_relative_position(self):
        for t in (20, 21, 23, 25.99):
            pose = sample(t)
            for a, b, offset in zip(pose.helicopter, pose.drone, OFFSET):
                self.assertAlmostEqual(b - a, offset)

    def test_continuity_all_boundaries_including_loop(self):
        boundary = 0
        for stage in STAGES:
            boundary += stage.duration
            before, after = sample(boundary - 1e-6), sample(boundary + 1e-6)
            self.assertLess(math.dist(before.helicopter, after.helicopter), 1e-4)
            self.assertLess(math.dist(before.drone, after.drone), 1e-4)
            for a, b in [
                (before.helicopter_yaw, after.helicopter_yaw),
                (before.drone_yaw, after.drone_yaw),
            ]:
                self.assertLess(abs((a - b + math.pi) % math.tau - math.pi), 1e-4)

    def test_large_step_and_speed(self):
        mission = Mission()
        mission.speed = 2
        mission.advance(CYCLE_DURATION * 2 + 8)
        self.assertEqual(mission.pose.cycle, 4)
        self.assertEqual(mission.pose.stage_index, 4)

    def test_stage_shortcut_and_cycle(self):
        mission = Mission()
        for i in range(1, len(STAGES) + 1):
            mission.next_stage()
            self.assertEqual(mission.pose.stage_index, i % len(STAGES))
        self.assertEqual(mission.pose.cycle, 1)

    def test_finite_positions_and_separation(self):
        for tick in range(int(CYCLE_DURATION * 60)):
            pose = sample(tick / 60)
            self.assertGreater(math.dist(pose.helicopter, pose.drone), 2.5)
            self.assertGreaterEqual(pose.helicopter[1], 0.16 - 1e-6)
            self.assertGreaterEqual(pose.drone[1], 0.16 - 1e-6)
            self.assertTrue(all(math.isfinite(v) for v in (*pose.helicopter, *pose.drone)))

    def test_invalid_time(self):
        for value in (-1, float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                sample(value)
            with self.assertRaises(ValueError):
                Mission().advance(value)


if __name__ == "__main__":
    unittest.main()
