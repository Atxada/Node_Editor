
import operator

import maya.api.OpenMaya as om
import maya.api.OpenMayaUI as omui

import maya.cmds as cmds

import ZCore.ToolsSystem as ToolsSystem

'''
---------------------------------- Feature expansion ----------------------------------
-ray get closest intersection, optimized and not heavy tested with multiple mesh
-tool settings for advance context (like ep curve tool settings), and query live mesh to flag argument ctx

--------------------------------------- Problem ---------------------------------------
-undo stack queue problem (crash when undo? with live surface)
-change query from live to live cache (need more testing for error proof)
-in middle of context if user delete crv problem occur
'''

"""
# directory 
icon_dir = ToolsSystem.ZCore_icon_dir

class SplineContext():
    def __init__(self,name_id=""):
        self.name_id = name_id 
        self.active_crv = None
        self.active_jnt = []
        self.size = 1

    def create_joint(self,pos):
        cmds.select(cl=1)
        jnt = cmds.joint(n=self.name_id+"joint1",p=pos)
        cmds.setAttr(jnt+".radius",self.size*2.5)
        self.active_jnt.append(jnt)

    def add_item(self,pos):
        if self.active_crv != None:
            cmds.curve(self.active_crv,a=1,ep=pos)
            cmds.xform(self.active_crv,cp=1)
            cmds.rebuildCurve(self.active_crv,ch=0,kcp=1,kr=0,d=1) # set max value to 1
        else:
            self.active_crv = cmds.curve(n=self.name_id+"setup1",d=1,ep=pos)
            cmds.xform(self.active_crv,cp=1)   
        self.create_joint(pos)

    def remove_item(self):
        crv_last_index = len(cmds.getAttr(self.active_crv+".ep[:]"))-1
        cmds.delete(self.active_jnt[-1])
        self.active_jnt = self.active_jnt[:-1]
        cmds.delete(self.active_crv+".ep[%s]"%crv_last_index)
        if crv_last_index == 0:
            cmds.delete(self.active_crv)
        if not cmds.objExists(self.active_crv):
            self.active_crv = None
"""

# tell maya plugin produces and need to be passed, maya api 2.0
def maya_useNewAPI():
    pass
        
class SplineContext(omui.MPxContext):
    TITLE = "Ribbon Spline Tool"
    HELP_TEXT = "Select vertex to add joint placement. Enter to complete"
    CTX_ICON = ToolsSystem.get_path("Sources","icons","context","splineContext.png")
    
    # context data
    SETUP_COLOR = 22
    jnt = []

    def __init__(self):
        super(SplineContext, self).__init__()

        # reference to class attr(<class name>.<variable>), so it will stay consistent to all instance 
        self.setTitleString(SplineContext.TITLE)  
        self.setImage(SplineContext.CTX_ICON, omui.MPxContext.kImage1) # up to 3 slot
        self.setCursor(omui.MCursor.kDoubleCrossHairCursor)	

    def helpStateHasChanged(self, event):
        self.setHelpString(SplineContext.HELP_TEXT)
        
    def toolOnSetup(self,event):
        om.MGlobal.selectCommand(om.MSelectionList())  # select nothing, to record undo
        self.reset_context()
        
    def toolOffCleanup(self):
        self.reset_context()

    def doPress(self, event, draw_manager, frame_context):
        ray_source = om.MPoint()  # 3D point with double-precision coordinates
        ray_direction = om.MVector()  # 3D vector with double-precision coordinates
        omui.M3dView().active3dView().viewToWorld(event.position[0],event.position[1],ray_source,ray_direction)
        if ToolsSystem.live_mesh: 
            live_mesh = ToolsSystem.live_mesh
        else:
            live_mesh = cmds.ls(type="mesh")
            if len(live_mesh) > 10:
                cmds.warning("truncate live mesh to 10, mesh amount exceed safe perfomance limit. Use live object for accurate result")
                live_mesh = live_mesh[:10]

        for mesh in live_mesh:
            selectionList = om.MSelectionList()
            selectionList.add(mesh)  # Add mesh to list
            dagPath = selectionList.getDagPath(0)  # Path to a DAG node
            fnMesh = om.MFnMesh(dagPath)  # Function set for operation on meshes

            intersection = fnMesh.closestIntersection(om.MFloatPoint(ray_source),  # raySource
                                                      om.MFloatVector(ray_direction),  # rayDirection
                                                      om.MSpace.kWorld,  # space
                                                      99999,  # maxParam (search radius around the raySource point)
                                                      False)  # testBothDirections

            # Extract the different values from the intersection result     
            hitPoint, hitRayParam, hitFace, hitTriangle, hitBary1, hitBary2 = intersection
            x, y, z, _ = hitPoint

            """
            obj_distances = []
            if (x, y, z) != (0.0, 0.0, 0.0): 
                distance_vector = map(lambda i, j: i-j, hitPoint, ray_source)
                obj_distances.append(distance_vector[0]*distance_vector[0] + distance_vector[1]*distance_vector[1] + distance_vector[2]*distance_vector[2])
            else:
                obj_distances.append(0)
            """
    
            if (x, y, z) != (0.0, 0.0, 0.0):
                cmds.undoInfo(openChunk=True,cn="create spline point")
                cmds.select(cl=1)
                if not event.isModifierControl():
                    jnt = cmds.joint(n="splinePt1",p=(x,y,z))
                    cmds.setAttr(jnt+".overrideEnabled",1)
                    cmds.setAttr(jnt+".overrideColor",self.SETUP_COLOR)
                else:
                    # get closest vertex from hitPoint's face vertices (https://gist.github.com/hdlx/)
                    index = fnMesh.getClosestPoint(om.MPoint(hitPoint), space=om.MSpace.kWorld)[1]  # closest polygon index    
                    face_vertices = fnMesh.getPolygonVertices(index)  # get polygon vertices
                    vertex_distances = ((vertex, fnMesh.getPoint(vertex, om.MSpace.kWorld).distanceTo(om.MPoint(hitPoint)))
                                        for vertex in face_vertices)
                    closest_vertex = min(vertex_distances, key=operator.itemgetter(1))  # sort by smallest first index list
                    closest_vertex_pos = cmds.xform(mesh+".vtx[%s]"%closest_vertex[0],q=1,t=1,ws=1)
                    jnt = cmds.joint(n="splinePt1",p=closest_vertex_pos)
                    cmds.setAttr(jnt+".overrideEnabled",1)
                    cmds.setAttr(jnt+".overrideColor",self.SETUP_COLOR)
                self.jnt.append(jnt)
                cmds.undoInfo(closeChunk=True)
                break
            else: 
                if mesh == live_mesh[-1]: 
                    cmds.warning("ray source:%s & ray direction:%s, no intersection found!"%(ray_source,ray_direction))
    
    def completeAction(self):
        valid_jnt = [] 
        if self.jnt and cmds.objExists(self.jnt[0]):
            name = ToolsSystem.generate_nameID(3)
            grp = cmds.group(n=name,em=1)

            # get valid jnt (ignore deleted/missing joint according to database)
            for jnt in self.jnt:
                try:
                    cmds.setAttr(jnt+".overrideEnabled",0)
                    cmds.parent(jnt,grp)
                    valid_jnt.append(cmds.rename(jnt,name+"_jnt1")) # append renamed jnt 
                except:
                    cmds.warning("%s not found, skipped"%jnt)
            crv = cmds.curve(n=name+"_crv",d=3,ep=[cmds.xform(jnt,q=1,t=1,ws=1) for jnt in valid_jnt])
            cmds.parent(crv,grp)

            # create cluster control curve
            if len(valid_jnt)>1:
                for index,jnt in enumerate(valid_jnt):
                    if jnt == valid_jnt[0]:
                        cluster = cmds.cluster(crv+".cv[:1]")
                        cmds.parent(cluster[1],valid_jnt[0]) 
                    elif jnt == valid_jnt[-1]:
                        cluster = cmds.cluster(crv+".cv[%s:]"%len(valid_jnt)) # cv doesn't work with negative indicates
                        cmds.parent(cluster[1],valid_jnt[-1])
                    else:
                        cluster = cmds.cluster(crv+".cv[%s]"%(index+1))
                        cmds.parent(cluster[1],valid_jnt[index])
                    cmds.setAttr(cluster[1]+".visibility",0)

            # cleanup
            ToolsSystem.parent_setup(grp)
            self.jnt = []
            cmds.select(cl=1)
        
    def deleteAction(self):
        if self.jnt:
            try:
                cmds.delete(self.jnt[-1])
                self.jnt.pop()
            except:
                cmds.warning("Can't delete %s, object not found"%self.jnt[-1])
            
    def abortAction(self):
        for jnt in self.jnt:
            try:
                cmds.delete(jnt)
            except:
                cmds.warning("Can't delete %s, object not found"%jnt)
        self.jnt = []

    # user defined function 
    def reset_context(self):
        self.completeAction()
        self.jnt = []
   
