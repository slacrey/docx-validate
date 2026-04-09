from pathlib import Path
import shutil
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_dev_script_requires_local_virtualenv(tmp_path):
    source_script = REPO_ROOT / "scripts" / "dev.sh"
    temp_repo = tmp_path / "repo"
    temp_scripts = temp_repo / "scripts"
    temp_scripts.mkdir(parents=True)
    temp_script = temp_scripts / "dev.sh"
    shutil.copy2(source_script, temp_script)

    result = subprocess.run(
        ["bash", str(temp_script)],
        cwd=temp_repo,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "Missing virtual environment" in result.stderr
    assert "make install" in result.stderr


def test_makefile_exposes_common_dev_targets():
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    for target in ["venv:", "install:", "test:", "run:", "clean:"]:
        assert target in makefile

    assert "scripts/dev.sh" in makefile
