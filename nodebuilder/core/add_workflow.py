"""Copy workflow templates bundled inside the package into the user's project."""
from __future__ import annotations

from pathlib import Path
from importlib import resources


def _get_template_root() -> resources.Traversable:
    """Return a Traversable pointing to the package `templates` directory."""
    pkg = resources.files("nodebuilder")
    tpl = pkg.joinpath("templates")
    return tpl


def _copy_traversable(src: resources.Traversable, dest_path: Path) -> None:
    """Recursively copy a Traversable (package resource) into dest_path."""
    if src.is_file():
        # ensure parent exists
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_bytes()
        dest_path.write_bytes(data)
    else:
        dest_path.mkdir(parents=True, exist_ok=True)
        for child in src.iterdir():
            _copy_traversable(child, dest_path / child.name)


def add_workflow(name: str) -> None:
    """Copy a workflow template `templates/workflows/<name>/` into `./workflows/<name>/`.

    Raises FileNotFoundError if the template does not exist.
    """
    tpl_root = _get_template_root()
    workflow_tpl = tpl_root.joinpath("workflows").joinpath(name)
    if not workflow_tpl.exists():
        raise FileNotFoundError(
            f"Template workflow '{name}' not found in package templates. "
            f"Available workflows: {[p.name for p in tpl_root.joinpath('workflows').iterdir() if p.is_dir()]}"
        )

    target_dir = Path.cwd() / "workflows" / name
    if target_dir.exists():
        raise FileExistsError(f"Target directory {target_dir} already exists. Remove it first or choose another workflow name.")

    _copy_traversable(workflow_tpl, target_dir)
    print(f"Workflow '{name}' added to {target_dir}")
