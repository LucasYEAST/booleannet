# Note #
A newer version of the documentation is now maintained at: a [detailed documentation](http://atlas.bx.psu.edu/booleannet/booleannet.html)  See the [Tutorials](http://atlas.bx.psu.edu/booleannet/booleannet.html#Tutorials) for a quick overview on how the library works.

# Introduction #

The software comes with a series of helper function to facilitate its use. These range from built-in function generators i.e. a **hill** function or a random **proportions** generator, to easy parameter parsing and data collection routines. The `helper.py` and `util.py` modules contain these functions, below we document the most important ones. All the functions listed here are for convenience only.

# Parameter Input #

It is a very common use case to test the system with different sets of initial conditions or function parameters. Maintaining all these states can be a chore. The `Parameter()` class and its related functions were created to alleviate problems relating to keeping track of all the states. These functions operate on comma separated files that may be created with Excel. The files should be in the following format.

![http://booleannet.googlecode.com/svn/webdata/excel-data.png](http://booleannet.googlecode.com/svn/webdata/excel-data.png)

The first line contains the node ids, in this case `PIC1`, `MP`, `Ca+2`, and `Call`. Note that the node ids need not be unique. The second line contains the type of the value for the column. In this case `conc`, `decay`, `threshold` etc. Save this excel sheet into a **comma-separated format** then load it with:

```
from boolean import helper

lines = helper.read_parameters('parameter-data.csv')
```

The `lines` object returned by the helper method is a list that contains a nested _dictionary-like_ object for every row. In practice this means that the data in the table can be accessed by row, using the node name and the node type as indices.

```

# take first line
row = lines[0]

# access by keys
print row['PIC']['conc']     # prints 0.9
print row['PIC']['decay']    # prints 1.0
print row['MP']['gamma']     # prints 0.123
print row['Ca+2']['levels']  # prints 2.5

# access by attribute 
print row.PIC.conc           # prints 0.9
print row.MP.n               # prints 1.0

# values from the last row
print lines[-1].Call.status    # prints 'marginal'

# the attribute access works only if the nodes or labels 
# are valid python identifiers. i.e. Ca+2 is not 
```

Finally to streamline the loading of custom initialization parameters into the the engine
the `helper.py` module contains a function that will return another function that then can be used to initialize missing nodes in the system. For example to initialize the engine
based on the second row ( zero based counting!) one could write the following:

```
lines = helper.read_parameters('parameter-data.csv')
data  = lines[1] # second row
engine  = Engine( mode='lpde', text=text )
engine.initialize( missing=helper.initializer( data, default=(1,1,0.5) ) )
```

# Column Types #

Some helper functions are able to extract the proper information from the files as long as  some simple naming conventions are followed. For example the

```
helper.initialize( param )
```

module function can initialize nodes by looking up the **conc**, **decay** and **threshold** column labels. The hill function generator required the **h** and **n** labels, while the proportions generator looks for **rc** and **r** values.
