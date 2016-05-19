# pyCProject
Provides basic function to read a ContentMine [CProject](https://github.com/ContentMine/workshop-resources/blob/master/software-tutorials/cproject/README.md) and CTrees into python datastructures.

Main use is to read in all results.xml created by ami, and to be relate them to papers/metadata.


# Installation

You can install it from PyPI with

```
pip install pycproject
```

Another option is to install it into a [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/):

```
source activate YOURVIRTUALENV
pip install pycproject
```

Download and unzip the [source from github](https://github.com/ContentMine/pyCProject/archive/master.zip), change into the unzipped folder, then run

```
python setup.py build
python setup.py install
```

# Usage

You can then read a generated ContentMine-project in with

```
from pycproject.readctree import CProject
MYPROJECT = CProject("path_to_cproject", "cproject_name")
```
