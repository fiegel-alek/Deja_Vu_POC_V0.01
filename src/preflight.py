from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
import shutil
import subprocess


@dataclass(frozen=True)
class PreflightCheck:
    name: str
    passed: bool
    message: str
    required: bool = True


def load_local_properties(path: str | Path) -> dict[str, str]:
    properties_path = Path(path)
    if not properties_path.exists():
        return {}

    properties: dict[str, str] = {}
    for line in properties_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        properties[key.strip()] = value.strip()
    return properties


def run_preflight(root: str | Path) -> list[PreflightCheck]:
    root_path = Path(root)
    local_properties = load_local_properties(root_path / "local.properties")

    return [
        _check_exists(root_path / "gradlew", "Gradle wrapper script"),
        _check_exists(root_path / "gradle" / "wrapper" / "gradle-wrapper.jar", "Gradle wrapper jar"),
        _check_exists(root_path / "gradle" / "wrapper" / "gradle-wrapper.properties", "Gradle wrapper properties"),
        _check_java(),
        _check_value(
            name="Android SDK path",
            value=os.getenv("ANDROID_HOME") or os.getenv("ANDROID_SDK_ROOT"),
            message="Set ANDROID_HOME or ANDROID_SDK_ROOT for Android builds.",
        ),
        _check_value(
            name="GitHub Packages token",
            value=os.getenv("GITHUB_TOKEN") or local_properties.get("github_token"),
            message="Set GITHUB_TOKEN or github_token in local.properties for Meta DAT packages.",
        ),
        _check_value(
            name="Meta DAT application id",
            value=os.getenv("META_DAT_APPLICATION_ID") or local_properties.get("META_DAT_APPLICATION_ID"),
            message="Set META_DAT_APPLICATION_ID in local.properties.",
        ),
        _check_value(
            name="Meta DAT client token",
            value=os.getenv("META_DAT_CLIENT_TOKEN") or local_properties.get("META_DAT_CLIENT_TOKEN"),
            message="Set META_DAT_CLIENT_TOKEN in local.properties for Display/DAM flows.",
        ),
        _check_exists(
            root_path / "third_party_refs" / "meta-wearables-dat-android" / "samples" / "CameraAccess",
            "Meta DAT CameraAccess reference",
            required=False,
        ),
        _check_exists(
            root_path / "third_party_refs" / "mediapipe-samples" / "examples" / "object_detection" / "android",
            "MediaPipe Android object detection reference",
            required=False,
        ),
    ]


def has_required_failures(checks: list[PreflightCheck]) -> bool:
    return any(check.required and not check.passed for check in checks)


def format_preflight(checks: list[PreflightCheck]) -> str:
    lines = ["Preflight checks:"]
    for check in checks:
        marker = "PASS" if check.passed else "FAIL" if check.required else "WARN"
        lines.append(f"- {marker}: {check.name} - {check.message}")
    return "\n".join(lines)


def _check_exists(path: Path, name: str, required: bool = True) -> PreflightCheck:
    return PreflightCheck(
        name=name,
        passed=path.exists(),
        message=str(path) if path.exists() else f"Missing {path}",
        required=required,
    )


def _check_command(command: str, name: str, message: str) -> PreflightCheck:
    return PreflightCheck(
        name=name,
        passed=shutil.which(command) is not None,
        message=command if shutil.which(command) is not None else message,
    )


def _check_java() -> PreflightCheck:
    if shutil.which("java") is None:
        return PreflightCheck(
            name="Java runtime / JDK",
            passed=False,
            message="Install JDK 17 for Android builds.",
        )

    result = subprocess.run(["java", "-version"], capture_output=True, text=True, timeout=5)
    output = result.stderr or result.stdout
    return PreflightCheck(
        name="Java runtime / JDK",
        passed=result.returncode == 0,
        message=output.splitlines()[0] if result.returncode == 0 and output else "Install JDK 17 for Android builds.",
    )


def _check_value(name: str, value: str | None, message: str) -> PreflightCheck:
    placeholder_values = {
        "",
        "YOUR_GITHUB_PACKAGES_TOKEN",
        "YOUR_META_DAT_APP_ID",
        "YOUR_META_DAT_CLIENT_TOKEN",
        "replace_with_meta_dat_app_id",
        "replace_with_meta_dat_client_token",
    }
    passed = value is not None and value not in placeholder_values
    return PreflightCheck(name=name, passed=passed, message="configured" if passed else message)
