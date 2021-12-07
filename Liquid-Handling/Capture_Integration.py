# Author: Anurag Kanase
# Program: Capture using camera when the 
"""
The program takes POST requests sent by the OT-2
and captures the images of the pipette and saves 
it into different file names, directories and respective
volumes. 

The program takes input in following order:

python Caputre_Integration.py Process_Name Unique_Name Volume FileNumber Directory 

This file is further analysed using Computer vision analysis

""" 

import sys
import cv2
import numpy as np 
import pandas as pd
import pathlib
cmd = sys.argv
print(cmd)

def create_directory(heute, dir_name, process_name, uniqe, roll):
	pathlib.Path(heute+dir_name).mkdir(parents=True, exist_ok=True)

def capture() 