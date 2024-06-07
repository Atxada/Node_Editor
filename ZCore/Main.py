import inspect
import os
import sys

'============================ redirect system path for maya (placeholder) ============================'
sys.path.insert(0, "C:/Users/atxad/Desktop/Maya Scripts Draft/1st Album EPILOGUE/Face Tools/ZenoRig")
sys.dont_write_bytecode = True  # prevent by bytecode python being generated (.pyc)

# extend PYTHONPATH so app executable inside command prompt (optional)
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))    # go 2 level above, hard-coded
'====================================================================================================='

"""
from PySide2 import QtCore, QtGui, QtWidgets

from ZCore.UI import ZenoMainWindow
from GUI.node_editor import NodeEditorWindow
from GUI.utils import loadStylesheet
"""

''' MIGHT DELETE LATER 
# load node editor
if __name__ == "__main__":
    
    try:
        window.close()
        window.deleteLater()    # override inside closeEvent mainWindow
    except:
        pass
    
    #print (QtWidgets.QStyleFactory.keys())
    window = ZenoMainWindow()
    #QtWidgets.QApplication.setStyle('windows')
    #module_path = os.path.dirname(inspect.getfile(window.__class__))   # retrieve file path where this class is located in disk
    #loadStylesheet(window, os.path.join(module_path, 'Sources/style/nodestyle.qss')) # append path with qss sub path

    window.show()
'''

print ("ZCore package initialized"),