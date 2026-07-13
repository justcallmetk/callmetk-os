from pathlib import Path

from ctk.cli import main
from ctk.core.ai_manager import recommend_provider
from ctk.core.config import CoreConfig, load_config
from ctk.core.library import scan_library, validate_library
from ctk.core.toast import ToastDecision


def test_free_mode_defaults_to_local_provider():
    config = CoreConfig()
    decision = recommend_provider(config, "coding")
    assert decision.selection == "ollama"
    assert decision.estimated_cost_usd == 0
    assert decision.requires_approval is False
    assert decision.validate() == []


def test_free_mode_rejects_paid_only_provider():
    config = CoreConfig()
    config.ai.providers["ollama"].enabled = False
    config.ai.providers["openai"].enabled = True
    decision = recommend_provider(config, "coding", {"openai": 0.05})
    assert decision.requires_approval is True
    assert decision.confidence < 0.5


def test_toast_validation():
    decision = ToastDecision(
        target="Choose provider",
        options=["ollama"],
        selection="ollama",
        confidence=0.9,
        reasoning=["Local and free"],
        requires_approval=False,
    )
    assert decision.validate() == []


def test_ai_init_and_modes(tmp_path: Path, capsys):
    config_path = tmp_path / "config.json"
    assert main(["ai", "init", "--path", str(config_path)]) == 0
    assert main(["ai", "mode", "balanced", "--budget", "10", "--path", str(config_path)]) == 0
    config = load_config(config_path)
    assert config.ai.cost_mode == "balanced"
    assert config.ai.monthly_budget_usd == 10
    assert main(["ai", "status", "--path", str(config_path)]) == 0
    assert "balanced" in capsys.readouterr().out


def test_ai_route_outputs_toast_json(tmp_path: Path, capsys):
    config_path = tmp_path / "config.json"
    assert main(["ai", "init", "--path", str(config_path)]) == 0
    assert main(["ai", "route", "coding", "--path", str(config_path)]) == 0
    out = capsys.readouterr().out
    assert '"selection": "ollama"' in out
    assert '"estimated_cost_usd": 0.0' in out


def test_library_init_scan_validate(tmp_path: Path):
    root = tmp_path / "library"
    assert main(["library", "init", str(root)]) == 0
    song = root / "music" / "masters" / "song.wav"
    song.write_bytes(b"audio data")
    result = scan_library(root)
    assert result.indexed == 1
    assert validate_library(root) == []
    assert main(["library", "validate", str(root)]) == 0


def test_workspace_init_and_status(tmp_path: Path, capsys):
    workspace = tmp_path / "workspace"
    assert main(["workspace", "init", str(workspace)]) == 0
    assert main(["workspace", "status", str(workspace)]) == 0
    out = capsys.readouterr().out
    assert "Projects: 0" in out
    assert "Libraries: 0" in out
