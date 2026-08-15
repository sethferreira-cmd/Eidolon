import sys
from pathlib import Path

# Make the repo root (containing providers/ and analysis/) importable
# from anywhere inside the app package.
_repo_root = str(Path(__file__).resolve().parent.parent.parent)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)
