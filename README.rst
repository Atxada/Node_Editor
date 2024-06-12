Node Editor 
==========================
.. image:: https://github.com/Atxada/Node_Editor/blob/main/docs/Node%20Editor%20UI.PNG
Description
-----------

The initial goal of this project is to create an auto-rig for Maya and get a better understanding of the Qt Framework to create a more complex GUI.

I plan to continue developing this project's architecture by adding more functions and features as I develop my knowledge. 
The main reason to create a custom node editor is to visualize the rigging structure and promote reusability. 
Each node contains its own data structure that can be deserialized or serialized whenever needed.
This project has been fun and stressful for me, but through it all, I learned so many things.
thanks to all the resources and people online who have helped me when I'm stuck. As a gratitude, I want to share this project with anyone interested.

Also, **big thanks to Pavel Křupala** for the node editor GUI tutorial he provided. It helps me a lot to start building my basic knowledge of the Qt framework and many important topics (event/callback, debugging process, sphinx documentation, etc.). After the course, I also continued to develop a few more helpful features and remake the node editor's graphic representation.

The resource link:
https://www.blenderfreak.com/tutorials/node-editor-tutorial-series/

Features
--------

- full framework for creating customizable graphs, nodes, sockets, and edges
.. image:: https://github.com/Atxada/Node_Editor/blob/main/docs/Example%20Node%20Editor.gif
- support for undo/redo and serialization into files
- support for implementing evaluation logic
- scene mode to edit nodes (dragging edge, rerouting edge, cutting edge, etc.)
.. image:: https://github.com/Atxada/Node_Editor/blob/main/docs/Mode%20Node%20Editor.gif
- simple set of math nodes to use as a demo
- support for saving custom executable scripts
- simple maya context (zSpline) 
- command line interpreters consisting of some handy scripts (? for help)
.. image:: https://github.com/Atxada/Node_Editor/blob/main/docs/Command%20line%20Node%20Editor.gif
- tested in Maya 2020.4 (python 2.7) and 2022 (python 3.7).

Links
-------------

- `Documentation <https://zeno-node-editor.readthedocs.io/en/latest/>`_
- `Linkedin <https://www.linkedin.com/in/aldo-aldrich-962975220/>`_

Testing
------------

1. Download files from the repository
2. Unzip the files, rename the folder **Node_Editor-main** to **Node_Editor_main**
3. Place the folder inside maya script directory:                 
   ``C:\Users<Username>\Documents\maya<version_number>\scripts``
4. Copy the following code to script editor
::
    from Node_Editor_main.ZCore import UI 
    
    try:
        zeno_rig_window.close()
        zeno_rig_window.deleteLater()
    except:
        pass
    
    zeno_rig_window = UI.ZenoMainWindow()
    zeno_rig_window.show()
5. Node Editor will show up and ready to use!
