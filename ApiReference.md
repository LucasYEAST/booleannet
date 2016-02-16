# Note #
A newer version of the documentation is now maintained at: a [detailed documentation](http://atlas.bx.psu.edu/booleannet/booleannet.html)  See the [Tutorials](http://atlas.bx.psu.edu/booleannet/booleannet.html#Tutorials) for a quick overview on how the library works.

# Programming Interface Reference #

Below we document the class and method signatures. This is a quick reference, some functionality is explained in  more detail at [BooleanAPI](BooleanAPI.md) and [HybridAPI](HybridAPI.md).

### Engine Creation ###


```
engine = boolean.Engine( mode='sync', text=text )
#
# mode may be: sync, async or plde corresponding to
# synchronous, asycnhronous and piece-wise linear differential equations
```

### State Initialization ###

```

def missing( node ):
    return True

engine.initialize( misssing=missing, default=dict(A=True) )

#
# both the missing, and default parameters are optional
# the missing parameter needs to be a function that, if 
# present will be called for every node that was not 
# initialized in the main body of the text input
#
# the parameter named default, if present is used to override all values
# that may be set beforehand either in the text file or via the missing
# parameter
#
```

### State Modifications ###

```
from boolean import util
text = util.modify_states(text=text, turnon=["A", "B"], turnoff=["C", "D"])

#
# a convenience function that modifies the input rules
# it turns on or off nodes (sets the nodes to True or False) 
# and comments out updating rules for each node, print the text
# to see what it does
#
```

### Operation Override in sync/async Modes ###

```
# setting and getting node values
engine.RULE_SETVALUE ( state, name, value, parser)
engine.RULE_GETVALUE ( state, name, parser)

# changing the semantics of the operators 
engine.RULE_AND (node1, node2, parser)
engine.RULE_OR  (node1, node2, parser)
engine.RULE_NOT (node, parser)
```

### Operation Override in PLDE Mode ###

The `indexer` is a dictionary that contains the numerical index for every node i.e. the index for node `MT1` is `indexer['MT1']`.

```
# called before every node, needs to return None
# for nodes that should not be overriden,
engine.OVERRIDE( node, indexer, tokens )

# modifies initialization lines, params is a dictionary 
# containing the states for each node
engine.INIT_LINE( params ) 

# modify the default equation that is created
engine.DEFAULT_EQUATION( tokens, indexer )
```

### PLDE Helper Functions ###

Simple functions to make your program more reusable. Used when overriding node behavior in PLDE mode.
```

# return the newvalue, concentration, decay 
# and treshold for each node. 
helper.change( node, indexer )
helper.conc ( node, indexer )
helper.decay( node, indexer )
helper.threshold( node, indexer )

# automatically extracts the proper parameters to generate 
# a hill or a proportion function for the node (see naming conventions)

helper.hill_func( node, indexer, param )
helper.prop_func( node, indexer, param )
```