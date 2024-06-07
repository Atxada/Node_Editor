import os 
import json

import maya.cmds as cmds 

import ZCore.ToolsSystem as ToolsSystem

# directory
module_path = ToolsSystem.get_path("Sources","ControlCurves")
#current_dir = os.path.dirname(__file__)
#module_path = os.path.join(current_dir,"Sources")

# Color Enum
COLOR_RED = 13
COLOR_YELLOW = 17
COLOR_GREEN = 14
COLOR_CYAN = 18
COLOR_BLUE = 6
COLOR_CREAM = 20
COLOR_WHITE = 16
COLOR_BLACK = 1

# axis const
WORLD_X = "x"
WORLD_Y = "y"
WORLD_Z = "z"

def  __init__(self):
    pass

# Error (Unusable if obj in world space outliner and already freezed transform)
# parameter(selection = object, group_name = string)
def create_extra_group(self, selection, suffix_name):
    cmds.select(selection)
    selection_parent = cmds.pickWalk(d="up")

    if selection_parent[0] == selection: 
        extra_group = cmds.group(n = selection + "_" + suffix_name,w=1,em=1) 
        cmds.matchTransform(extra_group,selection)
        cmds.parent(selection,extra_group)
        return extra_group
    
    else:
        extra_group = cmds.group(n = selection + "_" + suffix_name,w=1,em=1)
        cmds.parent(extra_group,selection_parent)
        self.zero_transform(extra_group)
        cmds.makeIdentity(extra_group)
        cmds.parent(selection,extra_group)
        cmds.select(cl=1)
        return extra_group
    
    #print ("Create extra group for {0}".format(selection))

# Beta
def system_group_hierarchy(self, system_group_order):
    if system_group_order == 0:
        system_group_order = "Extra"
    elif system_group_order == 1:
        system_group_order = "Flip"
    elif system_group_order == 2:
        system_group_order = "Global"
    elif system_group_order == 3:
        system_group_order = "Follow"        
    elif system_group_order == 4:
        system_group_order = "Offset"  
    else:
        cmds.error("please specify valid order input")

# this function create extra group for follow so you don't need to
# parameter(selection=ctrl,follow_target1,follow_target2,skip_translate=axis to be ignore,skip_rotate=axis to be ignore) 
# follow_type = "translate"|"rotate"|"translate_and_rotate")
def follow_system(self,selection,follow_target1,follow_target2,follow_type = "translate_and_rotate",attribute_name=None):
    # Beta
    cmds.select(selection)
    
    # Decide follow_type
    if follow_type == "translate_and_rotate":
        if attribute_name == None:
            attribute_name = "Follow"
        if cmds.objExists(selection+"_"+attribute_name):
            follow_group = selection+"_"+attribute_name
        else:
            follow_group = self.create_extra_group(selection,attribute_name)

        follow_constraint = cmds.parentConstraint(follow_target2,follow_target1,follow_group,mo=1)[0]
        cmds.setAttr(follow_constraint + ".interpType", 2)
        setrange_name = "_follow_setrange"
        
    elif follow_type == "translate":
        

        if attribute_name == None:
            attribute_name = "Follow_Translate"
        if cmds.objExists(selection+"_"+attribute_name):
            follow_group = selection+"_"+attribute_name
        else:
            follow_group = self.create_extra_group(selection,attribute_name)

        follow_constraint = cmds.parentConstraint(follow_target2,follow_target1,follow_group,
        mo=1,sr=("x","y","z"))[0]
        cmds.setAttr(follow_constraint + ".interpType", 2)
        setrange_name = "_follow_trans_setrange"
        
    else: 
        if attribute_name == None:
            attribute_name = "Follow_Rotate"
        if cmds.objExists(selection+"_"+attribute_name):
            follow_group = selection+"_"+attribute_name
        else:
            follow_group = self.create_extra_group(selection,attribute_name)

        follow_constraint = cmds.parentConstraint(follow_target2,follow_target1,follow_group,
        mo=1,st=("x","y","z"))[0]
        cmds.setAttr(follow_constraint + ".interpType", 2)
        setrange_name = "_follow_rot_setrange"
    
    #  Create Follow Attribute
    if not cmds.objExists(selection+"."+attribute_name):
        cmds.addAttr (selection, ln=attribute_name, at="float",dv=0,min=0, max=10)
        cmds.setAttr (selection + ("."+attribute_name),e=1, k=1)

    # connect follow attribute to drive weight constraint
    
    rev_node = cmds.shadingNode("setRange", n=(selection + setrange_name) , au=1 )
    cmds.setAttr(rev_node + ".oldMaxX", 10)
    cmds.setAttr(rev_node + ".oldMaxY", 10)
    cmds.setAttr(rev_node + ".minY", 1)
    cmds.setAttr(rev_node + ".maxX", 1)
    
    cmds.connectAttr(selection+"."+attribute_name, rev_node+".value.valueX")
    cmds.connectAttr(selection+"."+attribute_name, rev_node+".value.valueY")
    cmds.connectAttr(rev_node+".outValue.outValueX",follow_constraint+"."+follow_target1+"W1")
    cmds.connectAttr(rev_node+".outValue.outValueY",follow_constraint+"."+follow_target2+"W0")
    
    cmds.select(cl=1)
    return (selection + "." + attribute_name)
    
