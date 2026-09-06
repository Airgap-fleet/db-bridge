"""Packaging honesty: UNSIGNED INTERNAL labels and protocol-only caveat."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_readme_leads_with_installer_and_caveat() -> None:
    text = (REPO / "README.md").read_text(encoding="utf-8")
    assert "UNSIGNED INTERNAL" in text
    assert "Install-DbBridge.ps1" in text
    assert "protocol-only" in text.lower()
    assert "full tool coverage" in text.lower()
    installer_pos = text.find("Install-DbBridge.ps1")
    uvx_pos = text.lower().find("uvx")
    assert installer_pos != -1
    assert uvx_pos == -1 or installer_pos < uvx_pos


def test_installer_scripts_labelled_unsigned_internal() -> None:
    install = (REPO / "installer" / "Install-DbBridge.ps1").read_text(encoding="utf-8")
    uninstall = (REPO / "installer" / "Uninstall-DbBridge.ps1").read_text(encoding="utf-8")
    readme = (REPO / "installer" / "README.md").read_text(encoding="utf-8")
    assert "UNSIGNED INTERNAL" in install
    assert "UNSIGNED INTERNAL" in uninstall
    assert "UNSIGNED INTERNAL" in readme


def test_signing_and_self_test_honesty() -> None:
    signing = (REPO / "proof-pack" / "SIGNING.md").read_text(encoding="utf-8")
    self_test = (REPO / "scripts" / "self_test.py").read_text(encoding="utf-8")
    assert "UNSIGNED INTERNAL" in signing
    assert "thumbprint" in signing.lower()
    assert "protocol-only" in self_test.lower() or "protocol_only" in self_test
    assert "full tool coverage" in self_test.lower()
