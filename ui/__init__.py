from .element import *
from .screen import *
from .stage import *

# Draw the stage first
Element.registry.remove(Stage)
Element.registry.insert(0, Stage)