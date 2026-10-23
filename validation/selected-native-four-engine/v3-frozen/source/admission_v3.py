"""Reuse frozen v2 mathematical/interface checks without changing them."""
from pathlib import Path
import sys
V3=Path.cwd()/'target/selected-native-optimized/four-engine-v3'
sys.path.insert(0,str(V3.parent/'four-engine-v2'))
from admission_v2 import *
