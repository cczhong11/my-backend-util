from pathlib import Path
import sys
PATH = str(Path(__file__).parent.absolute())
if PATH not in sys.path:
    sys.path.append(PATH)