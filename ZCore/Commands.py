from ZCore.ToolsSystem import OUTPUT_INFO, OUTPUT_SUCCESS, OUTPUT_WARNING, OUTPUT_ERROR

import cmd, math
import ZCore.Config as Config

class ZenoCommand(cmd.Cmd, object):
    prompt ="(Zeno) > "
    # use_rawinput = True   # good to know this default is true, and let cmdloop accept input()/raw_input()

    def __init__(self, app):
        super(ZenoCommand, self).__init__()
        self.app = app
        self.command_list = []
    
        # automate cmd list registration
        for func in dir(self):
            if func[:3] == "do_": self.command_list.append(func[3:])

    def default(self, arg): # handle unknown command
        self.app.outputLogInfo("unknown command: '%s'"%arg, OUTPUT_ERROR)

    def do_help(self, arg):
        # super(ZenoCommand, self).do_help(arg)
        # check if help also called with command to return docstring
        if arg: 
            try:
                doc = getattr(self, 'do_'+arg).__doc__
                if doc: 
                    self.app.outputLogInfo(doc)
                return
            except AttributeError: pass

        # get all nice name cmd to list
        func = self.command_list
        self.app.outputLogInfo("ZENO COMMANDS:", OUTPUT_WARNING, log_detail=False)
        self.app.outputLogInfo("============================", OUTPUT_WARNING, log_detail=False)
        self.custom_column(func)

    def custom_column(self, item_list, column_size=3, column_padding=4):
        ncolumn = int(math.ceil(len(item_list)/float(column_size))) # convert to float to get precise decimal value
        column_width = []
        # iterate through all item to find each column longest text
        for num in range(column_size):
            column_width.append(max(len(item) for item in item_list[num::column_size]) + column_padding)
        # print each item with width of longest text of corresponding column
        for num in range(ncolumn):
            item_in_row = [item for item in item_list if item in item_list[0+(num*column_size):column_size+(num*column_size)]]
            self.app.outputLogInfo("".join((item).ljust(column_width[index]) for index, item in enumerate(item_in_row)))

    # required 'do_' as prefix followed by command to bind command with this function
    def do_debug_on_screen(self, arg):
        """Show debug information on scene graphic"""
        try:
            active_editor = self.app.getCurrentNodeEditorWidget()
            if active_editor:
                if active_editor.debug_widget.isVisible():
                    active_editor.debug_widget.setVisible(False)
                    self.app.outputLogInfo("turn off: on-screen debug", OUTPUT_WARNING)
                else:
                    active_editor.debug_widget.setVisible(True)
                    self.app.outputLogInfo("turn on: on-screen debug", OUTPUT_WARNING)
                return
            self.app.outputLogInfo("error : no graphic scene found", OUTPUT_ERROR)
        except Exception as e: self.app.outputLogInfo(e, OUTPUT_ERROR)

    def do_debug_on_log(self, arg):
        """Show debug information on output log"""
        self.app.outputLogInfo("debug_on_log")

    def do_print(self, arg):
        """Print some text with argument"""
        self.app.outputLogInfo(arg)

    def do_newScene(self, arg):
        """Create new scene graph"""
        try: self.app.onFileNew()
        except Exception as e: self.app.outputLogInfo(e, OUTPUT_ERROR)

    def do_node(self, arg):
        """Create node from given node name"""
        args = arg.split()
        if len(args) == 0: return
        node_name = str(args[0])
        if len(args) > 1: node_amount = int(args[1])
        else: node_amount = 1
        reached_limit = False

        if node_name in Config.NODES_NAME:
            active_editor = self.app.getCurrentNodeEditorWidget()
            if node_amount > 20: 
                reached_limit = True
                args[1] = 20
            try:
                active_editor.scene.doDeselectItems(silent=True)
                x, y = active_editor.scene.getView().width()/2, active_editor.scene.getView().height()/2
                scenepos = active_editor.scene.getView().mapToScene(x, y)
                for index in range(node_amount):
                    node = active_editor.addNode(Config.NODES_NAME[node_name])
                    node.setPos(scenepos.x(), scenepos.y()+((node.node_graphic.height+10)*index))
                    node.doSelect()
            except Exception as e: self.app.outputLogInfo(e, OUTPUT_ERROR)
            if reached_limit: self.app.outputLogInfo("only 20 new nodes allowed at a time", OUTPUT_ERROR)

    def do_openScene(self, arg):
        """Open scene graph"""
        try: self.app.onFileOpen()
        except Exception as e: self.app.outputLogInfo(e, OUTPUT_ERROR)