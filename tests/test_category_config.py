"""Pruebas unitarias para load_category_config (TK-003 US-002)."""

from __future__ import annotations

from pathlib import Path

import pytest

from smart_api_search.cli.ingest import load_category_config


class TestLoadCategoryConfig:
    def test_valid_entry_with_title_and_description(self, tmp_path: Path) -> None:
        cfg = tmp_path / "categories.yaml"
        cfg.write_text("payments:\n  title: Payments\n  description: Pay endpoints\n")
        result = load_category_config(str(cfg))
        assert result["payments"]["title"] == "Payments"
        assert result["payments"]["description"] == "Pay endpoints"

    def test_entry_without_title(self, tmp_path: Path) -> None:
        cfg = tmp_path / "categories.yaml"
        cfg.write_text("users:\n  description: User mgmt\n")
        result = load_category_config(str(cfg))
        assert "title" not in result["users"]
        assert result["users"]["description"] == "User mgmt"

    def test_empty_file_returns_empty_dict(self, tmp_path: Path) -> None:
        cfg = tmp_path / "categories.yaml"
        cfg.write_text("")
        assert load_category_config(str(cfg)) == {}

    def test_multiple_categories_all_loaded(self, tmp_path: Path) -> None:
        cfg = tmp_path / "categories.yaml"
        cfg.write_text("a:\n  title: A\nb:\n  title: B\n")
        result = load_category_config(str(cfg))
        assert set(result.keys()) == {"a", "b"}

    def test_missing_file_raises_system_exit(self, tmp_path: Path) -> None:
        with pytest.raises(SystemExit) as exc_info:
            load_category_config(str(tmp_path / "nonexistent.yaml"))
        assert exc_info.value.code == 1

    def test_missing_file_message_contains_path(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        path = str(tmp_path / "nonexistent.yaml")
        with pytest.raises(SystemExit):
            load_category_config(path)
        captured = capsys.readouterr()
        assert path in captured.err

    def test_invalid_yaml_raises_system_exit(self, tmp_path: Path) -> None:
        cfg = tmp_path / "categories.yaml"
        cfg.write_text("key: [\n  - bad\n")
        with pytest.raises(SystemExit) as exc_info:
            load_category_config(str(cfg))
        assert exc_info.value.code == 1

    def test_invalid_yaml_message_contains_path_and_cause(
        self, tmp_path: Path, capsys: pytest.CaptureFixture[str]
    ) -> None:
        cfg = tmp_path / "categories.yaml"
        cfg.write_text("key: [\n  - bad\n")
        with pytest.raises(SystemExit):
            load_category_config(str(cfg))
        captured = capsys.readouterr()
        assert str(cfg) in captured.err
