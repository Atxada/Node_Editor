from ZCore.Face import FaceSystem

import maya.api.OpenMaya as om
import maya.cmds as cmds 

'''
---------------------------------- Feature expansion ----------------------------------
-migrate constraint jnt along curve to MayaUtil
-request id from parent
-mpxcontext, create using custom vtx
-when not select anything, will create curve skinned within joint

--------------------------------------- Problem ---------------------------------------
pass
'''

class EyebrowSystem(FaceSystem):  # inherit FaceRig later

    def __init__(self): 
        # constant properties
        self.nameID = "None" #FaceRig.generate_nameID()

        # writable properties
        self.ctrl_pos = []
        self.joint_num = 3
        self.name = self.nameID
        self.size = 1
          
        # read-only properties 
        self.setup_grp = None
        self.setup_crv = None
        self.nurbs_surface = None
        self.setup_jnt = []
        self.setup_ctrl = []
        self.ribbon_follicles = []    

    # def(vtx=list,pos=xform(ws))
    def setup(self):
        if self.setup_crv != None:
            cmds.curve(self.setup_crv,a=1,p=pos)
            cmds.xform(self.setup_crv,cp=1)
        else:
            self.setup_crv = cmds.curve(n=self.name+"setup1",d=1,ep=pos)
            cmds.xform(self.setup_crv,cp=1)
            self.setup_grp = cmds.group(n=self.name+"grp",em=1)
            cmds.parent(self.setup_crv,self.setup_grp)
        cmds.rebuildCurve(self.setup_crv,ch=0,kcp=1,kr=0,d=1) # set max value to 1
        
        cmds.select(cl=1)
        jnt = cmds.joint(n=self.name+"ctrl1")
        cmds.setAttr(jnt+".radius",self.size*2)
        self.setup_ctrl.append(jnt)
        cmds.parent(self.setup_ctrl,self.setup_grp)
        '''
        # setup jnt along setup_crv
        for iter in range(self.joint_num):
            cmds.select(cl=1)
            jnt = cmds.joint(n=self.name+"jnt1")
            cmds.setAttr(jnt+".radius",self.size)
            self.setup_jnt.append(jnt)
        cmds.parent(self.setup_jnt,self.setup_grp)
        self.distribute_object_to_curve(self.setup_jnt,self.setup_crv)
        for iter in range(self.ctrl_num):
            cmds.select(cl=1)
            jnt = cmds.joint(n=self.name+"ctrl1")
            cmds.setAttr(jnt+".radius",self.size*2)
            self.setup_ctrl.append(jnt)
        cmds.parent(self.setup_ctrl,self.setup_grp)
        self.distribute_object_to_curve(self.setup_ctrl,self.setup_crv)
        # create crv, if there is update 
        self.setup_crv = cmds.polyToCurve(f=2,dg=1,usm=0,ch=0,n=self.name+"setup1")[0]
        cmds.xform(self.setup_crv,cp=1)
        cmds.rebuildCurve(self.setup_crv,ch=0,kcp=1,kr=0,d=1) # set max value to 1
        self.setup_grp = cmds.group(n=self.name+"grp",em=1)
        cmds.parent(self.setup_crv,self.setup_grp)
        '''
            
    def build(self):
        self.nurbs_surface = cmds.extrude(self.setup_crv,n=self.name+"surface",ch=False,l=self.size*0.25,et=0)[0]
        cmds.extendSurface(self.nurbs_surface,ch=0,et=0,d=self.size*0.25,es=1,ed=1)
        cmds.rebuildSurface(self.nurbs_surface,ch=False,dir=1,sv=1,kr=0)        # remove v middle spans
        cmds.rebuildSurface(self.nurbs_surface,ch=False,kr=1,dir=0 ,su=0)         # make u spans cubic
        nurbs_surface_shape = cmds.listRelatives(self.nurbs_surface, s=1)[0]

        # setup ribbon using follicle node
        for iter in range(len(self.setup_jnt)):
            follicle = cmds.createNode("follicle")
            follicle = cmds.pickWalk(follicle, d="up")[0]
            follicle = cmds.rename(follicle, self.name + "_follicle#")
            follicle_index = follicle[len(self.name + "_follicle"):]
            follicle_shape = cmds.pickWalk(follicle, d="down")[0]
            self.ribbon_follicles.append(follicle)

            # connect follicles to nurbs plane
            cmds.connectAttr(nurbs_surface_shape + ".local", follicle_shape + ".inputSurface")
            cmds.connectAttr(nurbs_surface_shape + ".worldMatrix[0]", follicle_shape + ".inputWorldMatrix")
            cmds.connectAttr(follicle_shape + ".outRotate", follicle + ".rotate")
            cmds.connectAttr(follicle_shape + ".outTranslate", follicle + ".translate")

            # UValue (0-1). calculate U and V value to determine where to place follicle on surface
            dgpa = om.MDagPath.getAPathTo(om.MSelectionList().add(self.setup_crv).getDependNode(0))
            curve = om.MFnNurbsCurve(dgpa)
            cv_pos = curve.cvPosition(iter, om.MSpace.kObject)
            U = curve.closestPoint(cv_pos)[1]
            cmds.setAttr(follicle_shape+".parameterU",U)
            cmds.setAttr(follicle_shape+".parameterV",0.5)

    # migrate to maya util
    # def(obj=list,crv)
    def distribute_object_to_curve(self,obj,crv):
        mopath_list = []
        if len(obj) != 1:
            step = 1.0/(len(obj)-1)
            for iter in range(len(obj)):
                motion_path = cmds.pathAnimation(obj[iter], crv, f=1, fm=1)
                mopath_list.append(motion_path)
                mopath_input = motion_path + "_uValue.output"
                cmds.disconnectAttr(mopath_input, motion_path + ".uValue")
                cmds.delete(motion_path + "_uValue")
                cmds.setAttr(motion_path + ".uValue", 0+(step*iter))
            return mopath_list
            
        else:
            motion_path = cmds.pathAnimation(obj[0], crv, f=1, fm=1)
            mopath_input = motion_path + "_uValue.output"
            cmds.disconnectAttr(mopath_input, motion_path + ".uValue")
            cmds.delete(motion_path + "_uValue")
            cmds.setAttr(motion_path + ".uValue", 0.5)
            return [motion_path]

'''
instance = EyebrowSystem()
instance.setup()
if instance.setup_crv is not None:
    instance.build()
    pass

1. select edge to curve
3. rebuild curve number span as controller needed
4. create ribbon
'''