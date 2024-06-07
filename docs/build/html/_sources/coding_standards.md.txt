# Coding standards

## File naming guidelines

* files in node editor package start with ```node_``` prefix

## Tools architecture guidelines

* GUI package include basic node editor functionality
* ZCore package include Tools UI, Tools System and all Zeno rig nodes

## Coding guidelines

* methods use Camel case naming
* variables/properties use Snake case naming
* The constructor ```__init__``` always contains all class variables for the entire class. This is helpful for new users, so they can
just look at the constructor and read about all properties that class is using in one place. Nobody wants any
surprises hidden in the code later
* methods inheriting (PySide2) Graphical class end with ```Graphics```
* nodeeditor uses custom callbacks and listeners. Methods for adding callback functions
are usually named ```addXYListener```
* custom events are usually named ```onXY```
* methods named ```doXY``` usually do certain tasks and also take care of low level operations
* classes ideally contain methods in this order:

    * ```__init__```
    * python magic methods (i.e. ```__str__```), setters and getters
    * ```initXY``` functions
    * listener functions
    * nodeeditor event fuctions
    * nodeeditor ```doXY``` and ```getXY``` helping functions
    * Qt5 event functions
    * other functions
    * optionally overridden Qt ```paint``` method
    * ```serialize``` and ```deserialize``` methods at the end*