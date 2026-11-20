"""Regression tests using synthetic credentials only."""

import json
import os
import shutil
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from agno.media import Audio
from agno.run.agent import RunInput
from pydantic import ValidationError

from utils.validate_envs import AppSettings

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("password", [None, "", "ai"])
def test_database_rejects_missing_or_default_password(monkeypatch, tmp_path, password):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_PASS", raising=False)
    if password is not None:
        monkeypatch.setenv("DB_PASS", password)
    monkeypatch.setenv("OPENAI_API_KEY", "private-test-marker")
    with pytest.raises(ValidationError, match="DB_PASS") as error:
        AppSettings()
    assert "private-test-marker" not in str(error.value)


def test_database_builder_reads_dotenv_and_encodes_password(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DB_PASS", raising=False)
    (tmp_path / ".env").write_text("DB_PASS='example:p@ss'\n")
    from db.url import build_db_url

    assert ":example%3Ap%40ss@" in build_db_url()
    (tmp_path / ".env").write_text("")
    with pytest.raises(ValidationError, match="DB_PASS"):
        build_db_url()
    for url in ("postgres://user:%61i@localhost/db", "postgres://user@localhost/db?password=%61i"):
        monkeypatch.setenv("DATABASE_URL", url)
        with pytest.raises(ValidationError, match="DATABASE_URL"):
            build_db_url()


def test_database_entrypoint_checks_password_before_startup(tmp_path):
    entrypoint = tmp_path / "docker-entrypoint.sh"
    entrypoint.write_text('#!/bin/sh\nexec "$@"\n')
    entrypoint.chmod(0o755)
    command = ["sh", "scripts/postgres-entrypoint.sh", "true"]
    for password in ("", " ", "ai", "local-test-only"):
        env = {"PATH": f"{tmp_path}:{os.defpath}", "POSTGRES_PASSWORD": password}
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True)
        assert (result.returncode == 0) == (password == "local-test-only")


def test_entrypoint_does_not_echo_environment_or_command_arguments():
    marker = "private-test-marker"
    result = subprocess.run(
        ["bash", "-x", "scripts/entrypoint.sh", "test", marker, "=", marker],
        cwd=ROOT,
        env={"PATH": os.defpath, "PRINT_ENV_ON_LOAD": "True", "OPENAI_API_KEY": marker},
        capture_output=True,
        text=True,
        check=True,
    )
    assert marker not in result.stdout + result.stderr


def test_railway_setup_passes_api_key_only_on_stdin(tmp_path):
    marker = "private-test-marker"
    (tmp_path / ".env").write_text(f"OPENAI_API_KEY={marker}\n")
    cli = tmp_path / "railway"
    cli.write_text(
        "#!/bin/sh\n"
        'echo "$@"\n'
        'if [ "$1" = variable ]; then\n'
        '  [ "$2 $3 $4" = "set OPENAI_API_KEY --stdin" ] && [ "$(cat)" = "$OPENAI_API_KEY" ] || exit 1\n'
        '  echo "key received"\n'
        "fi\n"
    )
    cli.chmod(0o755)
    (tmp_path / "sleep").symlink_to(shutil.which("true") or "/bin/true")
    result = subprocess.run(
        ["bash", "-x", str(ROOT / "scripts/railway_up.sh")],
        cwd=tmp_path,
        env={"PATH": f"{tmp_path}:{os.defpath}"},
        text=True,
        capture_output=True,
        check=True,
    )
    assert "key received" in result.stdout
    assert marker not in result.stdout + result.stderr


def test_whatsapp_keeps_message_and_provider_details_out_of_logs(monkeypatch, caplog):
    from agno.os.interfaces.whatsapp import helpers, router

    from app.interfaces import _configure_whatsapp_adapter

    for module in (helpers, router):
        for attr in ("log_info", "log_warning", "log_error"):
            monkeypatch.setattr(module, attr, getattr(module, attr))
    monkeypatch.setattr(router, "send_whatsapp_message_async", router.send_whatsapp_message_async)
    _configure_whatsapp_adapter()
    marker = "private-test-marker"
    with caplog.at_level("INFO"):
        parsed = helpers.extract_message_content({"type": "text", "text": {"body": marker}})
        assert parsed and parsed.text == marker
        helpers.log_warning(marker)
        router.log_error(marker)
    assert "WhatsApp request failed" in caplog.text
    assert marker not in caplog.text


def test_provider_and_database_exceptions_keep_details_out_of_logs(monkeypatch):
    monkeypatch.setenv("DB_PASS", "local-test-only")
    from agents.hooks import prepare_multimodal_input
    from db.schema import repair_agentos_db_schema

    error = ValueError("private-test-marker")
    with (
        patch("agents.hooks.media._transcribe_audio", side_effect=error),
        patch("agents.hooks.media.log_warning") as log,
    ):
        prepare_multimodal_input(RunInput(input_content="", audios=[Audio(content=b"test")]))
        log.assert_called_once_with("audio transcription failed for audio #1: ValueError", exc_info=False)
    with (
        patch("db.schema.ensure_approvals_run_status_column", side_effect=error),
        patch("db.schema.log_warning") as log,
    ):
        repair_agentos_db_schema(Mock())
        log.assert_called_once_with("AgentOS database schema repair skipped: ValueError", exc_info=False)


@pytest.mark.skipif(shutil.which("docker") is None, reason="requires Docker Compose")
def test_compose_requires_password_and_keeps_database_internal():
    command = ["docker", "compose", "--env-file", os.devnull, "config", "--format", "json"]
    env = {"PATH": os.environ["PATH"], "OPENAI_API_KEY": "example"}
    for empty in ({}, {"DB_PASS": ""}):
        result = subprocess.run(command, cwd=ROOT, env=env | empty, capture_output=True, text=True)
        assert result.returncode != 0 and "DB_PASS" in result.stderr
    password = "local-test-only"
    result = subprocess.run(
        command, cwd=ROOT, env=env | {"DB_PASS": password}, capture_output=True, text=True, check=True
    )
    services = json.loads(result.stdout)["services"]
    db, api = services["agentos-db"], services["agentos-api"]
    assert db["environment"]["POSTGRES_PASSWORD"] == api["environment"]["DB_PASS"] == password
    assert not db.get("ports") and api["environment"]["DB_HOST"] == "agentos-db"
    assert "--no-access-log" in api["command"]


def test_postgres_container_authentication(tmp_path):
    if not shutil.which("docker") or subprocess.run(["docker", "info"], capture_output=True).returncode:
        if os.getenv("GITHUB_ACTIONS") == "true":
            pytest.fail("Docker is required for the PostgreSQL integration check on GitHub Actions")
        pytest.skip("requires a running Docker daemon")
    subprocess.run(["bash", "tests/postgres-compose.sh", str(tmp_path / "override.yml")], cwd=ROOT, check=True)
