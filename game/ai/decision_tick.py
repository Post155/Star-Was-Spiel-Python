"""
decision_tick.py
Simple DecisionTick helper to throttle heavy AI computations.
"""

class DecisionTick:
    def __init__(self, frequency_hz: float = 10.0, baseline_fps: float = 60.0):
        self.frequency = max(0.1, float(frequency_hz))
        self.baseline_fps = float(baseline_fps)
        self.frames_per_tick = max(1, int(round(self.baseline_fps / self.frequency)))

    def _frequency_for_distance(self, distance: float) -> float:
        """
        Simple heuristic mapping distance -> decision frequency (Hz).
        Closer targets get higher frequencies for more responsive behavior.
        Tunable thresholds here are conservative; adjust during playtesting.
        """
        if distance is None:
            return self.frequency
        d = float(distance)
        if d < 150.0:
            return max(self.frequency, 25.0)
        if d < 300.0:
            return max(self.frequency, 15.0)
        if d < 600.0:
            return max(self.frequency, 8.0)
        if d < 1200.0:
            return max(self.frequency, 4.0)
        return max(self.frequency, 2.0)

    def should_run(self, frame_index: int, distance: float = None) -> bool:
        # compute frames_per_tick dynamically if distance provided
        if distance is not None:
            freq = self._frequency_for_distance(distance)
            frames = max(1, int(round(self.baseline_fps / float(freq))))
            return (frame_index % frames) == 0
        # fallback to static frames_per_tick
        if self.frames_per_tick <= 1:
            return True
        return (frame_index % self.frames_per_tick) == 0
