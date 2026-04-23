# Backward-compatibility shim: allows `import easygopigo3` to work when the
# package is installed via pip (where easygopigo3 lives inside the gopigo3 package).
from gopigo3.easygopigo3 import *
from gopigo3.easygopigo3 import EasyGoPiGo3  # ensure explicit name is importable
