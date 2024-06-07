"""
version 1.3
- add advance options for attr name and define blendshape name (done)
- add collapsable shelf (done)
"""
from PySide2 import QtCore,QtWidgets,QtGui
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMayaUI as omui
import maya.OpenMaya as om  # to raise error message
import math # To round up number (ceil)

from string import ascii_letters, digits # to check special character

def maya_main_window():
    # Return the maya main window widget as a python object
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class addBlendshape(QtWidgets.QDialog):
    
    # runtime cache [global variables]
    concatenated_widgets_dict = {}
    select_widgets_dict = {}
    user_input_dict = {}
    
    cache_blendshape_object = []
    attr_name_list = []
    target_ctrl_list = []
    blendshape_line_edit_list = []
    
    class_instance = None
    
    @classmethod
    def show_dialog(cls):
        if not cls.class_instance:
            cls.class_instance = addBlendshape()
        if cls.class_instance.isHidden():
            cls.class_instance.show()
        else:
            cls.class_instance.raise_()
            cls.class_instance.activateWindow()
    
    def  __init__(self, parent=maya_main_window()):
        super(addBlendshape, self).__init__(parent)
        
        self.setWindowTitle("Add Blendshape Options")
        self.setWindowFlags(QtCore.Qt.WindowType.Window)
        self.setStyleSheet("borderstyle:outset")
        self.setMinimumWidth(450)
        self.resize(450,250)
        
        # Remove window question 
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
    
    def create_widgets(self):    
        # Create widgets
        self.attr_check = QtWidgets.QCheckBox("Ignore duplicated attribute name")
        
        # Create line edit
        self.blendshape_nodes_line_edit = QtWidgets.QLineEdit()
        self.ratio_attr_line_edit = QtWidgets.QLineEdit()
        
        # Create Slider
        self.ratio_attribute_Slider = QtWidgets.QSlider()
        self.ratio_attribute_Slider.setOrientation(QtCore.Qt.Horizontal)
        self.ratio_attribute_Slider.setTickInterval(100)
        self.ratio_attribute_Slider.setSingleStep(0.1)
        self.ratio_attribute_Slider.setRange(0, 100)
        self.ratio_attribute_Slider.setSliderPosition(10)
        
        # Button widget
        self.add_btn = QtWidgets.QPushButton("Add blendshape")
        self.clear_btn = QtWidgets.QPushButton()
        self.select_all_btn = QtWidgets.QPushButton()
        self.create_blendshape_btn = QtWidgets.QPushButton("Create")
        self.blendshape_nodes_btn = QtWidgets.QPushButton()
        
        # Add label
        self.blendshape_label = QtWidgets.QLabel("Blendshape")
        self.control_label = QtWidgets.QLabel("Control")
        self.attribute_name_label = QtWidgets.QLabel("Attribute name")
        self.ratio_attr_label = QtWidgets.QLabel("Ratio Attribute")
        
        # Modify label
        myFont = QtGui.QFont()
        myFont.setBold(True)
        myFont.setPixelSize(12)
        
        self.blendshape_label.setFont(myFont)
        self.control_label.setFont(myFont)
        self.attribute_name_label.setFont(myFont)
        
        # Spacer (unused)
        self.top_spacer = QtWidgets.QSpacerItem(0, 0)
        self.bottom_spacer = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        
        # Frame
        self.separator_one = QtWidgets.QFrame()
        self.separator_one.setFrameShape(self.separator_one.HLine)
        self.separator_one.setLineWidth(2)
        self.separator_one.setStyleSheet("border: 1px solid grey")     

        # modify widget if needed
        self.add_btn.setMinimumHeight(30)
                
        self.create_blendshape_btn.setMinimumHeight(30)
        
        self.blendshape_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.control_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.attribute_name_label.setAlignment(QtCore.Qt.AlignCenter)
        
        self.blendshape_label.setMinimumWidth(105)
        
        self.blendshape_label.setMaximumHeight(10)
        
        self.control_label.setMinimumWidth(105)
        
        self.control_label.setMaximumHeight(10)
        
        self.attribute_name_label.setMinimumWidth(105)
        
        self.attribute_name_label.setMaximumHeight(10)
        
        self.clear_btn.setMaximumWidth(35)
        
        self.clear_btn.setMaximumHeight(25)
        
        self.select_all_btn.setMaximumWidth(35)
        
        self.select_all_btn.setMaximumHeight(25)
        
        self.blendshape_nodes_btn.setMaximumWidth(35)
    
        self.blendshape_nodes_btn.setMaximumHeight(25)
        
        self.ratio_attr_line_edit.setAlignment(QtCore.Qt.AlignCenter)
        
        self.ratio_attr_line_edit.setMaximumWidth(40)
        
        self.ratio_attr_line_edit.setText("10")
        
        # set icon to QPushButton
        self.create_blendshape_btn.setIcon(QtGui.QIcon(":blendShape.png"))
        self.clear_btn.setIcon(QtGui.QIcon(":deletePCM"))
        self.select_all_btn.setIcon(QtGui.QIcon(":selectOverlappingUV"))
        self.blendshape_nodes_btn.setIcon(QtGui.QIcon(":nodeGrapherAddNodes"))
        
    def create_layouts(self):
        main_layout = QtWidgets.QVBoxLayout(self)
                
        # Scroll widget
        addBlendshape_list_widget = QtWidgets.QWidget()
        
        # scroll area properties
        addBlendshape_list_scroll_area = QtWidgets.QScrollArea()
        addBlendshape_list_scroll_area.setWidgetResizable(True)
        addBlendshape_list_scroll_area.setWidget(addBlendshape_list_widget)
     
        # No need to parent this layout because it's already parented to main after it created
        top_layout = QtWidgets.QHBoxLayout()
        top_spacer_layout = QtWidgets.QHBoxLayout()
        separator_layout = QtWidgets.QHBoxLayout()
        self.mid_layout = QtWidgets.QVBoxLayout(addBlendshape_list_widget)
        bottom_spacer_layout = QtWidgets.QHBoxLayout()
        advance_options_layout = QtWidgets.QVBoxLayout()
        first_section_adv_layout = QtWidgets.QHBoxLayout()
        second_section_adv_layout = QtWidgets.QHBoxLayout()
        bottom_layout = QtWidgets.QHBoxLayout()
        header_layout = QtWidgets.QHBoxLayout()
                
        # It's like adding spacer in qt designer i suppose?
        top_layout.addWidget(self.add_btn)
        
        header_layout.addWidget(self.blendshape_label)
        header_layout.addWidget(self.clear_btn)   
        header_layout.addWidget(self.control_label)
        header_layout.addWidget(self.select_all_btn)
        header_layout.addWidget(self.attribute_name_label)
        
        separator_layout.addWidget(self.separator_one)
        
        self.mid_layout.setAlignment(QtCore.Qt.AlignTop)
        
        first_section_adv_layout.addWidget(self.attr_check)
        first_section_adv_layout.addWidget(self.blendshape_nodes_btn)
        first_section_adv_layout.addWidget(self.blendshape_nodes_line_edit)
        
        second_section_adv_layout.addWidget(self.ratio_attr_label)
        second_section_adv_layout.addWidget(self.ratio_attribute_Slider)
        second_section_adv_layout.addWidget(self.ratio_attr_line_edit)
        
        bottom_layout.addWidget(self.create_blendshape_btn)
        
        # Advance layout has a few child layout, let's parent is first

    
        # Parent all child layout to main layout, otherwise it will not show
        main_layout.addLayout(top_layout)
        main_layout.addLayout(header_layout)
        main_layout.addLayout(top_spacer_layout)
        main_layout.addLayout(separator_layout)
        main_layout.addWidget(addBlendshape_list_scroll_area)
        main_layout.addLayout(advance_options_layout)
        main_layout.addLayout(bottom_spacer_layout)
        main_layout.addLayout(bottom_layout)
        
        # Create accordion widget like maya GUI
        container = Container("Advanced options")
        advance_options_layout.addWidget(container)
        content_layout = QtWidgets.QVBoxLayout(container.contentWidget)

        content_layout.addLayout(first_section_adv_layout)
        content_layout.addLayout(second_section_adv_layout)

        advance_options_layout.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding))
        advance_options_layout.setStretch(1, 1)

    def create_connections(self):
        # the structure is (widget_name. signals.connect.function that run)
        self.add_btn.clicked.connect(self.undo_chunk_create_new_object)
        self.clear_btn.clicked.connect(self.clear_dynamic_widgets)
        self.create_blendshape_btn.clicked.connect(self.create_blendshape)
        self.select_all_btn.clicked.connect(self.select_all_control)
        self.blendshape_nodes_btn.clicked.connect(self.add_blendshape_nodes)
        self.ratio_attribute_Slider.valueChanged.connect(self.change_slider_value)
    
    def change_slider_value (self,x):
        try:
            float(x)
            self.ratio_attribute_Slider.valueChanged.connect(lambda x: self.ratio_attr_line_edit.setText(str(x)))
            
        except Exception as e:
            print (e)
    
    def clear_dynamic_widgets(self):  
        
        if len(self.cache_blendshape_object) > 0:
            all_keys = self.concatenated_widgets_dict.keys()
            count = 0
            
            for i in all_keys:
                for i in self.concatenated_widgets_dict.get(all_keys[count]):
                    i.deleteLater()
                count += 1
                    
            # Clear the cache 
            self.concatenated_widgets_dict.clear()
            self.select_widgets_dict.clear()
            self.user_input_dict.clear()
            
            del self.cache_blendshape_object [:]
            del self.attr_name_list [:]
            del self.target_ctrl_list [:]
            del self.blendshape_line_edit_list [:]
            
        else:
            print ("list cleared"),
            
    def add_blendshape_nodes(self):
        if not len(cmds.ls(sl=1)) == 0:
            if cmds.objectType(cmds.ls(sl=1)[0]) == "blendShape":
                self.blendshape_nodes_line_edit.setText(cmds.ls(sl=1)[0])
            else:
                print ("Please only select blendshape node"),
        else:
            print ("please select blendshape node"),
   
    def create_blendshape(self): 
        if not cmds.ls(sl=1):
            om.MGlobal.displayError("please only select target mesh object before apply")
            return
            
        target_obj = cmds.ls(sl=1)[0]
        all_keys = self.concatenated_widgets_dict.keys()
        # catch all error and check for any missing requirement
        
        #-------------------------------------------------------------------------------------------------------
        ### Blendshape object validation
        # check if all object is present in scene, this fix not updated list
        
        for i in all_keys:
            all_temp_widget = self.concatenated_widgets_dict.get(i)
            if cmds.objExists((all_temp_widget)[0].text()):
                pass
            elif "|" in all_temp_widget[0].text():
                om.MGlobal.displayError(all_temp_widget[0].text() + " object is not included because tools found duplicate in scene or contain |") 
                return                
                
            else:
                for x in all_temp_widget:
                    x.deleteLater()
                
                om.MGlobal.displayError(all_temp_widget[0].text() + " object is not included because it's not found in scene") 
                return
                
                # clear cache
                del self.concatenated_widgets_dict[i]
                del self.select_widgets_dict[(all_temp_widget)[4]]
                del self.user_input_dict[(all_temp_widget)[0]]
                
                self.cache_blendshape_object.remove((all_temp_widget)[0].text())  # very elegant way to retrieve lineedit value(JK)
                self.attr_name_list.remove((all_temp_widget)[2])
                self.target_ctrl_list.remove((all_temp_widget)[3])   
                self.blendshape_line_edit_list.remove((all_temp_widget[0]))
        
        #-------------------------------------------------------------------------------------------------------
        # Target object requirement
        """
        if cmds.objExists(target_obj+"_addBS_system"):
            om.MGlobal.displayError("Target object already had blendshape system from this tool, if u want proceed pls kindly rename it :)")
            return  
        """
        
        if len(self.cache_blendshape_object) == 0:
            om.MGlobal.displayError("No blendshape found")
            return            
        
        if not cmds.ls(sl=1)[0] in self.cache_blendshape_object:
            pass
        else:
            om.MGlobal.displayError("you selecting blendshape object, please only select target mesh object before apply")  
            return                            # these 2 lines of code is necessary to break program
            
        if not cmds.ls(sl=1,typ=["mesh","nurbsSurface"],dag=1,long=1):
            om.MGlobal.displayError("only select mesh for object target")  
            return                           
        
        #-------------------------------------------------------------------------------------------------------
        # Attribute name requirement
        temp_attr_list = []
        
        for i in self.attr_name_list:
            temp_attr_list.append(i.text())
            
        # valid name check
        for i in temp_attr_list:
            if set(i).difference(ascii_letters + digits + "_"):
                om.MGlobal.displayError("Found invalid character for atttribute name: {0}".format(i))  
                return    
            elif " " in i:
                om.MGlobal.displayError("Found spacing in: {0}".format(i))
                return
            else:
                pass
    
        for i in temp_attr_list:     
            if i == "":
                om.MGlobal.displayError("Please don't leave any unfilled section")  
                return       
            elif len(temp_attr_list) != len(set(temp_attr_list)):
                if self.attr_check.isChecked():
                    pass
                else:
                    om.MGlobal.displayError("Found duplicate in attribute name section")  
                    return                       
            else:
                pass
                
        # Check if attribute exist in control 
        if  self.attr_check.isChecked():
            pass
        else:
            for i in all_keys:
                all_widgets_temp = self.concatenated_widgets_dict.get(i)
                if cmds.objExists(all_widgets_temp[3].text() + "." + all_widgets_temp[2].text()):
                    om.MGlobal.displayError("Found same attribute name on {0}".format(all_widgets_temp[3].text() + "." + all_widgets_temp[2].text()))
                    return
        
        #-------------------------------------------------------------------------------------------------------        
        # Target control requirement
        temp_target_list = []
        
        for i in self.target_ctrl_list:
            temp_target_list.append(i.text())
        
        for i in temp_target_list:
            if i=="":
                om.MGlobal.displayError("Please don't leave any unfilled section")  
                return
        
        #-------------------------------------------------------------------------------------------------------
        # Advance option error check
        if not self.blendshape_nodes_line_edit.text() == "":
            if cmds.objectType(self.blendshape_nodes_line_edit.text()) != "blendShape":
                om.MGlobal.displayError("Custom blendshape is not blendshape type")
                return
            elif cmds.objExists(self.blendshape_nodes_line_edit.text()) == False:
                om.MGlobal.displayError("Custom blendshape not found")
                return
            elif not self.blendshape_nodes_line_edit.text() in cmds.listHistory(target_obj):
                om.MGlobal.displayError("Custom blendshape is not applied to object")
                return
            else:
                pass
        else:
            pass
             
        # Group Undo and call the function
        cmds.undoInfo(openChunk=True,cn="Blendshape system")
        
        try:
            addBlendshape.add_blendshape_operation(self) 
        finally:
            cmds.undoInfo(closeChunk=True)
                                           
    def add_blendshape_operation(self):
        target_obj = cmds.ls(sl=1)[0]
        all_keys = self.concatenated_widgets_dict.keys()
        if self.blendshape_nodes_line_edit.text() == "":
            blendshape_nodes = target_obj + "_addBS_system"
        else:
            blendshape_nodes = self.blendshape_nodes_line_edit.text()
        
        # sort dictionary
        self.blendshape_line_edit_list
        
        ordered_ctrl_list = []
        ordered_attr_list = []
        
        for i in self.blendshape_line_edit_list:
            user_input_keys = self.user_input_dict.get(i)
            ordered_ctrl = user_input_keys[0].text()
            ordered_attr = user_input_keys[1].text()
            
            ordered_ctrl_list.append(ordered_ctrl)
            ordered_attr_list.append(ordered_attr)
            
        # Default nodes creation function    
        def create_default_blendshape_nodes():
            if cmds.objExists(target_obj+"_addBS_system"):
                # add target to existing blendshape_nodes
                blendshape_len = len(cmds.blendShape(blendshape_nodes, q=True, w=1))
                count_target = 0
                for i in self.cache_blendshape_object:
                    cmds.blendShape( target_obj+"_addBS_system", edit=True, t=(target_obj, blendshape_len+count_target, i, 1.0))
                    count_target+=1
                
            else:
                # create blendshape_nodes and add target
                cmds.select(cl=1)
                for i in self.cache_blendshape_object:
                    cmds.select(i,add=1)
                cmds.select(target_obj,add=1)    
                cmds.blendShape (foc=1,n=target_obj + "_addBS_system")
                
        # Custom nodes creation function
        def create_custom_blendshape_nodes():
            # add target to existing blendshape_nodes
            if cmds.blendShape(blendshape_nodes, q=True, w=1) is None:
                blendshape_len = 0
            else:
                blendshape_len = len(cmds.blendShape(blendshape_nodes, q=True, w=1))
            count_target = 0
            for i in self.cache_blendshape_object:
                cmds.blendShape(blendshape_nodes, edit=True, t=(target_obj, blendshape_len+count_target, i, 1.0))
                count_target+=1
                if i not in cmds.blendShape(blendshape_nodes, q=True, t=1):
                    print ("Maya Bug: Reassign target to blendshape nodes")
                    cmds.blendShape(blendshape_nodes, edit=True, t=(target_obj, blendshape_len+count_target, i, 1.0))
                    count_target+=1
                        
        # If user doesn't have custom nodes use code below
        if self.blendshape_nodes_line_edit.text() == "":
            create_default_blendshape_nodes()
        else:
            create_custom_blendshape_nodes()
        
        # Add attribute    
        count1 = 0  
        
        for i in ordered_attr_list:
            if cmds.objExists(ordered_ctrl_list[count1]+"."+i):
                count1+=1
                pass
            else:
                cmds.addAttr(ordered_ctrl_list[count1],ln=i ,at="float",min=0,max=10,dv=0)
                cmds.setAttr(ordered_ctrl_list[count1] + "." + i,e=1,k=1)
                count1+= 1
            
        # Create unitConversion nodes
        data_quantity = len(self.cache_blendshape_object)/1.0
        node_quantity = int(math.ceil(data_quantity))
           
        all_unitCon_nodes = []
        
        for i in range(node_quantity):
            cmds.shadingNode("unitConversion", au=1, n = blendshape_nodes + "_unitCon") # this node is much clearer in history list
            active_sel = cmds.ls(sl=1)[0]
            all_unitCon_nodes.append(active_sel)
        
        attribute_factor = 1.0/float(self.ratio_attr_line_edit.text())
        print (self.ratio_attr_line_edit.text())
        print (attribute_factor)
        
        for i in all_unitCon_nodes:
            cmds.setAttr(i + ".conversionFactor", attribute_factor)
            
        count = 0
        
        for i in all_keys:
            all_widgets_temp = self.concatenated_widgets_dict.get(i)
            print all_widgets_temp[3].text() + "." + all_widgets_temp[2].text()
            print all_unitCon_nodes[count] + ".input"
            print all_unitCon_nodes[count] + ".output"
            print blendshape_nodes + "." + (all_widgets_temp[0].text()).rpartition(":")[2]
            cmds.connectAttr(all_widgets_temp[3].text() + "." + all_widgets_temp[2].text(),all_unitCon_nodes[count] + ".input",f=1)
            cmds.connectAttr(all_unitCon_nodes[count] + ".output",blendshape_nodes + "." + (all_widgets_temp[0].text()).rpartition(":")[2],f=1)
            print "done"
            count +=1
            
        # As a tradition you must end operation logic with this
        cmds.select(cl=1)
        print ("Blendshape successfully added to {0} mesh :D".format(target_obj)),
        
    def delete_object(self):
        sender = self.sender()
        all_widgets_temp = self.concatenated_widgets_dict.get(sender)
        for i in all_widgets_temp:
            self.mid_layout.removeWidget(i)
            i.deleteLater()
            i = None
        
        # Clear the cache 
        del self.concatenated_widgets_dict[sender]
        del self.select_widgets_dict[all_widgets_temp[4]]
        del self.user_input_dict[all_widgets_temp[0]]
        
        self.cache_blendshape_object.remove(all_widgets_temp[0].text())  # very elegant way to retrieve lineedit value(JK)
        self.attr_name_list.remove(all_widgets_temp[2])
        self.target_ctrl_list.remove(all_widgets_temp[3])
        self.blendshape_line_edit_list.remove(all_widgets_temp[0])
    
    def select_control(self):
        # Query text by user selection
        if cmds.ls(sl=1)[0] in self.cache_blendshape_object:
            cmds.warning("please select target control")
        
        else:
            temp_text = cmds.ls(sl=1)[0]
            sender = self.sender()
            selected_target_control_line_edit = self.select_widgets_dict.get(sender)
            selected_target_control_line_edit.setText(temp_text)
    
    def select_all_control(self):
        all_keys = self.concatenated_widgets_dict.keys()
        
        if len(self.cache_blendshape_object) > 0:
            try:
                sel = cmds.ls(sl=1)[0]
                for i in all_keys:
                    self.concatenated_widgets_dict.get(i)[3].setText(sel)
            except:
                print ("no control selected"),
        else:
            print ("add blendshape first"),
                
    def create_new_object(self):
        for i in cmds.ls(sl=1):
            cmds.select(i)
            if cmds.ls(sl=1,type=["mesh","nurbsSurface"],dag=1,long=1):
                for i in cmds.ls(sl=1):
                    
                    # don't receive object that's already stored
                    if i in self.cache_blendshape_object:
                        continue
                        
                    else:
                        # Store the blendshape object to list
                        self.cache_blendshape_object.append(i)
                        
                        # Declare object name
                        object_name = i
                        cmds.select(cl=1)
                        
                        # Create the UI element when clicked
                        
                        delete_button = QtWidgets.QPushButton()
                        delete_button.setMaximumHeight(22)
                        delete_button.setIcon(QtGui.QIcon(":deleteActive.png"))
                        
                        select_button = QtWidgets.QPushButton()
                        select_button.setMaximumHeight(22)
                        select_button.setIcon(QtGui.QIcon(":aselect.png"))
                        
                        blendshape_line_edit = QtWidgets.QLineEdit(object_name)
                        blendshape_line_edit.setMinimumHeight(20)
                        blendshape_line_edit.setAlignment(QtCore.Qt.AlignCenter)
                        blendshape_line_edit.setReadOnly(True)
                        
                        target_control_line_edit = QtWidgets.QLineEdit()
                        target_control_line_edit.setMinimumHeight(20)
                        target_control_line_edit.setReadOnly(True)
                        target_control_line_edit.setAlignment(QtCore.Qt.AlignCenter)
                        
                        # check if namespace is present
                        if ":" in object_name:
                            atr_name_line_edit = QtWidgets.QLineEdit(object_name.rpartition(":")[2])
                        else:
                            atr_name_line_edit = QtWidgets.QLineEdit(object_name)
                            
                        atr_name_line_edit.setMinimumHeight(20)
                        atr_name_line_edit.setAlignment(QtCore.Qt.AlignCenter)
                        
                        # separator
                        separator_two = QtWidgets.QFrame()
                        separator_two.setFrameShape(separator_two.VLine)
                        separator_two.setLineWidth(2)
                        separator_two.setStyleSheet("border: 1px solid grey")
                        
                        separator_three = QtWidgets.QFrame()
                        separator_three.setFrameShape(separator_three.VLine)
                        separator_three.setLineWidth(2)
                        separator_three.setStyleSheet("border: 1px solid grey")
                        
                        # Create the layout
                        
                        custom_layout = QtWidgets.QHBoxLayout()
                        custom_layout.addWidget(blendshape_line_edit)
                        custom_layout.addWidget(delete_button)
                        custom_layout.addWidget(separator_three)
                        custom_layout.addWidget(target_control_line_edit)
                        custom_layout.addWidget(select_button)
                        custom_layout.addWidget(separator_two)
                        custom_layout.addWidget(atr_name_line_edit)

                        self.mid_layout.addLayout(custom_layout)
                        
                        # append all data to cache 
                        # dict
                        widgets_list = [blendshape_line_edit, delete_button, 
                        atr_name_line_edit,target_control_line_edit,select_button,separator_two,separator_three]
                        
                        user_data_widget_list = [target_control_line_edit,atr_name_line_edit]
                        
                        self.concatenated_widgets_dict[delete_button] = widgets_list
                        self.select_widgets_dict[select_button] = target_control_line_edit
                        self.user_input_dict[blendshape_line_edit] = user_data_widget_list
                        
                        # list
                        self.attr_name_list.append(atr_name_line_edit)
                        self.target_ctrl_list.append(target_control_line_edit)
                        self.blendshape_line_edit_list.append(blendshape_line_edit)
                        
                        # Create connection to the object button
                        delete_button.clicked.connect(self.delete_object)
                        select_button.clicked.connect(self.select_control)
                        
                        cmds.select(cl=1)

            else:
                om.MGlobal.displayWarning("only select mesh object for blendshape target")  
                cmds.select(cl=1)
    
    def undo_chunk_create_new_object(self):
        cmds.undoInfo(openChunk=True,cn="Add Blendshape to list")
        try:
            addBlendshape.create_new_object(self) 
        finally:
            cmds.undoInfo(closeChunk=True) 

