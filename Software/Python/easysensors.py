# Backward-compatibility shim: allows `import easysensors` to work when the
# package is installed via pip (where easysensors lives inside the gopigo3 package).
from gopigo3.easysensors import *
