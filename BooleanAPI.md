# Note #
A newer version of the documentation is now maintained at: a [detailed documentation](http://atlas.bx.psu.edu/booleannet/booleannet.html)  See the [Tutorials](http://atlas.bx.psu.edu/booleannet/booleannet.html#Tutorials) for a quick overview on how the library works.

# Introduction #

A Boolean Network is a set of boolean variables (nodes) that are updated
via rules (edges) connecting them. The system evolves by performing updates,
one iteration has elapsed when all updating rules have been performed once.
During these updates the system visits different states (_N_ nodes
have _2^N_ different states).

Different updating methodologies may be used. In _synchronous_ updating one
only commits the new values for the nodes at the end of
each iteration. In _asynchronous_ updating the new values of the nodes became
active at the moment they are assigned. The update order of the nodes may also be important. This order may be _fixed_, meaning that the order is always the same. It can be _random_ where the nodes are assigned new values in random order in each iteration, and finally it can be _rank-random_ where each node has a rank and within ranks the node order is randomized.

# Usage #

**BooleanNet** is a python library for performing boolean network simulations.
It provides an easy to use application programming interface (API) for
various simulation related tasks. It can execute instructions written out
in a simple text format and maintains a list of all visited states.

Here is a typical usage that runs 5 iterations:
```
import boolean
engine = boolean.Engine( mode='async', text=text )
engine.initialize()
engine.iterate( steps=5 )
```

The input data is a text (that can be read from a file) that lists the
inital conditions for the nodes and the updating rules that affect these nodes. The updating rules must be specified in the following form::

```
rank: target* = rule
```

For example:

```
1: A* = B and C
```

Meaning that the new value of A (specified as `A*`) will be equal to the values of `B` and `C` and that the rank of the update order is 1.

The rank is an integer value that represents the order of update (only used in _asynchronous_ mode). Lower ranks will get updated before higher ranks, but within ranks the update order is randomized. The star indicates that this is an update rule rather than
an initialization rule. For synchronous updates the order of updates will follow the order
in which the rules are listed.

Here is a more realistic example for what this text (file) might look like::

```
#
# initialization of the nodes
#
ABA = ABH1 = ERA1 = AGB1 = True
ERA1 = AGB1 = Random
GRC3 = Random

#
# updating rules
#
1: GPA1* = (S1P or not GCR1) and AGB1
1: Atrboh* = pHc and OST1 and ROP2 and not ABI1
1: H+ATPase* = not ROS and not pHc and not Ca2+c
2: AnionEM* = ((Ca2+c or pHc) and not ABI1 ) or (Ca2+c and pHc)
2: Depolar* = KEV or AnionEM  or (not H+ATPase) or (not KOUT) or Ca2+c
2: CaIM* = (ROS or not ERA1 or not ABH1) and (not Depolar)
... 
```

The initialization conditions can be `True/False` or `Random`,
this latter being a random choice between `True/False`. Multiple assignments
of the form `A = B = Random` are allowed  (note that this example will set `A` and `B`
to the same random value). It is also possible to set all uninitialized values to
`Random` or any other desired value. This can simplify the files, see later sections (Advanced Usage)
for how to accomplish this. When run in PLDE mode (Piecewise Linear Differential Equations) we have
the option of specifying other parameters during initialization. In that case each node of the network
may be characterized by an a triplet of values that correspoind to the
_inital concentration_, a _decay_ and a _threshold_ (see [HybridAPI](HybridAPI.md) for what these parameters mean).
Thus we could also write the inital conditions as:

```
ABA = ABH1 = ERA1 = AGB1 = (1, 2, 0.7)
```

meaning that the `concentration=1`, `decay=2` and the `threshold=0.7`.
Both kinds of initializations are accepted for every operating mode. Depending on
the mode (pure boolean or hybrid) the value will be converted the appropriate one, with the following conversions rules:
`True/False` values will be converted to `(1, 1, 0,5)/(0, 1, 0.5)` whereas
value triplets will be converted to the truth value of _concentration > threshold_.

During the simulation the engine collects all the states
that the system has visited. To view the states use:

```
for state in engine.states:
    print state
```

Each `state` is an object that provides access to the values of each node
either as a dictionary or as attribute. Note that while more convenient the attribute
access works only for node names that are valid python  identifiers i.e. `state.A` will
work but `state.Ca+2` will not. Here is an example:

```
for state in enigne.states:
    print state.A, state['A'], state['Ca+2']
```

Please see the `examples` directory for other many other use cases.

# Advanced Use #

The library allows the user to override multiple aspects of its operation. For example
one may inspect and alter the values right before setting or using them. This allows for
additional computations to take place or to make some decisions based on other biological
or empirical evidence, decisions that do not have a proper boolean representation. It is also possible to change how the operators themselves work, or make operators
work differently for different nodes.

## Advanced Initialization ##

Often it is inconvenient or impractical to explicitly initialize all nodes in the input file. The library offers the option of passing a custom function to the engine initializer that will be called for all nodes that are left uninitalized. This function needs to take one parameter and must return a `True/False` value in _sync_ and _async_ modes and a value triplet in _lpde_ modes.

```
import random, boolean

def randomizer( node_name ):
    return random.choice( [True, False] )
 
engine = boolean.Engine( mode='async', text=text )
engine.initialize( missing=randomizer )
```

The example above sets uninitialized nodes to a random state. In the example we are ignoring the
node name but it would be possible to make use of it i.e. in a gene regulatory network some genes might be more likely to start being set to a given state.
Occasionally we need to force an initialization value to override any other setting it might
take from the original file or the `missing` function, for those cases we can use the defaults parameter
a dictionary that is keyed by nodes with the desired values as keys:

```
engine = boolean.Engine( mode='async', text=text )
engine.initialize( missing=randomizer, defaults={ 'A':True, 'B':False } )
```

## Action Overriding ##

The software is designed with extensibility and adaptability in mind, and to that end it allows the user to override its behavior at different points of the execution. The following functions may be altered (we also list the function signatures for reference):

```
engine.RULE_SETVALUE ( state, name, value, parser)
engine.RULE_GETVALUE ( state, name, parser)

engine.RULE_AND (node1, node2, parser)
engine.RULE_OR  (node1, node2, parser)
engine.RULE_NOT (node, parser)
```

Each of these rules have proper default action and only need be assigned behaviors  if a special operation is desired. Typically the `RULE_SETVALUE` and `RULE_GETVALUE` functions more naturally lend themselves to interpretation. There is an important distinction between the two:
  * `RULE_SETVALUE` will be called while assigning a value to a node and it will overwrite the value.
  * `RULE_GETVALUE` will be called while querying the state of a node and will not overwrite the actual value of the node

We'll demonstrate the use of these by implementing a hypothetical scenario in a gene regulatory network where:

> _The expression level of gene `SAM1` is affected by unknown factors and it has been observed that its mRNA level occasionally and spontaneously resets to a low value (OFF). Also it has been empirically observed that the levels of protein `BLK2` can vary more than its mRNA levels thus indicating a post-translational supression_

Here is the model that captures these behaviors (we will omit listing the rules as
those are not relevant for the point we are making):

```
import random
from boolean import Engine, util

def local_setvalue( state, name, value, parser ):
    if name == 'SAM1':
        value = random.choice( [False, value] ) 
    return util.default_set_value( state, name, value, parser )

def local_getvalue( state, name, parser ):
    value = util.default_get_value( state, name, parser )
    if name == 'BLK2':            
        return random.choice( [False, value] )
    else:
        return value

engine = Engine( mode='async', text=text )
engine.RULE_SETVALUE = local_setvalue
engine.RULE_GETVALUE = local_getvalue 
engine.initialize()
engine.iterate( steps=5 )
```

The `state` parameter is an state object (see above) that contains the state of each node at the time the rule is triggered. The last of the parameters `parser` almost always can be ignored
(that is you won't need it make any use of it). It is there to allow for situations
where one would need to inspect the state of parser up to the point when the rule is
triggered (rarely needed if ever).