# parameter(object = selected dag_object)
def zero_transform(self,object):
    cmds.setAttr(object + ".tx", 0)
    cmds.setAttr(object + ".ty", 0)
    cmds.setAttr(object + ".tz", 0)
    cmds.setAttr(object + ".rx", 0)
    cmds.setAttr(object + ".ry", 0)
    cmds.setAttr(object + ".rz", 0)

# parameter(object = selected dag_object, channel to lock and hide(e.g. ".tx",".ty", etc..))
def lock_hide_attr(self,object,channel):
    for i in channel:
        cmds.setAttr(object + i, l=1, k=0, cb=0)

# parameter(source,target,translate,rotate,scale)
def connect_attr(self,source,target,channel=("x","y","z"),translate=True,rotate=True,scale=False):
    for i in channel:
        if translate==True:
            cmds.connectAttr(source+".translate.t"+i,target+".translate.t"+i,f=1)
        if rotate==True:
            cmds.connectAttr(source+".rotate.r"+i,target+".rotate.r"+i,f=1)
        if scale==True:
            cmds.connectAttr(source+".scale.s"+i,target+".scale.s"+i,f=1)
        
# Beta
# Make sure all argument ordered correctly (top to bottom in hierarchy)!
# parameter(follow_gr p= list or string, fk_ctrl = list or string, follow_grp_parent = string, 
# fk_ctrl_parent = list or string, follow_attr = obj_name + attr_name)
def set_follow_for_fk(self,follow_grp,fk_ctrl,follow_grp_parent,fk_ctrl_parent,follow_attr,max_attr=10):
    offset_fk = []
    offset_follow = []
    constraint_list = []
    count_follow_grp = 0
    count_fk_ctrl = 0
    count_offset_follow = 0
    count_constraint_list = 0
    
    for i in fk_ctrl:
        new_fk_group = self.create_extra_group(i,"connectFollow")
        offset_fk.append(new_fk_group)
        cmds.parent(new_fk_group,fk_ctrl_parent[count_fk_ctrl])
        count_fk_ctrl+=1
        
    for i in follow_grp:
        new_follow_grp = self.create_extra_group(i,"off")
        offset_follow.append(new_follow_grp)
        cmds.parent(new_follow_grp,follow_grp_parent)
        cmds.connectAttr(i+".translate",offset_fk[count_follow_grp]+".translate",f=1)
        cmds.connectAttr(i+".rotate",offset_fk[count_follow_grp]+".rotate",f=1)
        count_follow_grp+=1
    
    # Exclude first offset
    for i in offset_follow[1:]:
        constraint = cmds.parentConstraint(follow_grp[count_offset_follow],fk_ctrl[count_offset_follow],
        i,mo=1)[0]
        cmds.setAttr(constraint + ".interpType", 2)
        constraint_list.append(constraint)
        count_offset_follow+=1
    
    # Switch for follow and fk system
    rename_follow_attr = follow_attr.replace(".","_")
    if cmds.objExists(rename_follow_attr+"_setFK_SR"):
        shading_node = rename_follow_attr + "_setFK_SR"
    else:
        shading_node = cmds.shadingNode("setRange",n=rename_follow_attr+"_setFK_SR",au=1)
        cmds.setAttr(shading_node + ".oldMaxX", max_attr)
        cmds.setAttr(shading_node + ".oldMaxY", max_attr)
        cmds.setAttr(shading_node + ".minY", 1)
        cmds.setAttr(shading_node+ ".maxX", 1)
        cmds.connectAttr(follow_attr, shading_node+".value.valueX")
        cmds.connectAttr(follow_attr, shading_node+".value.valueY")
    
    for i in constraint_list:
        cmds.connectAttr(shading_node+".outValue.outValueX",i+"."+follow_grp[count_constraint_list]+"W0")
        cmds.connectAttr(shading_node+".outValue.outValueY",i+"."+fk_ctrl[count_constraint_list]+"W1")
        count_constraint_list+=1

