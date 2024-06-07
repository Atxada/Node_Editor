'''
created to automated building html docs
'''
import os

os.chdir(os.path.dirname(__file__)) # change current working directory
os.system('make clean')
os.system('make html')