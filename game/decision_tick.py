"""
decision_tick.py
Simple DecisionTick helper to throttle heavy AI computations.
Assumes a baseline of 60 FPS; frames_per_tick computed from desired frequency.
"""

class DecisionTick:
    def __init__(self, frequency_hz: float = 10.0, baseline_fps: float = 60.0):
        self.frequency = max(0.1, float(frequency_hz))
        self.baseline_fps = float(baseline_fps)
        self.frames_per_tick = max(1, int(round(self.baseline_fps / self.frequency)))

    def should_run(self, frame_index: int) -> bool:
        # frame_index is expected to start at 0 and increment each frame
        if self.frames_per_tick <= 1:
            return True
        return (frame_index % self.frames_per_tick) == 0