# HEAVY 
def are_vertices_connected(self,vertex1, vertex2):
    #basically query all edge that connected to first vertex
    connected_edges = cmds.polyListComponentConversion(vertex1, toEdge=True)
    connected_edges = cmds.filterExpand(connected_edges, sm=32)

    # Check if the second vertex is part of any of the connected edges
    for edge in connected_edges:
        vertices = cmds.polyListComponentConversion(edge, toVertex=True)
        vertices = cmds.filterExpand(vertices, sm=31)
        if vertex2 in vertices:
            return True
        
    return False
    
# HEAVY 
# parameter(vertex, all_vertex = list of selected vertex)
def is_vertex_on_edge(self,vertex, all_vertex):
    connect_count = 0
    
    #basically query all edge that connected to first vertex
    connected_edges = cmds.polyListComponentConversion(vertex, toEdge=True)
    connected_edges = cmds.filterExpand(connected_edges, sm=32)
    cmds.select(cl=1)
    
    # Check if the second vertex is part of any of the connected edges
    for edge in connected_edges:
        vertices = cmds.polyListComponentConversion(edge, toVertex=True)
        vertices = cmds.filterExpand(vertices, sm=31)
        cmds.select(vertices,add=1)
        neighbor_vtx = cmds.ls(sl=1,fl=1)
        
    for vtx in all_vertex:
        if vtx in neighbor_vtx:
            connect_count +=1
            if connect_count == 3:
                return False
        
    return True

# Beta(Remember only passing the correct parameter for this to work)
# Note(this function can remove element in given argument)
# parameter(selection = vertex selected (cmds.ls(fl=1,os=1))
def order_selection(self,selection):  
    selection_initial_length = len(selection)
    connected_vtx=[]
    
    count = 0
    for i in range(len(selection)):
        if len(selection) == 1:
            connected_vtx.append(selection[0])
            selection.remove(selection[0])
            break
        for vtx in selection:
            first_index = selection[0]
            vertex = vtx
            if first_index!=vtx:
                if self.are_vertices_connected(first_index,vtx):
                    connected_vtx.append(first_index)
                    selection.remove(selection[0])
                    selection.remove(vtx)
                    selection.insert(0,vtx)
        count+=1
    
    if len(connected_vtx) != selection_initial_length:
        print (connected_vtx)
        cmds.warning("some vertices have been excluded, please select clean vertex loop")

    return connected_vtx

def do_wire_deform(self, shape, deformCurves, baseCurves):
    count = len(deformCurves)
    wireDef = cmds.wire(shape, wc= count)[0]
    for i in range(count):  
        cmds.connectAttr('%s.worldSpace[0]' % deformCurves[i], '%s.deformedWire[%s]' % (wireDef, i)) 
        cmds.connectAttr('%s.worldSpace[0]' % baseCurves[i], '%s.baseWire[%s]' % (wireDef, i)) 
    cmds.setAttr('%s.rotation' % wireDef, 0)
    
# Beta
# parameter(name,vtx=single or multiple xform/(x,y,z),degree,width,color=remember to use enum for easier us)
def create_curve_from_pos(self,name,pos,degree=1,width=1,color=0):
    curve = cmds.curve(n=name,d=degree,p=pos,k=range(len(pos)))
    cmds.xform(curve,cp=1)
    curveShape = cmds.listRelatives(curve, s=1)[0]
    
    cmds.setAttr(curveShape+".lineWidth",width)
    cmds.setAttr(curveShape+".overrideEnabled",1)
    cmds.setAttr(curveShape+".overrideColor",color)
    
    return curve

