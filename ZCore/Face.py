import ZCore.ToolsSystem as ToolsSystem

'''
function: 
-contains generic face nodes method and hold important face nodes data
'''

class FaceSystem():
    
    def __init__(self):
        self.RIG_NODES_TYPE = ["eyebrow_"]

        # active node
        self.eyebrow_nodes = {}

    def mirror(self,plane="YZ"):
        pass