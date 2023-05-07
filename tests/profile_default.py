import sys
from pathlib import Path

pathitem = Path('..').resolve().as_posix()
print(f"Adding path: {pathitem}")
sys.path.insert(0, pathitem)

def setup():
    ...
    