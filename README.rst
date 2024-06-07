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
my basic knowledge over Qt framework and many important things (event/callback, debugging process, documentation, etc).

The resource link below:
https://www.blenderfreak.com/tutorials/node-editor-tutorial-series/

Features
--------

- provides full framework for creating customizable graph, nodes, sockets and edges
- full support for undo / redo and serialization into files in a VCS friendly way
- support for implementing evaluation logic
- hovering effects, dragging edges, cutting lines and a bunch more...
- provided 2 examples on how node editor can be implemented

Requirements
------------

- Python 3.x
- PyQt5 or PySide2 (using wrapper QtPy)

Installation
------------

::

    $ pip install nodeeditor


Or directly from source code to get the latest version


::

    $ pip install git+https://gitlab.com/pavel.krupala/pyqt-node-editor.git


Or download the source code from gitlab::

    git clone https://gitlab.com/pavel.krupala/pyqt-node-editor.git


Screenshots
-----------

.. image:: https://www.blenderfreak.com/media/products/NodeEditor/screenshot-calculator.png
  :alt: Screenshot of Calculator Example

.. image:: https://www.blenderfreak.com/media/products/NodeEditor/screenshot-example.png
  :alt: Screenshot of Node Editor

Other links
-----------

- `Documentation <https://pyqt-node-editor.readthedocs.io/en/latest/>`_

- `Contribute <https://gitlab.com/pavel.krupala/pyqt-node-editor/blob/master/CONTRIBUTING.md>`_

- `Issues <https://gitlab.com/pavel.krupala/pyqt-node-editor/issues>`_

- `Merge requests <https://gitlab.com/pavel.krupala/pyqt-node-editor/merge_requests>`_

- `Changelog <https://gitlab.com/pavel.krupala/pyqt-node-editor/blob/master/CHANGES.rst>`_
