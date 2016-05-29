#! /usr/bin/env python
import os
import subprocess

subprocess.check_call(["hugo"])

base_path = os.path.join(os.getcwd(), "public")
site_path = os.path.join(base_path, "iambismark.net")

aliases = ["blog.iambismark.net", "www.iambismark.net", "iambismark.nfshost.com"]

for alias in aliases:
    alias_path = os.path.join(site_path, alias)
    new_path = os.path.join(base_path, alias)
    os.rename(alias_path, new_path)

for root, dirs, files in os.walk(site_path):
    if root == site_path:
        continue
    if "index.xml" in files:
        os.remove(os.path.join(root, "index.xml"))
