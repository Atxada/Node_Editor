Node Editor 
==========================
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
- support for undo/redo and serialization into files
- support for implementing evaluation logic
- scene mode to edit nodes (dragging edge, rerouting edge, cutting edge, etc.)
- simple set of math nodes to use as a demo
- support for saving custom executable scripts
- simple maya context (zSpline) 
- command line interpreters consisting of some handy scripts (? for help)
- tested in Maya 2020.4 (python 2.7) and 2022 (python 3.7).

Documentation
-------------

- `Documentation <https://pyqt-node-editor.readthedocs.io/en/latest/>`_