# parameter(obj)
# Note(use translation flag)
def get_xform_pos(self,obj):
    if isinstance(obj, list):
        obj_xform = []
        
        for i in obj:
            pos = cmds.xform(i, q=1,ws=1,t=1)
            obj_xform.append(pos)
        
        return obj_xform
    else:
        return cmds.xform(obj,q=1,ws=1,t=1)

# Beta 
# Parameter (name,pos,rot,color,width,shape=ctrl shape you want to create)
def create_ctrl_on_pos(self,name,pos=(0,0,0),rot=(0,0,0),color=0,width=1,shape="circle",scale=1):
    if shape != "circle":
        with open(self.module_path+"/controls.json") as read_file:
            json_file = json.load(read_file)
            point = json_file[shape]
            
            if scale != 1:
                for i in range(len(point)):
                    point[i][0] = point[i][0]*scale
                    point[i][1] = point[i][1]*scale
                    point[i][2] = point[i][2]*scale
                ctrl = cmds.curve(n=name,d=1,p=point)
            else:    
                ctrl = cmds.curve(n=name,d=1,p=point)
    else:
        ctrl = cmds.circle(n=name,ch=0)[0]
        if scale!=1:
            for i in range(cmds.getAttr(ctrl+'.spans')):
                X_CV = cmds.xform(ctrl+".cv[{0}]".format(i),q=1,ws=1,t=1)[0]
                Y_CV = cmds.xform(ctrl+".cv[{0}]".format(i),q=1,ws=1,t=1)[1]
                Z_CV = cmds.xform(ctrl+".cv[{0}]".format(i),q=1,ws=1,t=1)[2]
                cmds.xform(ctrl+".cv[{0}]".format(i),ws=1,t=(X_CV*scale,Y_CV*scale,Z_CV*scale))
        
    group = cmds.group(n=name+"_off",em=1,w=1)
    cmds.parent(ctrl,group)
    
    # Move group on pos and rot
    cmds.xform(group,ws=1,t=pos,ro=rot)
    
    # Change Color if needed
    circleShape = cmds.listRelatives(ctrl, s=1)
    
    for shape in circleShape:
        cmds.setAttr(shape+".lineWidth",width)
        cmds.setAttr(shape+".overrideEnabled",1)
        cmds.setAttr(shape+".overrideColor",color)
    
    return group, ctrl

# source: stackoverflow by Kyle baker 
def findMiddle(self,input_list):
    middle = float(len(input_list))/2
    if middle % 2 != 0:
        return input_list[int(middle - .5)]         # return element in list
    else:
        return (input_list[int(middle)], input_list[int(middle-1)])     # return tuple between two object


# parameter (pos_1 = (x,y,z), pos_2 = (x,y,z))
def findMiddle_pos(self,pos_1,pos_2):
    center = []

    for i in range(3):
        center.append((pos_1[i]+pos_2[i])/2)
    return center
    
# parameter (obj to add,name)
def add_attr_separator(self,obj,name):
    cmds.addAttr(obj, ln=name, at="enum", en="___________:")
    cmds.setAttr(obj+"."+name, e=1, k=0, cb=1)
    
    return obj + "." + name

# you can assign max_value/min_value as false using string
# parameter (obj to add,name,min_value,max_value)
def add_attr_float(self,obj,name,min_value,max_value,dv=0):
    if max_value=="False" and min_value=="False":
        cmds.addAttr(obj,ln=name,at="double",dv=dv)
        cmds.setAttr(obj+"."+name,e=1,k=1)       
        return obj + "." + name
        
    elif max_value=="False":
        cmds.addAttr(obj,ln=name,at="double",dv=dv,min=min_value)
        cmds.setAttr(obj+"."+name,e=1,k=1)
        return obj + "." + name
        
    elif min_value=="False":
        cmds.addAttr(obj,ln=name,at="double",dv=dv,max=max_value)
        cmds.setAttr(obj+"."+name,e=1,k=1)
        return obj + "." + name
        
    else:
        cmds.addAttr(obj,ln=name,at="double",dv=dv,max=max_value,min=min_value)
        cmds.setAttr(obj+"."+name,e=1,k=1)
        return obj + "." + name        

