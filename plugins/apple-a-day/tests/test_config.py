"""Tests for apple-a-day config."""

from pathlib import Path
from unittest.mock import patch

from apple_a_day.config import load_config, remote_storage_status, set_remote_folder


def test_load_config_defaults_when_missing(tmp_path: Path) -> None:
    with patch("apple_a_day.config.CONFIG_PATH", tmp_path / "missing.json"):
        config = load_config()

    assert config["storage"]["remote_folder"] is None
    assert config["storage"]["provider"] == "mounted-folder"
    assert config["storage"]["rclone_remote"] is None
    assert config["storage"]["min_boot_free_gb"] == 50


def test_set_remote_folder_creates_and_persists(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    target = tmp_path / "external" / "clouds"

    with (
        patch("apple_a_day.config.CONFIG_DIR", tmp_path),
        patch("apple_a_day.config.CONFIG_PATH", config_path),
    ):
        config = set_remote_folder(
            target,
            create=True,
            provider="rclone",
            rclone_remote="clouds:",
        )
        loaded = load_config()

    assert target.is_dir()
    assert config["storage"]["remote_folder"] == str(target)
    assert config["storage"]["provider"] == "rclone"
    assert config["storage"]["rclone_remote"] == "clouds:"
    assert loaded["storage"]["remote_folder"] == str(target)
    assert loaded["storage"]["provider"] == "rclone"
    assert loaded["storage"]["rclone_remote"] == "clouds:"


def test_remote_storage_status_unconfigured() -> None:
    status = remote_storage_status({"storage": {"remote_folder": None}})

    assert status == {"configured": False}


def test_remote_storage_status_missing_path(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    status = remote_storage_status({"storage": {"remote_folder": str(missing)}})

    assert status["configured"] is True
    assert status["exists"] is False
