import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui

# flag definition
kMeshFlag = "-m"
kMeshLongFlag = "-mesh"

# maya api 2.0
def maya_useNewAPI():
    pass

class RibbonContext(omui.MPxContext):

    def __init__(self):
        super(RibbonContext, self).__init__()
        
    def toolOnSetup(self,event):
        om.MGlobal.selectCommand(om.MSelectionList()) 
        self.reset_context()
        
    def toolOffCleanup(self):
        self.reset_context()

    def doPress(self, event, draw_manager, frame_context):
        print ("do press")
          
    def completeAction(self):
        print ("complete action")
        
    def deleteAction(self):
        print ("delete action")
        
    def abortAction(self):
        print ("abort action")

    def reset_context(self):
        print ("reset context")
   
class RibbonContextCmd(omui.MPxContextCommand):
    
    COMMAND_NAME = "zRibbonCtx"   
    
    def __init__(self):
        super(RibbonContextCmd, self).__init__()
        
    def makeObj(self):
        return RibbonContext() 
    
    @classmethod
    def creator(cls):
        return RibbonContextCmd()

    def appendSyntax(self):
        syntax = self.syntax()
        syntax.addFlag(kMeshFlag, kMeshLongFlag, om.MSyntax.kDouble)

    def doEditFlags(self):
        argParser = self.parser()

        if argParser.isFlagSet(kMeshFlag):
            mesh_flag = argParser.flagArgumentInt(kMeshFlag, 0)
            self.mesh_flag = mesh_flag  # setting a dummy attribute..
            print(f'===>>> Editing flag with value: {mesh_flag} <<<===')      

    def doQueryFlags(self):
        argParser = self.parser()

        if argParser.isFlagSet(kMeshFlag):
            # get something when in query mode, and call setResult() method with argument of what querying this flag should return
            if hasattr(self, 'mesh_flag'):  # check if attribute exists, since we've created it on the fly for this demo, in first edit flag call
                print(f'===>>> Querying flag {kMeshLongFlag}: {self.mesh_flag} <<<===')
                self.setResult(self.mesh_flag)  # setting result to dummy value we stored when editing flag      

def initializePlugin(plugin):
    
    plugin_fn = om.MFnPlugin(plugin)
    
    try:
        plugin_fn.registerContextCommand(RibbonContextCmd.COMMAND_NAME,
                                         RibbonContextCmd.creator)
    except:
        om.MGlobal.displayError("Failed to register context command: %s"
                                 %RibbonContextCmd.COMMAND_NAME)
    
def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)
    
    try:
       plugin_fn.deregisterContextCommand(RibbonContextCmd.COMMAND_NAME)
    except:
        om.MGlobal.displayError("Failed to deregister context command: %s"
                                 %RibbonContextCmd.COMMAND_NAME)