# You can pass None to output_attr 
# parameter (input_attr=name+attr_name,output_attr=name+attr_name,factor=conversion factor)
def convert_value(self,input_attr,output_attr,factor):
    if output_attr == None:
        node = cmds.shadingNode("unitConversion",au=1,n="UC_"+input_attr.rpartition(".")[2])
    if not output_attr == None:
        node = cmds.shadingNode("unitConversion",au=1,n="UC_"+input_attr.rpartition(".")[2]+"_"+(output_attr.rpartition(".")[2])[:14])
        cmds.connectAttr(node+".output",output_attr,f=1)
    cmds.connectAttr(input_attr,node+".input.",f=1)
    cmds.setAttr(node+".conversionFactor",factor)
    
    return node

# drivers take list
# parameter(drivers=[obj_name+attr_name,...], driven = obj_name+attr_name)
def clamp_multi_input(self,drivers,driven,clamp_min=0,clamp_max=1):
    # check passed argument if it list
    if not isinstance(drivers, list):
        cmds.warning("Only detect one input clamp, skip operation")
        return
        
    # Select all driver first then the driven
    rename_driven = driven.replace(".","_")
    clamp_node_name = rename_driven + "_clamp"
    blendWeight_node_name = rename_driven + "_blendW"
    
    cmds.shadingNode("blendWeighted",n=blendWeight_node_name,au=1)
    cmds.shadingNode("clamp",n=clamp_node_name,au=1)
    
    cmds.setAttr(clamp_node_name + ".minR",clamp_min)
    cmds.setAttr(clamp_node_name + ".maxR",clamp_max)
    
    count = 0
    for i in drivers:
        cmds.connectAttr(i,blendWeight_node_name+".input"+str([count]),f=1)
        count+=1
        
    cmds.connectAttr(blendWeight_node_name+".output",clamp_node_name+".input.inputR",f=1)
    cmds.connectAttr(clamp_node_name+".output.outputR",driven,f=1)
    
    return blendWeight_node_name,clamp_node_name

# you can pass None to output attr and input2
# parameter (input1 = list or single as x input, input2 = float, number, list or single as x input, 
#            name = node_name,output_attr = list or single as x input)
# example input1 = ["obj.rx","obj.ry"] -> input1[0] and input1[1] will use x and y channel automatically
def multiply_divide(self,input1,input2,name,output_attr=None):
    channel = ["X","Y","Z"]
    count = 0

    if output_attr == None:
        node = cmds.shadingNode("multiplyDivide",au=1,n=name)
    if not output_attr == None:
        node = cmds.shadingNode("multiplyDivide",au=1,n=name)
        if isinstance(output_attr, list or tuple):
            for i in output_attr:
                cmds.connectAttr(node+".output"+channel[count],i,f=1)
                count+=1
        else:
            cmds.connectAttr(node+".outputX",i,f=1)

    count = 0        
    if isinstance(input1, list or tuple):
        for i in input1:
            cmds.connectAttr(i,node+".input1"+channel[count],f=1)
            count+=1
    else:
        cmds.connectAttr(i,node+".input1X",f=1)

    count = 0
    if isinstance(input2, list or tuple):
        for i in input2:
            if type(i) == int or float:
                cmds.setAttr(node+".input2"+channel[count],i)
                count+=1
            else:
                cmds.connectAttr(i,node+".input2"+channel[count],f=1)
                count+=1
    elif input2 == None:
        pass
    else:
        if type(input2) == int or float:
            cmds.setAttr(node+".input2X",input2)
        else:
            cmds.connectAttr(input2,node+".input2X",f=1)

    return node

# Beta (only 1D available ATM)
# parameter(input_attr = obj attr name single or list, name, output_attr, input_type)
def plus_minus_average(self,input_attr,name,output_attr=None,input_type="1D"):
    count = 0
    if output_attr == None:
        node = cmds.shadingNode("plusMinusAverage",au=1,n=name)
    else:
        node = cmds.shadingNode("plusMinusAverage",au=1,n=name)
        cmds.connectAttr(node+".output"+input_type,output_attr,f=1)
    count = 0
    if isinstance(input_attr, list or tuple):
        for i in input_attr:
                cmds.connectAttr(i,node+".input"+input_type+"[{0}]".format(count))
                count +=1
    else:
        cmds.connectAttr(input_attr,node+".input"+input_type+"[{0}]".format(count))

    return node

