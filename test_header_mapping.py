"""Tests for src.header_mapping module."""

import pandas as pd
import pytest

from src.header_mapping import (
    standardize_headers,
    get_canonical_vocabulary,
    add_alias,
    CANONICAL_NAMES,
    _normalize_text,
    _exact_match,
    _fuzzy_match,
    _substring_match,
)


class TestNormalizeText:
    @pytest.mark.parametrize(
        "input_text,expected",
        [
            ("  Animal ID  ", "animal id"),
            ("Animal_ID", "animal id"),
            ("X-Center", "x center"),
            ("DISTANCE TRAVELLED", "distance travelled"),
            ("", ""),
        ],
    )
    def test_normalize(self, input_text, expected):
        assert _normalize_text(input_text) == expected


class TestExactMatch:
    def test_exact_match_found(self):
        lookup = {"animal id": "animal_id", "x center": "x_center"}
        assert _exact_match("Animal ID", lookup) == "animal_id"
        assert _exact_match("X Center", lookup) == "x_center"

    def test_exact_match_not_found(self):
        lookup = {"animal id": "animal_id"}
        assert _exact_match("Velocity", lookup) is None


class TestFuzzyMatch:
    def test_fuzzy_match_close(self):
        lookup = {"animal id": "animal_id", "distance travelled": "distance_travelled"}
        assert _fuzzy_match("Animal IDs", lookup, cutoff=0.8) == "animal_id"

    def test_fuzzy_match_too_different(self):
        lookup = {"animal id": "animal_id"}
        assert _fuzzy_match("Completely Different", lookup, cutoff=0.9) is None


class TestSubstringMatch:
    def test_substring_containment(self):
        lookup = {"distance travelled": "distance_travelled"}
        assert _substring_match("Total distance travelled (cm)", lookup) == "distance_travelled"

    def test_substring_no_match(self):
        lookup = {"distance travelled": "distance_travelled"}
        assert _substring_match("Time in zone", lookup) is None


class TestStandardizeHeaders:
    def test_basic_renaming(self):
        df = pd.DataFrame({
            "Animal ID": [1, 2],
            "X Center": [10, 20],
            "Distance Travelled": [100, 200],
        })
        df_out, report = standardize_headers(df)
        assert "animal_id" in df_out.columns
        assert "x_center" in df_out.columns
        assert "distance_travelled" in df_out.columns
        assert report["renamed"]["Animal ID"] == "animal_id"
        assert len(report["unmatched"]) == 0

    def test_fuzzy_renaming(self):
        df = pd.DataFrame({
            "Animl ID": [1, 2],  # typo
            "Distnce Traveld": [100, 200],  # typos
        })
        df_out, report = standardize_headers(df)
        assert "animal_id" in df_out.columns
        assert "distance_travelled" in df_out.columns

    def test_unmatched_keep_strategy(self):
        df = pd.DataFrame({
            "Animal ID": [1, 2],
            "Some Weird Column": ["a", "b"],
        })
        df_out, report = standardize_headers(df, unmatched_strategy="keep")
        assert "animal_id" in df_out.columns
        assert "Some Weird Column" in df_out.columns
        assert "Some Weird Column" in report["unmatched"]

    def test_unmatched_drop_strategy(self):
        df = pd.DataFrame({
            "Animal ID": [1, 2],
            "Some Weird Column": ["a", "b"],
        })
        df_out, report = standardize_headers(df, unmatched_strategy="drop")
        assert "animal_id" in df_out.columns
        assert "Some Weird Column" not in df_out.columns
        assert "Some Weird Column" in report["dropped"]

    def test_collision_handling(self):
        df = pd.DataFrame({
            "Animal ID": [1, 2],
            "Subject": ["A", "B"],  # also maps to animal_id
        })
        df_out, report = standardize_headers(df)
        assert "animal_id" in df_out.columns
        assert "animal_id_1" in df_out.columns
        assert "animal_id" in report["collisions"]

    def test_ethovision_style_headers(self):
        """Simulate EthoVision XT export style."""
        df = pd.DataFrame({
            "Trial": [1, 2],
            "Animal": ["rat1", "rat2"],
            "X center": [10.0, 20.0],
            "Y center": [5.0, 15.0],
            "Velocity": [0.1, 0.2],
        })
        df_out, report = standardize_headers(df)
        assert "animal_id" in df_out.columns  # Trial -> animal_id, Animal -> animal_id_1
        assert "x_center" in df_out.columns
        assert "y_center" in df_out.columns
        assert "velocity" in df_out.columns

    def test_anymaze_style_headers(self):
        """Simulate ANY-maze export style."""
        df = pd.DataFrame({
            "Distance travelled": [100, 200],
            "Time in zone": [30, 45],
            "Entries": [5, 8],
            "Latency": [10, 15],
        })
        df_out, report = standardize_headers(df)
        assert "distance_travelled" in df_out.columns
        assert "time_in_zone" in df_out.columns
        assert "entries_into_zone" in df_out.columns
        assert "latency" in df_out.columns

    def test_custom_canonical_map(self):
        custom_map = {
            "my_special_col": ["special", "spcl", "special_column"],
        }
        df = pd.DataFrame({"Special": [1, 2]})
        df_out, report = standardize_headers(df, canonical_map=custom_map)
        assert "my_special_col" in df_out.columns


class TestAddAlias:
    def test_add_alias_runtime(self):
        original_len = len(CANONICAL_NAMES.get("animal_id", []))
        add_alias("animal_id", ["creature_id", "beast_id"])
        df = pd.DataFrame({"Creature ID": [1, 2]})
        df_out, report = standardize_headers(df)
        assert "animal_id" in df_out.columns
        # Clean up
        CANONICAL_NAMES["animal_id"] = CANONICAL_NAMES["animal_id"][:-2]

    def test_add_new_canonical(self):
        add_alias("custom_measure", ["my_measure", "lab_measure"])
        df = pd.DataFrame({"My Measure": [1, 2]})
        df_out, report = standardize_headers(df)
        assert "custom_measure" in df_out.columns
        # Clean up
        if "custom_measure" in CANONICAL_NAMES:
            del CANONICAL_NAMES["custom_measure"]