# Snippets by aronamao on github
# link: https://github.com/aronamao/PySide2-Collapsible-Widget
#-------------------------------------------------------------------------------------
class Header(QtWidgets.QWidget):
    """Header class for collapsible group"""

    def __init__(self, name, content_widget):
        """Header Class Constructor to initialize the object.

        Args:
            name (str): Name for the header
            content_widget (QtWidgets.QWidget): Widget containing child elements
        """
        super(Header, self).__init__()
        self.content = content_widget
        self.content.setVisible(False)
        self.expand_ico = QtGui.QPixmap(":teDownArrow.png")
        self.collapse_ico = QtGui.QPixmap(":teRightArrow.png")

        stacked = QtWidgets.QStackedLayout(self)
        stacked.setStackingMode(QtWidgets.QStackedLayout.StackAll)
        background = QtWidgets.QLabel()
        background.setStyleSheet("QLabel{ background-color: rgb(90, 90, 90); border-radius:2px}")

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(widget)

        self.icon = QtWidgets.QLabel()
        self.icon.setPixmap(self.expand_ico)
        layout.addWidget(self.icon)
        layout.setContentsMargins(11, 0, 11, 0)

        font = QtGui.QFont()
        font.setBold(True)
        label = QtWidgets.QLabel(name)
        label.setFont(font)

        layout.addWidget(label)
        layout.addItem(QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding))

        stacked.addWidget(widget)
        stacked.addWidget(background)
        background.setMinimumHeight(layout.sizeHint().height() * 1.5)

    def mousePressEvent(self, *args):
        """Handle mouse events, call the function to toggle groups"""
        self.expand() if not self.content.isVisible() else self.collapse()

    def expand(self):
        self.content.setVisible(True)
        self.icon.setPixmap(self.expand_ico)

    def collapse(self):
        self.content.setVisible(False)
        self.icon.setPixmap(self.collapse_ico)


