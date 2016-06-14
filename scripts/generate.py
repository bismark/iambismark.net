#! /usr/bin/env python
import os
import subprocess

current_path = os.getcwd()
base_path = os.path.join(current_path, "iambismark.net")
os.chdir(base_path)
subprocess.check_call(["hugo"])

output_path = os.path.join(os.getcwd(), "public")

for root, dirs, files in os.walk(output_path):
    for filename in files:
        if filename == "index.xml" and root != output_path:
            os.remove(os.path.join(root, "index.xml"))
            continue

        path = os.path.join(root, filename)
        if filename.split(".", 1)[1] in ["html", "xml", "css"]:
            subprocess.check_call(["gzip", "--no-name", "--rsyncable", "--force", "--best", "--keep", path])


os.remove(os.path.join(output_path, "post", "index.html.gz"))
os.remove(os.path.join(output_path, "post", "index.html"))

os.chdir(current_path)
