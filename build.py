import itertools
from jinja2 import Environment, FileSystemLoader
import os
import shutil
from helper import *

DIST = "dist"
REPO = "webplates/symfony-logstash"

VERSIONS = ["1.5.6-1", "2.0.0-1", "2.1.3-1", "2.2.4-1", "2.3.4-1", "2.4.0-1"]

MATRIX = set(VERSIONS)

# Prepare Jinja
env = Environment(loader=FileSystemLoader(os.path.dirname(os.path.realpath(__file__))))

# Clear the dist folder
if os.path.isdir(DIST):
    shutil.rmtree(DIST, ignore_errors=True)
os.mkdir(DIST)

# Initialize state variables
paths = []
tags = []

# Initialize template
template = env.get_template('Dockerfile.template')

for image in MATRIX:
    path = DIST + "/" + minorize(image)
    os.makedirs(path, exist_ok=True)
    dockerfile = path + "/Dockerfile"
    template.stream(parent=image).dump(dockerfile)
    shutil.copytree("conf", path + "/conf")
    paths.append(path)
    tags.append(set(get_tags(image)))

with open(".auth", "r") as f:
    token = f.readline().rstrip()

delete_builds(REPO, token)
add_builds(REPO, token, paths, tags)

FORMAT = "%-35s %s"
print (FORMAT % ("PATH", "TAG"))

for c1, c2 in zip(paths, tags):
    for tag in c2:
        print ("%-35s %s" % (c1, tag))
