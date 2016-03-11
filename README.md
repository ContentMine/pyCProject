# pyCProject
Provides basic function to read a ContentMine CProject and CTrees into python datastructures.

Main use is to read in all results.xml created by ami, and to be relate them to papers/metadata.


# Usage

Best use would be to install it into a virtualenv:

```
source activate YOURVIRTUALENV
python setup.py build
python setup.py install
```

Within your virtualenv, you can then use it with 

```
from pycproject import readctree
```