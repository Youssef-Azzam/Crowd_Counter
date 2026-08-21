from people_counter.config_runtime import load_config


def test_load_config_merges_nested_values(tmp_path):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        """
detector:
  model_path: yolo11s.pt
tracker:
  backend: botsort
analytics:
  lines:
    - name: entrance
      start: [1, 2]
      end: [3, 4]
      in_direction: positive_to_negative
""",
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.detector.model_path == "yolo11s.pt"
    assert config.detector.confidence == 0.5
    assert config.tracker.backend == "botsort"
    assert config.analytics.lines[0].name == "entrance"
    assert config.analytics.lines[0].start == (1, 2)
