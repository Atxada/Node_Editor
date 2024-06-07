Node Editor 
==========================
Description
-----------
The initial goals of this project is to create an auto rig for maya, get a better understanding of Qt Framework, 
and integrating custom GUI to Maya application.

I planning to continue developing this project architecture by adding more function and features as i develop my knowledge.
The main reason to create custom node editor is to visualize the rigging structure and promote reusability, so each
nodes contains it's own data structure that can be deserialized or serialized whenever needed.

This project have been fun and stressful for me, but through it all I learned so many things, thanks to all the resources and
people online that helped me when i'm stuck. As a gratitude, I want to share this project to anyone who interested.

Also, Big thanks to Pavel Křupala for the node editor GUI tutorial he provided, it helps me a lot to start building
my basic knowledge over Qt framework and many important topics (event/callback, debugging process, documentation, etc).
At last, i also continue to develop a few more helpful features and remake the node editor's graphic representation.

The resource link below:
https://www.blenderfreak.com/tutorials/node-editor-tutorial-series/

Features
--------

- full framework for creating customizable graph, nodes, sockets and edges, architecture by Pavel Křupala
- support for undo/redo and serialization into files
- support for implementing evaluation logic
- scene mode to edit nodes (dragging edge, rerouting edge, cutting edge, etc)
- simple set of math nodes to use as a demo
- support for saving custom executable script into shelf
- simple maya context (zSpline) 
- command line interpreters consisting some of handy script (? for help)
- tested in maya 2020.4 (python 2.7) and 2022 (python 3.7)

Documentation
-------------

- `Documentation <https://pyqt-node-editor.readthedocs.io/en/latest/>`_
