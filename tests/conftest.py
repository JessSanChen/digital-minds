import shutil
import subprocess

import pytest


def _docker_up() -> bool:
    if not shutil.which("docker"):
        return False
    return subprocess.run(["docker", "info"], capture_output=True).returncode == 0


requires_docker = pytest.mark.skipif(not _docker_up(), reason="code affordance runs in a Docker sandbox")
