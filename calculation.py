class Calculation(object):
    """ An abstract class all calculations inherit from. """

class ScfCalculation(Calculation):
    """ An SCF calculation. """

class RelaxCalculation(Calculation):
    """ A relaxation calculation. """

class VcCalculation(Calculation):
    """ A variable cell relaxation calculation."""

