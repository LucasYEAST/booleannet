# Note #
A newer version of the documentation is now maintained at: a [detailed documentation](http://atlas.bx.psu.edu/booleannet/booleannet.html)  See the [Tutorials](http://atlas.bx.psu.edu/booleannet/booleannet.html#Tutorials) for a quick overview on how the library works.


# Introduction #

The hybrid model solves the boolean rules via _piecewise linear differential equations_.
In this mode every node in the system will have three continuous variables associated with it a _concentration_, a _decay_, and a _threshold_ . Each node is considered `ON` when its concentration is greater than the threshold. Practically this means that a rule written as:

```
A = B and C 
```

will be solved as a differential equation of the form:

```
dA/dt = (( conc(B) > threshold(B)) and (conc(C) > threshold(C)) - decay(A) * conc(A) 
```

Here the boolean (first) term corresponds to the _regulated synthesis_ while the decay (second) term corresponds to _free (unregulated) dissociation_. The equation leads to the following dynamics for each node:

  * when the boolean term is `True` the equation is of the form `dA/dt = 1 - decay * A`
  * when the boolean term is `False` the equation is of the form `dA/dt = - decay * A`

This means that in time we may have either an exponential type increase (to a maximal value of `1/decay`) or an exponential type decrease (to zero) of the concentrations.

# Usage #

The engine can operate on the same syntax files as the [boolean mode](BooleanAPI.md), although one most likely will need to change the initialization parameters from `True/False` values to triplets like `(1.0, 2.0, 0.5)` corresponding to the actual _concentration_, _decay_ and _threshold_. An automatic conversion will take place if the initialization values correspond to the boolean mode:`True/False` values will be converted to `(1, 1, 0,5)/(0, 1, 0.5)`. Here is a typical use case:

```
import boolean, pylab

text = """
A = True
B = True 
C = False
1: A* = not C 
2: B* = A and B
3: C* = B
"""

engine = boolean.Engine( text=text, mode='plde' )
engine.initialize()
engine.iterate( fullt=8, steps=100 )

p1 = pylab.plot( engine.data['A'] , 'ob-' )
p2 = pylab.plot( engine.data['B'] , 'sr-' )
p3 = pylab.plot( engine.data['C'] , '^g-' )
pylab.legend( [p1,p2,p3], "A B C".split(), loc="best")

pylab.show()
```

Note how simple these equations are, could you predict what the shape of the curves for `A`, `B` and `C` will be like? How about the steady state values for each node? See the image at the bottom image for the answer.

# Advanced Usage #

There are common circumstances where the default behaviors need to be augmented to account for certain biological knowledge. The software provides great flexibility allowing one to alter all aspects of the process.

First some background on what takes place. Internally the software will dynamically generate a Python module that contains the time dependent component of the differential equations. It then numerically integrates this generated function with a fourth order [Runge-Kutta method](http://en.wikipedia.org/wiki/Runge-Kutta_methods). To modify the behavior we will need to modify this dynamically generated code.

By default the dynamically generated module will be located in the `autogen.py` file. For the example above the file will look something like this:
```
## dynamically generated code
# abbreviations: c=concentration, d=decay, t=threshold, n=newvalue
# [(0, 'A', (1.0, 1.0, 0.5)), (1, 'B', (1.0, 1.0, 0.5)), (2, 'C', (0.0, 1.0, 0.5))]
c0, d0, t0 = 1.000000, 1.000000, 0.500000 # A
c1, d1, t1 = 1.000000, 1.000000, 0.500000 # B
c2, d2, t2 = 0.000000, 1.000000, 0.500000 # C
dt = 0.1
x0 = c0, c1, c2
def derivs( x, t):
    c0, c1, c2 = x
    n0, n1, n2 = 0.0, 0.0, 0.0
    
    #1: A * = not C
    n0 = float( not  ( c2 > t2 )  ) - d0 * c0
    
    #2: B * = A and B
    n1 = float(  ( c0 > t0 )  and  ( c1 > t1 )  ) - d1 * c1
    
    #3: C * = B
    n2 = float(  ( c1 > t1 )  ) - d2 * c2

    return ( n0, n1, n2 ) 
```

Compare this file to the original text input. The code above can be understood in the following way. Each node is associated an index, for example the `B` node has the index of `1`. The `c`, `d`, and `t` variables stand for the _concentration_, _decay_ and _threshold_ for the node index that follows the variable, this makes say `t1` is the threshold for node `B`. The `n` variable stands for **the change** in the value of the node. To make it easier to keep track of what is going on  each line is also displayed in a commented out form (with the `#` sign, these lines are not executed, are there only to allow one to keep track of what was the original line was).

Code generation can be interacted with in a manner similar to the BooleanAPI. The most important of these is the `OVERRIDE` function that gets called at every node generation.
Here is how one starts out overriding. First create an empty function that is assigned to the engine:

```
def override( node, indexer, tokens ):
    return None

engine = Engine( text=text, mode='plde' )
engine.OVERRIDE = override
engine.initialize( )
engine.iterate( fullt=FULLT, steps=STEPS )
```

then slowly build up the function, while watching how the code is being altered. In this example we notice that the levels of `A` and `C` return to initial values. But the levels for `B` change from a concentration of 1 (`True`) to a concentration of 0 (`False`). What if we wished to simulate a system where the levels of node `B` are periodically replenished, e.g. repeatedly set to an exponential increase between 7 and 9th second of every 10 second interval. The override function above would need to take the following form:

```
from boolean import helper

def override( node, indexer, tokens ):

    if node == 'B':
        
        changeB = helper.change( 'B', indexer)
        concB   = helper.conc( 'B', indexer)
        decayB  = helper.decay( 'B', indexer)
        pieceB  = helper.piecewise( indexer=indexer, tokens=tokens )
        
        expr1 = "p1 = %s" % pieceB
        expr2 = "p2 = 1 - %s * %s" % (decayB, concB)
        expr3 = "%s = choose( p1, p2, t )" % changeB 
        
        return [ expr1, expr2, expr3 ]
    
    return None
```
While you could directly write the node indices to produce `p2 = 1 - d1 * c1` for expression `expr2` it is highly advisable to rely on the helper functions (`change`, `conc`, `decay`) because these will produce the right values for the node even after inserting new nodes into the system.

This override function produces two kinds of potential changes for node `B`. One with the default piecewise differential equation and stored in `p1` the other is an exponential increase and stored in `p2`. In the third step it invokes the `choose` function to pick between the two. It is a good habit to put functions in a separate module and we can instruct the system load all functions from a module into the autogenerated code. To load all functions from a module called 'myfunctions.py' we would need to write:

```
engine.iterate( fullt=FULLT, steps=STEPS, localdefs='myfunctions' )
```

The override and this line above will now produce the following internal code (compare it to the original one)

```
from myfunctions import *
def derivs( x, t):
    c0, c1, c2 = x
    n0, n1, n2 = 0.0, 0.0, 0.0
    
    #1: A * = not C
    n0  = float( not  ( c2 > t2 )  ) - d0 * c0
    
    #2: B * = A and B
    p1 = float(  ( c0 > t0 )  and  ( c1 > t1 )  ) - d1 * c1
    p2 = 1 -  d1  *  c1
    n1  = choose( p1, p2, t )
    
    #3: C * = B
    n2  = float(  ( c1 > t1 )  ) - d2 * c2

    return ( n0, n1, n2 ) 
```

We still need to specify what the `choose` function is so in `myfunctions.py` we will insert:

```
import math

def choose( p1, p2, t):
    "Every ten seconds chooses p2"
    
    mult = math.floor( t / 10.0)
    t = t - 10 * mult 

    if 7 < t < 9:
        return p2
    else:
        return p1
```

This achieves what we wanted, the B node in our system is now executing a different behavior every ten seconds producing the following output:

![http://booleannet.googlecode.com/svn/webdata/example-hybrid-override.png](http://booleannet.googlecode.com/svn/webdata/example-hybrid-override.png)

Please see the examples in the source code download. We have a large number of demos and examples that cover a wide variety of use cases.