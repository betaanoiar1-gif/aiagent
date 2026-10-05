"""Validation tests for Software Profiler and Security Redaction."""

from runtime.profiler.software import SoftwareProfiler


def test_software_profiler_discovery():
    """Verify software profiler records runtime versions and git repository state."""
    profiler = SoftwareProfiler()
    profile = profiler.profile()

    assert profile.os_name in {"Linux", "Darwin", "Windows"}
    assert profile.python_version.startswith("3.")
    assert len(profile.git_state.commit) == 40 or profile.git_state.commit == "unknown"
    assert profile.git_state.branch != ""
    assert isinstance(profile.installed_packages, dict)
    assert len(profile.installed_packages) > 0


def test_software_fingerprint_stability():
    """Verify software fingerprint is reproducible."""
    profiler = SoftwareProfiler()
    p1 = profiler.profile()
    p2 = profiler.profile()

    assert p1.software_fingerprint.startswith("swfp_")
    assert p1.software_fingerprint == p2.software_fingerprint


def test_sensitive_environment_variable_redaction(monkeypatch):
    """Verify that secrets, tokens, and passwords in environment variables are NEVER recorded."""
    monkeypatch.setenv("SECRET_API_KEY", "super_secret_token_123")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "hidden_key_456")
    monkeypatch.setenv("DB_PASSWORD", "mypassword")
    monkeypatch.setenv("RESEARCH_TRIAL_MODE", "enabled")

    profiler = SoftwareProfiler()
    profile = profiler.profile()

    captured_keys = profile.environment_variables.keys()
    assert "SECRET_API_KEY" not in captured_keys
    assert "AWS_SECRET_ACCESS_KEY" not in captured_keys
    assert "DB_PASSWORD" not in captured_keys
    assert "RESEARCH_TRIAL_MODE" in captured_keys
    assert profile.environment_variables["RESEARCH_TRIAL_MODE"] == "enabled"
