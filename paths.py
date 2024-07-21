import os
import sys

cwd = os.getcwd()
dir_name = sys.argv[0]

flags_path = os.path.join(cwd,dir_name,'flags_images')
json_path = os.path.join(cwd,dir_name,'used.json')