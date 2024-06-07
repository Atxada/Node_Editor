from os.path import dirname, basename, isfile, join
import glob
modules = glob.glob(join(dirname(__file__), "*.py"))    # collect all module inside package
__all__ = [ basename(file)[:-3] for file in modules if isfile(file) and not file.endswith("__init__.py")]   # go through all file then append to __all__ 