# you can pass None to output attr
# parameter (input_attr,output_attr)
def reverse_value(self,input_attr,output_attr):
    if output_attr == None:
        node = cmds.shadingNode("reverse",au=1,n="Rev_"+input_attr.rpartition(".")[2])
    if not output_attr == None:
        node = cmds.shadingNode("reverse",au=1,n="Rev_"+input_attr.rpartition(".")[2]+"_"+(output_attr.rpartition(".")[2])[:14])
        cmds.connectAttr(node+".outputX",output_attr,f=1)
    cmds.connectAttr(input_attr,node+".inputX",f=1)
    
    return node

# parameter (name,source=list/single object,target=obj)
def create_blendshape(self,name,source,target):
    cmds.select(cl=1)
    if isinstance(source, list or tuple):
        for i in source:
            cmds.select(i,add=1)
    else:
        cmds.select(source)
    
    cmds.select(target,add=1)
    return cmds.blendShape(n=name)[0]

# Beta (Unstable)
# driver attr take 2 level tuple/list and driven also take 2 level tuple
# parameter (driver_attr=((driver attr name, value),(..)), driven attr=((driven attr name, value),(..))
def set_driven_key(self,driver_attr,driven_attr):
    for i in range(len(driver_attr)):
        cmds.setAttr(driver_attr[i][0],driver_attr[i][1])
        cmds.setAttr(driven_attr[i][0],driven_attr[i][1])
        cmds.setDrivenKeyframe(driven_attr[i][0],cd=driver_attr[i][0])
        
    # Reset to normal
    cmds.setAttr(driver_attr[0][0],driver_attr[0][1])

# parameter (source_attr = attr_name to connect to input BW, target_attr,name,weight_attr=weight input in BW node)
def blend_weight(self,source_attr,target_attr,name,weight_attr=None):
    cmds.shadingNode("blendWeighted",n=name,au=1)
    
    source_count = 0
    weight_count = 0
    
    if isinstance(source_attr, list):
        for i in source_attr:
            cmds.connectAttr(i,name+".input"+str[source_count],f=1)
            source_count+=1
    else:
        cmds.connectAttr(source_attr,name+".input[0]",f=1)
    
    if weight_attr != None:
        if isinstance(weight_attr, list):
            for i in weight_attr:
                cmds.connectAttr(i,name+".weight"+str[weight_count],f=1)
                weight_count+=1
        else:
            cmds.connectAttr(weight_attr,name+".weight[0]",f=1)
            
    cmds.connectAttr(name+".output",target_attr,f=1)
    
    return name

# Beta(Heavy)(not effective)
# parameter (obj,axis= x or y or z or (x,y,z) individual, amount = target pos)
def move_cv(self,obj,axis,amount):
    degs = cmds.getAttr(obj+'.degree')
    spans = cmds.getAttr(obj+'.spans')
    cvs = degs+spans
    
    for i in range(cvs):
        if "x" in axis:
            temp_posY = cmds.xform(obj+".cv[{0}]".format(i),q=1,ws=1,t=1)[1]
            temp_posZ = cmds.xform(obj+".cv[{0}]".format(i),q=1,ws=1,t=1)[2]
            temp_posX = cmds.xform(obj+".cv[{0}]".format(i),ws=1,t=(amount,temp_posY,temp_posZ),wd=1)
            temp_posX = cmds.xform(obj+".cv[{0}]".format(i),q=1,ws=1,t=1)[0]
            
        if "y" in axis:
            temp_posX = cmds.xform(obj+".cv[{0}]".format(i),q=1,ws=1,t=1)[0]
            temp_posZ = cmds.xform(obj+".cv[{0}]".format(i),q=1,ws=1,t=1)[2]
            temp_posY = cmds.xform(obj+".cv[{0}]".format(i),ws=1,t=(temp_posX,amount,temp_posZ),wd=1)
            temp_posY = cmds.xform(obj+".cv[{0}]".format(i),q=1,ws=1,t=1)[1]

        if "z" in axis:
            temp_posX = cmds.xform(obj+".cv[{0}]".format(i),q=1,ws=1,t=1)[0]
            temp_posY = cmds.xform(obj+".cv[{0}]".format(i),q=1,ws=1,t=1)[1]
            temp_posZ = cmds.xform(obj+".cv[{0}]".format(i),ws=1,t=(temp_posX,temp_posY,amount),wd=1)
            temp_posZ = cmds.xform(obj+".cv[{0}]".format(i),q=1,ws=1,t=1)[2]
        