class SplineContextCmd(omui.MPxContextCommand):
    
    COMMAND_NAME = "zSplineCtx"   # used as mel command to create context
    
    def __init__(self):
        super(SplineContextCmd, self).__init__()
        
    # required for maya to get instance of context
    def makeObj(self):
        return SplineContext()    # return ribbon spline ctx 
    
    @classmethod
    def creator(cls):
        return SplineContextCmd() # return ribbon spline ctx cmd   

def initializePlugin(plugin):
    author = "Aldo Aldrich"
    version = "0.1.0"
    
    plugin_fn = om.MFnPlugin(plugin, "", author, version)
    
    try:
        plugin_fn.registerContextCommand(SplineContextCmd.COMMAND_NAME,
                                         SplineContextCmd.creator)

    except:
        om.MGlobal.displayError("Failed to register context command: %s"
                                 %SplineContextCmd.COMMAND_NAME)
    
def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)
    
    try:
       plugin_fn.deregisterContextCommand(SplineContextCmd.COMMAND_NAME)

    except:
        om.MGlobal.displayError("Failed to deregister context command: %s"
                                 %SplineContextCmd.COMMAND_NAME)

'''
# development phase
if __name__ == "__main__":
    # required before unloading the plugin
    # cmds.flushUndo()
    # cmds.file(new=True, force=True)

    # reload the plugin
    plugin_name = "C:/Users/atxad/Desktop/Maya Scripts Draft/1st Album EPILOGUE/Face Tools/ZenoRig/ZCore/SplineCtx.py"

    #cmds.loadPlugin(plugin_name)
    cmds.evalDeferred('if cmds.pluginInfo("{0}", q=True, loaded=True): cmds.unloadPlugin("{0}")'.format(plugin_name))
    cmds.evalDeferred('if not cmds.pluginInfo("{0}", q=True, loaded=True): cmds.loadPlugin("{0}")'.format(plugin_name))

    # setup code to help speed up testing (e.g. load context)
    # cmds.evalDeferred('cmds.file("C:/Users/atxad/Desktop/Maya Scripts Draft/1st Album EPILOGUE/Face Tools/Test Model Subject/Haeri.ma",open=True,force=True)')
    cmds.evalDeferred('context = cmds.zSplineCtx(); cmds.setToolTo(context)') # ctx already added to cmds module  
'''  