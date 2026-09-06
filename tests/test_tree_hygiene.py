"""Product-tree hygiene: vault folders and stale artefacts must stay out."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

VAULT_IGNORE_PATHS = [
    "00_Master/",
    "01_Obi-Wan/",
    "02_Sub-Agents/",
    "03_Context/",
    "04_Daily_Logs/",
    "05_Skills/",
    "05_Studies/",
    "Anakin/",
    "Chat Logs/",
    "July 2026/",
    "masters-profile/",
    "projects/",
]


def test_gitignore_excludes_vault_folders() -> None:
    text = (REPO / ".gitignore").read_text(encoding="utf-8")
    for path in VAULT_IGNORE_PATHS:
        assert path in text, f".gitignore must exclude {path}"
    assert "dist/" in text
    assert "db_bridge-*" in text


def test_working_tree_has_no_vault_or_stale_dist() -> None:
    for path in VAULT_IGNORE_PATHS:
        assert not (REPO / path.rstrip("/")).exists(), f"do not ship {path}"
    assert not (REPO / "dist").exists() or not any((REPO / "dist").iterdir())
    stale = list(REPO.glob("db_bridge-1.0.0*")) + list(REPO.glob("db-bridge-1.0.0*"))
    assert stale == []
