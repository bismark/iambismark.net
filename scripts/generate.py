import os
import subprocess

subprocess.check_call(["hugo"])

path = os.path.join(os.getcwd(), "public")
for root, dirs, files in os.walk(path):
    if root == os.getcwd():
        continue
    if "index.xml" in files:
        os.remove(os.path.join(root, "index.xml"))
