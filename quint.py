""" An interface to facilitate a chain of Quantum Espresso calculations

We create a modular structure in which Quantum Espresso calculations can easily
be chained and combined as needed. This makes redundant copying of input
parameters across calculations unnecessary, and automatically generates all the
parsed files I want. In essence, this is a structured framework to do the many
hacky scripts I've written over the years.
"""


