# Riverscapes Upload Tool

This is a simple proof-of-concept tool to get people started with uploading projects into

## Arguments:

* **project**: The path (absolute or relative) to the `project.xml` for the project you wish to upload.
* **--program**: *(optional)* The path to the program XML file. This defaults to the one at:


``` text
usage: main.py [-h] [--program PROGRAM] project

positional arguments:
  project            Path to the project XML file.

optional arguments:
  -h, --help         show this help message and exit
  --program PROGRAM  Path to the Program XML file (optional)
```

## Installation

**NB:** Even though this installation uses pip you need to use git to clone it from github. This means that you need to make sure git is in your PATH for whatever command-line environement you use

```bash
pip install https://github.com/Riverscapes/rspupload.git
```