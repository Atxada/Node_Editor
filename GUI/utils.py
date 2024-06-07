# -*- encoding: utf-8 -*-
"""
Module with some helper functions
"""

import traceback
from PySide2 import QtCore, QtWidgets, QtGui
from pprint import PrettyPrinter

pp = PrettyPrinter(indent=4).pprint

def dumpException(e=None):
    """Prints out Exception message with traceback to the console

    :param e: Exception message
    :type e: Exception
    """
    # print("%s EXCEPTION:"% e.__class__.__name__, e)
    # traceback.print_tb(e.__traceback__)    python 2.7 incompatible?
    print ("EXCEPTION: ", e)
    

def loadStylesheet(instance, filename):
    """
    Loads an qss stylesheet to the current QApplication instance

    :param filename: Filename of qss stylesheet
    :type filename: str
    """
    # print ("load STYLE:", filename)
    file = QtCore.QFile(filename)
    # print ("open style: " + str(file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)))
    stylesheet = file.readAll()
    # print ("stylesheet content: ", stylesheet)
    instance.setStyleSheet(str(stylesheet))

def loadStylesheets(instance, *args):
    """
    Loads multiple qss stylesheets. Concatenates them together and applies the final stylesheet to the current QApplication instance

    :param args: variable number of filenames of qss stylesheets
    :type args: str, str,...
    """
    res = ""
    for arg in args:
        file = QtCore.QFile(arg)
        file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        stylesheet = file.readAll()
        res += "\n" + str(stylesheet)
    instance.setStyleSheet(res)