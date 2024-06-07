#from eye_rig_tool.face_rig import FaceRig

import maya.cmds as cmds 
import maya.mel as mel

"""
Features:
create ribbon based lip with basic ctrl + with proper skinning between upper and lower (WIP)
create basic emotions option (procedural?) + kissing and mmm  
create alphabet and lipsync 
create nasolabial fold
(advanced) zipping effect
"""

class LipSystem():

    # class properties 
    setup_node = None

    # setup
    def __init__(self):
        sel = cmds.filterExpand(sm=32)
        if sel != None:
            crv = cmds.polyToCurve(f=2,dg=1,usm=0,ch=False,n="eyebrow_setup")[0]
            cmds.xform(crv,cp=1)
        else:
            crv = cmds.curve(n="eyebrow_setup", 
                                        d=3, 
                                        p=[(0, 0, 2),(0, 0, 1.8), (0, 0, 0), (0, 0, -1.8),(0, 0, -2)])

            crv_cv = cmds.ls('%s.cv[:]'%crv, fl=1)
            cmds.select(crv_cv[0], crv_cv[1])
            cluster_a = cmds.cluster(n="cluster_a")
            cmds.select(crv_cv[2])
            cluster_b = cmds.cluster(n="cluster_b")
            cmds.select(crv_cv[3], crv_cv[4])
            cluster_c = cmds.cluster(n="cluster_c")
            cluster_grp = cmds.group(cluster_a,cluster_b,cluster_c,n="setup_cluster")
            cmds.setAttr(cluster_grp_+".visibility",0)
    
    # build rig system from setup
    def build(self):
        pass

    # mirror setup or system according to plane
    def mirror(self):
        pass

instance = LipSystem()

'''
1. select edge to curve
3. rebuild curve number span as controller needed
4. create ribbon
'''
