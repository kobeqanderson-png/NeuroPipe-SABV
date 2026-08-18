"""Tests for src.artifact_detection module."""

import numpy as np
import pandas as pd
import pytest

from src.artifact_detection import (
    detect_artifacts,
    _detect_velocity_spikes,
    _detect_tracking_dropouts,
    _detect_coordinate_jumps,
    _detect_missing_patterns,
    _detect_out_of_bounds,
    DEFAULT_THRESHOLDS,
)


class TestVelocitySpikes:
    def test_detects_high_velocity(self):
        df = pd.DataFrame({"velocity": [0.1, 0.5, 3.0, 0.2]})
        flags = _detect_velocity_spikes(df, "velocity", max_vel=2.0, min_vel=0.0)
        assert flags.tolist() == [False, False, True, False]

    def test_detects_negative_velocity(self):
        df = pd.DataFrame({"velocity": [0.1, -0.5, 0.2]})
        flags = _detect_velocity_spikes(df, "velocity", max_vel=2.0, min_vel=0.0)
        assert flags.tolist() == [False, True, False]

    def test_missing_column_returns_all_false(self):
        df = pd.DataFrame({"other": [1, 2, 3]})
        flags = _detect_velocity_spikes(df, "velocity", max_vel=2.0, min_vel=0.0)
        assert not flags.any()


class TestTrackingDropouts:
    def test_detects_frozen_coordinates(self):
        df = pd.DataFrame({
            "animal_id": [1, 1, 1, 1, 1, 1],
            "x_center": [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            "y_center": [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        })
        flags = _detect_tracking_dropouts(df, "x_center", "y_center", "animal_id", max_identical=5)
        # First frame can't be flagged (no previous), then frames 2-5 are identical to previous
        # Run length of identical frames: frame 2 (1), 3 (2), 4 (3), 5 (4) — none reach 5
        # Actually run_length is count of consecutive identical INCLUDING current
        # Frame 2: same as 1 → run=2, Frame 3: run=3, Frame 4: run=4, Frame 5: run=5 → flagged
        assert flags.iloc[4]  # 5th frame (0-indexed: 4) should be flagged
        assert not flags.iloc[0]
        assert not flags.iloc[5]

    def test_no_dropouts(self):
        df = pd.DataFrame({
            "animal_id": [1, 1, 1],
            "x_center": [0.0, 0.1, 0.2],
            "y_center": [0.0, 0.1, 0.2],
        })
        flags = _detect_tracking_dropouts(df, "x_center", "y_center", "animal_id", max_identical=5)
        assert not flags.any()


class TestCoordinateJumps:
    def test_detects_large_jump(self):
        df = pd.DataFrame({
            "animal_id": [1, 1, 1],
            "x_center": [0.0, 0.0, 1.0],
            "y_center": [0.0, 0.0, 0.0],
        })
        flags = _detect_coordinate_jumps(df, "x_center", "y_center", "animal_id", max_jump=0.5)
        assert flags.tolist() == [False, False, True]

    def test_no_jump(self):
        df = pd.DataFrame({
            "animal_id": [1, 1, 1],
            "x_center": [0.0, 0.01, 0.02],
            "y_center": [0.0, 0.01, 0.02],
        })
        flags = _detect_coordinate_jumps(df, "x_center", "y_center", "animal_id", max_jump=0.5)
        assert not flags.any()


class TestMissingPatterns:
    def test_detects_missing_values(self):
        df = pd.DataFrame({
            "x_center": [0.0, np.nan, 0.2],
            "y_center": [0.0, 0.1, 0.2],
            "velocity": [0.1, 0.2, np.nan],
        })
        flags = _detect_missing_patterns(df, ["x_center", "y_center", "velocity"])
        assert flags.tolist() == [False, True, True]

    def test_no_missing(self):
        df = pd.DataFrame({
            "x_center": [0.0, 0.1, 0.2],
            "y_center": [0.0, 0.1, 0.2],
        })
        flags = _detect_missing_patterns(df, ["x_center", "y_center"])
        assert not flags.any()


class TestOutOfBounds:
    def test_detects_out_of_bounds(self):
        df = pd.DataFrame({
            "x_center": [0.5, 1.5, -0.1],
            "y_center": [0.5, 0.5, 0.5],
        })
        flags = _detect_out_of_bounds(df, "x_center", "y_center", arena_bounds=(0, 1, 0, 1))
        assert flags.tolist() == [False, True, True]

    def test_heuristic_bounds(self):
        df = pd.DataFrame({
            "x_center": [0.0] * 99 + [100.0],
            "y_center": [0.0] * 100,
        })
        flags = _detect_out_of_bounds(df, "x_center", "y_center", arena_bounds=None)
        assert flags.iloc[-1]
        assert not flags.iloc[:-1].any()


class TestDetectArtifactsIntegration:
    def test_full_pipeline_clean_data(self):
        df = pd.DataFrame({
            "animal_id": [1, 1, 1, 2, 2, 2],
            "x_center": [0.0, 0.1, 0.2, 0.0, 0.1, 0.2],
            "y_center": [0.0, 0.1, 0.2, 0.0, 0.1, 0.2],
            "velocity": [0.1, 0.15, 0.12, 0.1, 0.15, 0.12],
        })
        report = detect_artifacts(df)
        assert report["summary"]["any_flag"] == 0
        assert report["summary"]["flag_rate"] == 0.0
        assert len(report["recommendations"]) == 0

    def test_full_pipeline_with_all_artifacts(self):
        df = pd.DataFrame({
            "animal_id": [1, 1, 1, 1, 1, 1],
            "x_center": [0.0, 0.0, 0.0, 0.0, 0.0, 2.0],
            "y_center": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "velocity": [0.1, 0.1, 0.1, 0.1, 0.1, 5.0],
        })
        report = detect_artifacts(
            df,
            arena_bounds=(0, 1, 0, 1),
            thresholds={"max_consecutive_identical_frames": 5},
        )
        assert report["summary"]["velocity_spikes"] == 1
        assert report["summary"]["tracking_dropouts"] == 1  # frame 4 (0-indexed: 4)
        assert report["summary"]["coordinate_jumps"] == 1
        assert report["summary"]["out_of_bounds"] == 1
        assert report["summary"]["any_flag"] > 0
        assert len(report["recommendations"]) > 0
        assert len(report["flagged_df"]) > 0

    def test_missing_column_graceful(self):
        df = pd.DataFrame({"other": [1, 2, 3]})
        report = detect_artifacts(df)
        assert report["summary"]["total_rows"] == 3
        assert report["summary"]["any_flag"] == 0

    def test_custom_thresholds(self):
        df = pd.DataFrame({
            "animal_id": [1, 1, 1],
            "x_center": [0.0, 0.0, 0.0],
            "y_center": [0.0, 0.0, 0.0],
            "velocity": [0.1, 0.1, 0.1],
        })
        report = detect_artifacts(df, thresholds={"max_consecutive_identical_frames": 2})
        assert report["summary"]["tracking_dropouts"] > 0