# parameter (obj = can be single or multiple)
def check_objExist(self,obj):
    if isinstance(obj, list):
        for i in obj:
            if cmds.objExists(i):
                cmds.error("Duplicated object detected: {0}".format(i))
                return i
    else:
        if cmds.objExists(obj):
            cmds.error("Duplicated object detected: {0}".format(obj))
            return obj

# source: stackoverflow by theodox
# parameter (geo)
def is_obj_skinned(self,geo):
    objHist = cmds.listHistory(geo, pdo=True)
    skinCluster = cmds.ls(objHist, type="skinCluster") or [None]
    cluster = skinCluster[0]
    
    if cluster == None:
        return False
    else:
        return True

# parameter (obj = list that ordered(the first index is parent)(work with 1 root hierarchy))
def order_hierarchy(self,obj_list):
    if not isinstance(obj_list, list):
        return

    count = 0
    for i in range(len(obj_list)):
        if count == len(obj_list)-1:
            return
        
        if cmds.listRelatives(obj_list[count+1],p=1) != None:
            if cmds.listRelatives(obj_list[count+1],p=1)[0] == obj_list[count]:
                count += 1
                continue
            
        cmds.parent(obj_list[count+1],obj_list[count])
        count += 1

# parameter (joint = list/tuple or single object)
def segment_scale_compensate(self,joint):
    if isinstance(joint, list or tuple):
        for i in joint:
            cmds.setAttr(i+".segmentScaleCompensate", 0)
    else:
        cmds.setAttr(joint+".segmentScaleCompensate", 0)

# Parameter (joint = list joint, primary, secondary)
# Primary = The argument can be one of the following strings: xyz, yzx, zxy, zyx, yxz, xzy, none.
# Secondary = The argument can be one of the following strings: xup, xdown, yup, ydown, zup, zdown, none
def set_jnt_axis(self, joint, primary="xzy", secondary="zup"):
    if isinstance(joint,list or tuple):
        for i in joint:
            cmds.joint(i,e=1,oj=primary,sao=secondary,zso=1,ch=0)  
    else:
        cmds.joint(joint,e=1,oj=primary,sao=secondary,zso=1,ch=0)  

# Parameter (joint = single joint)
def set_tip_axis(self, joint):
    if isinstance(joint,list or tuple):
        for i in joint:
            cmds.joint(i,e=1,oj="none",zso=1,ch=0)
    else:
        cmds.joint(joint,e=1,oj="none",zso=1,ch=0)

# Beta
# Not yet clean constraint
# parameter(joints=selected lid jnt(w/o root) up_obj, jnt_name = suffix or prefix (jnt or joint)
# aim_vec = (x, y, z), up_vec = (x, y, z))
def set_aim_loc(self,joints,up_obj,jnt_name=None,aim_vec=(1,0,0),up_vec=(0,1,0)):
    lid_locator = []
    
    # Beta (unquote below, if head joint available)
    """
    up_vector = cmds.spaceLocator(n = dir_x+"_eyeUpVec_Loc", p = (0,0,0))
    up_vector_grp = cmds.group(n = dir_x+"_eyeUpVec_FollowHead", em=1, w=1)
    """
    
    # Create locator for each joint, and aim constraint
    for i in joints:
        loc = cmds.spaceLocator()[0]
        if jnt_name != None:
            loc = cmds.rename(cmds.ls(sl=1)[0], i.replace(jnt_name,"Loc"))
        lid_locator.append(loc)
        jnt_pos = cmds.xform(i, q=1, ws=1, t=1)
        cmds.xform(loc, ws=1, t=jnt_pos)
        jnt_parent = cmds.listRelatives(i,p=1)[0]
        
        cmds.aimConstraint(loc, jnt_parent, mo=1, w=1, aim=aim_vec, u=up_vec, wut="object", wuo=up_obj)

    return lid_locator