class Container(QtWidgets.QWidget):
    """Class for creating a collapsible group similar to how it is implement in Maya

        Examples:
            Simple example of how to add a Container to a QVBoxLayout and attach a QGridLayout

            >>> layout = QtWidgets.QVBoxLayout()
            >>> container = Container("Group")
            >>> layout.addWidget(container)
            >>> content_layout = QtWidgets.QGridLayout(container.contentWidget)
            >>> content_layout.addWidget(QtWidgets.QPushButton("Button"))
    """
    def __init__(self, name, color_background=False):
        """Container Class Constructor to initialize the object

        Args:
            name (str): Name for the header
            color_background (bool): whether or not to color the background lighter like in maya
        """
        super(Container, self).__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._content_widget = QtWidgets.QWidget()
        if color_background:
            self._content_widget.setStyleSheet(".QWidget{background-color: rgb(73, 73, 73); "
                                               "margin-left: 2px; margin-right: 2px}")
        header = Header(name, self._content_widget)
        layout.addWidget(header)
        layout.addWidget(self._content_widget)

        # assign header methods to instance attributes so they can be called outside of this class
        self.collapse = header.collapse
        self.expand = header.expand
        self.toggle = header.mousePressEvent

    @property
    def contentWidget(self):
        """Getter for the content widget

        Returns: Content widget
        """
        return self._content_widget

# development phase code
if __name__ == "__main__":

    try:
        addBlendshapeWindow.close()
        addBlendshapeWindow.deleteLater()
    except:
        pass
    
    addBlendshapeWindow = addBlendshape()
    addBlendshapeWindow.show()