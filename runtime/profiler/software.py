"""Software Environment Profiler for Phase 0 Research Foundation.

Captures Python runtime, operating system distribution, kernel details,
installed package manifests, Git repository state (commit, branch, dirty tree),
and non-sensitive runtime environment variables.
"""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


SENSITIVE_ENV_KEYWORDS = {
    "KEY",
    "TOKEN",
    "SECRET",
    "PASSWORD",
    "PASS",
    "AUTH",
    "CREDENTIAL",
    "PRIVATE",
    "SIGNATURE",
    "BEARER",
}


@dataclass
class GitState:
    """Git repository snapshot."""
    commit: str
    branch: str
    is_dirty: bool
    dirty_files: List[str] = field(default_factory=list)
    commit_timestamp: Optional[str] = None
    commit_author: Optional[str] = None
    commit_summary: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "commit": self.commit,
            "branch": self.branch,
            "is_dirty": self.is_dirty,
            "dirty_files": self.dirty_files,
            "commit_timestamp": self.commit_timestamp,
            "commit_author": self.commit_author,
            "commit_summary": self.commit_summary,
        }


@dataclass
class SoftwareProfile:
    """Comprehensive representation of the software execution environment."""
    os_name: str
    os_release: str
    os_distro: str
    kernel_version: str
    python_version: str
    python_executable: str
    python_implementation: str
    git_state: GitState
    installed_packages: Dict[str, str] = field(default_factory=dict)
    environment_variables: Dict[str, str] = field(default_factory=dict)
    software_fingerprint: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "software_fingerprint": self.software_fingerprint,
            "os_name": self.os_name,
            "os_release": self.os_release,
            "os_distro": self.os_distro,
            "kernel_version": self.kernel_version,
            "python_version": self.python_version,
            "python_executable": self.python_executable,
            "python_implementation": self.python_implementation,
            "git_state": self.git_state.to_dict(),
            "installed_packages": self.installed_packages,
            "environment_variables": self.environment_variables,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, sort_keys=True)


class SoftwareProfiler:
    """Probes the execution environment to build a detailed SoftwareProfile."""

    def __init__(self, repo_path: str = ".") -> None:
        self.repo_path = repo_path

    def profile(self) -> SoftwareProfile:
        """Capture the complete software environment profile."""
        os_distro = self._detect_os_distro()
        git_state = self._detect_git_state()
        packages = self._detect_packages()
        env_vars = self._detect_env_vars()

        kernel = platform.uname().release or platform.release()

        profile = SoftwareProfile(
            os_name=platform.system(),
            os_release=platform.release(),
            os_distro=os_distro,
            kernel_version=kernel,
            python_version=platform.python_version(),
            python_executable=sys.executable,
            python_implementation=platform.python_implementation(),
            git_state=git_state,
            installed_packages=packages,
            environment_variables=env_vars,
        )

        profile.software_fingerprint = self.compute_fingerprint(profile)
        return profile

    def compute_fingerprint(self, profile: SoftwareProfile) -> str:
        """Generate a deterministic SHA-256 fingerprint for the software environment."""
        # Focus on core reproducible aspects: python ver, git commit, core packages
        key_pkgs = sorted(
            [f"{k}=={v}" for k, v in profile.installed_packages.items() if k in {"pytest", "psutil", "torch", "numpy"}]
        )
        parts = [
            f"python:{profile.python_version}",
            f"git:{profile.git_state.commit}",
            f"dirty:{profile.git_state.is_dirty}",
            f"packages:{';'.join(key_pkgs)}",
        ]
        raw_string = "|".join(parts)
        digest = hashlib.sha256(raw_string.encode("utf-8")).hexdigest()
        return f"swfp_{digest[:32]}"

    def _detect_os_distro(self) -> str:
        """Read distribution identity cleanly."""
        if hasattr(platform, "freedesktop_os_release"):
            try:
                info = platform.freedesktop_os_release()
                return info.get("PRETTY_NAME", info.get("NAME", "Linux"))
            except Exception:
                pass

        if os.path.exists("/etc/os-release"):
            try:
                with open("/etc/os-release", "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            return line.split("=", 1)[1].strip().strip('"')
            except Exception:
                pass

        return f"{platform.system()} {platform.release()}"

    def _detect_git_state(self) -> GitState:
        """Extract Git repository metadata."""
        try:
            # Commit hash
            proc_commit = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            commit = proc_commit.stdout.strip() if proc_commit.returncode == 0 else "unknown"

            # Branch name
            proc_branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            branch = proc_branch.stdout.strip() if proc_branch.returncode == 0 else "unknown"

            # Working tree dirty status
            proc_status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            dirty_files: List[str] = []
            is_dirty = False
            if proc_status.returncode == 0:
                lines = [l.strip() for l in proc_status.stdout.splitlines() if l.strip()]
                if lines:
                    is_dirty = True
                    dirty_files = lines

            # Last commit metadata
            proc_meta = subprocess.run(
                ["git", "log", "-1", "--format=%cI|%an|%s"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False,
            )
            commit_ts = None
            author = None
            summary = None
            if proc_meta.returncode == 0 and proc_meta.stdout.strip():
                parts = proc_meta.stdout.strip().split("|", 2)
                if len(parts) >= 1:
                    commit_ts = parts[0]
                if len(parts) >= 2:
                    author = parts[1]
                if len(parts) >= 3:
                    summary = parts[2]

            return GitState(
                commit=commit,
                branch=branch,
                is_dirty=is_dirty,
                dirty_files=dirty_files,
                commit_timestamp=commit_ts,
                commit_author=author,
                commit_summary=summary,
            )
        except Exception:
            return GitState(
                commit="unavailable",
                branch="unavailable",
                is_dirty=False,
                dirty_files=[],
            )

    def _detect_packages(self) -> Dict[str, str]:
        """List all installed Python distribution packages and their versions."""
        packages: Dict[str, str] = {}
        try:
            for dist in importlib.metadata.distributions():
                name = dist.metadata["Name"] or dist.name
                packages[name] = dist.version
        except Exception:
            pass
        return dict(sorted(packages.items()))

    def _detect_env_vars(self) -> Dict[str, str]:
        """Capture select non-sensitive environment variables."""
        allowed_exact = {
            "PATH",
            "PYTHONPATH",
            "CUDA_VISIBLE_DEVICES",
            "OMP_NUM_THREADS",
            "MKL_NUM_THREADS",
            "LANG",
            "LC_ALL",
            "SHELL",
            "TERM",
            "USER",
        }

        captured: Dict[str, str] = {}
        for k, v in os.environ.items():
            upper = k.upper()
            # Omit any secret-looking variable
            if any(keyword in upper for keyword in SENSITIVE_ENV_KEYWORDS):
                continue
            if k in allowed_exact or upper.startswith("RESEARCH_") or upper.startswith("RUNTIME_"):
                captured[k] = v

        return dict(sorted(captured.items()))
