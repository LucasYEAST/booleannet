# Boolean Network Simulations #

The goal of this software package is to provide intuitive and accessible tools for simulating **biological regulatory networks** in a boolean formalism. Using this simulator biologist and bioinformaticians can specify their system in a simple textual language then explore various dynamic behaviors via a web interface or an application programming interface (API) each designed to facilitate scientific discovery, data collection and reporting.

The software is primarly distributed as [Python](http://www.python.org) source code and requires that [Python 2.4](http://www.python.org) (or later) be installed on the target computer.

## Introduction ##

When trying to understand the role and functioning of a regulatory network,
the first step is to assemble the components of the network and the interactions
between them. The experimental advances in the large scale mapping of regulatory networks are fairly recent, but modeling efforts date back to the end of 1960s thanks to the pioneering work of Stuart Kauffman and Rene Thomas.

In a Boolean representation we assume that nodes are equivalent, and their interactions form a directed graph in which each node receives inputs from its neighbors (nodes that are connected to it). The state of nodes is described by binary (ON/OFF) variables, and the dynamic behavior of each variable, that is, whether it will be ON or OFF at next moment, is governed by a Boolean function. In general, a Boolean or logical function is written as a statement acting on the inputs using the logical operators **and**, **or** and **not** and its output is ON(OFF) if the statement is true (false).

In this software package, we implement two advanced methodologies which combine discrete logical rules with more realistic assumptions regarding the relative timescales of the  processes. The first method introduces **asynchronous updates** where update times may be randomly chosen thus making the model stochastic. The second method associates a set of continuous variables (concentrations, decay rates and thresholds) to each discrete variable in the system. The dynamics of these continuous variables is determined by a _linear system of piecewise differential equations_, leading to a **hybrid model** in the manner first suggested by Leon Glass and collaborators.

  * A [general introduction and tutorial](BooleanAPI.md) on the boolean operating mode
  * A description of the [hybrid operating mode ](HybridAPI.md)
  * Get things done faster with [helper functions](HelperFunctions.md)
  * See the  [quick reference](ApiReference.md) for a reminder of how the library works.
  * Follow the [installation instructions](Installation.md).

**Note:** to run the examples you'll need to have [matplotlib](http://matplotlib.sourceforge.net/) installed.

## Examples ##

Here are a few example plots obtained while using Boolean Net to simulate:

  * Mammalian immune response to B. bronchiseptica infection  **[immune.txt](http://booleannet.googlecode.com/svn/webdata/immune.txt)**
  * Abscicis acid induced stomatal closure in plants  **[aba.txt](http://booleannet.googlecode.com/svn/webdata/aba.txt)**
  * T-cell large granular lymphocyte leukemia simulation  **[LGL.txt](http://booleannet.googlecode.com/svn/webdata/LGL.txt)** as input file

![http://booleannet.googlecode.com/svn/webdata/footer.png](http://booleannet.googlecode.com/svn/webdata/footer.png)

These and other examples can be found in the `examples` directory of the distribution

## Credits ##

The library has been conceived and programmed by [István Albert](http://www.personal.psu.edu/iua1/) using previous work, ideas and contributions from Song Li, [Juilee Thakar](http://www.phys.psu.edu/%7Ejthakar/) and Ranran Zhang. None of us would be thinking about Boolean Networks if it weren't for [Réka Albert](http://www.phys.psu.edu/~ralbert/).

For user convenience the following third party libraries are distributed with  the software:

  * [PLY](http://www.dabeaz.com/ply/) by David Beazley
  * [web.py](http://www.webpy.org) started by Aaron Schwartz
  * [functional.py](http://oakwinter.com/code/functional/) by Colin Winters

The following library must be also installed if the engine will be used in `plde` mode (piece-wise linear differential equations):

  * [matplotlib](http://matplotlib.sourceforge.net/) by Dave Hunter