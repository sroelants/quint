# import numpy as np
from subprocess import call
from output import *
from string import Template
from textwrap import dedent


class PwxCalculation(object):
    """ An abstract class all calculations inherit from. """
    def __init__(self, p, s):
        self.pars = p
        self.struc = s

    def control_input(self, p):
        return ("prefix = '" + p["prefix"] + "'\n"
                "calculation = 'scf'\n"
                "pseudodir = "
                "'/user/antwerpen/201/vsc20155/DFT/QEspresso/pseudopotentials'"
                "\n"
                "outdir = '/tmp/"+p['jobname']+"\n"
                "verbosity = 'high'\n"
                "nstep = "+("100" if 'nstep' not in p.keys() else
                            str(p['nstep'])) + "\n"
                )

    def system_input(self, p, s):
        return ("ibrav = " + str(s.lattice.ibrav) + "\n"
                "celldm(1) = " + str(s.lattice.alat) + "\n"
                "celldm(2) = " + str(s.lattice.ba) + "\n"
                "celldm(3) = " + str(s.lattice.ca) + "\n"
                "nat = " + str(len(s.specieslist)) + "\n"
                "ntyp = " + str(len(set(s.specieslist))) + "\n"
                "ecutwfc = " + str(p['ecutwfc']) + "\n"
                "ecutrho = " + str(p['ecutrho']) + "\n"
                "occupations = 'smearing'\n"
                "degaus = 0.02\n"
                "smearing = 'mp'\n"
                "nbnd = " + str(p['nbnd']) + "\n"
                "lspinorb = " + str(p['lspinorb']) + "\n"
                "noncolin = " + str(p['noncolin']) + "\n"
                )

    def electrons_input(self, p):
        return ("conv_thr = " + str(p['conv_thr']) + "\n"
                )

    def cell_input(self):
        return ""

    def atomic_input(self, s):
        return ("ATOMIC SPECIES\n" +
                "\n".join([x.info() for x in set(s.specieslist)]) +
                "\n\n"
                "ATOMIC POSITIONS (crystal)\n" +
                "\n".join([x.name + " " + str(y[0]) + " " + str(y[1]) + " " +
                          str(y[2]) for (x, y) in
                          zip(s.specieslist, s.coordlist)])
                )

    def kpts_input(self, p):
        return ("K_POINTS (automatic)\n"
                ""+str(p['nkpt']) + "  " + str(p['nkpt']) + "  1  0  0  0\n"
                )

    def generate_input(self, p, s):
        ''' Generates an input file from a structure and parameter set

            Piece together an SCF run input file from a structure and set
            of parameters. The building blocks are mostly common to all
            pw.x calculations, but the file is pieced together for a
            vanilla scf calculation specifically.

            Parameters:
            -----------
            p: Dictionary of QE parameters
            s: Structure object representing the system
        '''
        # TODO Implement this using template strings!
        # https://docs.python.org/3.4/library/string.html#template-strings
        return ("&control\n" +
                self.control_input(p) +
                "/\n\n"
                "&system\n" +
                self.system_input(p, s) +
                "/\n\n"
                "&electrons\n" +
                self.electrons_input(p) +
                "/\n\n" +
                self.cell_input() +
                self.atomic_input(s) +
                "\n\n" +
                self.kpts_input(p)
                )


class ScfCalculation(PwxCalculation):
    """ An SCF calculation.

    On initialization, an input file is generated from the
    parameters and structure. The input file is run, and
    an Output object is generated, which we can use to
    parse all the information.
    """

    def __init__(self, parameters, structure):
        PwxCalculation.__init__(self, parameters, structure)

        # Input generation
        inputstring = self.generate_input(parameters, structure)
        self.inputfilename = parameters['prefix'] + '.scf.in'
        write_to_file(inputstring, self.inputfilename)
        # Run pw.x and store output
        self.output = self.start_calculation(self.inputfilename)

    def control_input(self, p):
        return ("calculation = 'scf' \n" +
                super().control_input(p)
                )

    def start_calculation(self, filename):
        # TODO implement ACTUAL calculation starter
        outfilename = "SnMLbands.scf.out"
        call(["cp", "outfile", outfilename])
        return ScfOutput(outfilename)


class RelaxCalculation(PwxCalculation):
    """ A relaxation calculation.

    On initialization, an input file is generated from the
    parameters and structure. The input file is run, and
    an Output object is generated, which we can use to
    parse all the information.
    """
    def __init__(self, parameters, structure):
        PwxCalculation.__init__(self, parameters, structure)

        # Input generation
        inputstring = self.generate_input(parameters, structure)
        self.inputfilename = parameters['prefix'] + '.relax.in'
        write_to_file(inputstring, self.inputfilename)

        # Run pw.x and store output
        self.output = self.start_calculation(self.inputfilename)

    def control_input(self, p):
        return ("calculation = 'relax' \n" +
                super().control_input(p) +
                "etot_conv_thr = " + p['etot_conv_thr'] + "\n"
                "forc_conv_thr = " + p['forc_conv_thr'] + "\n"
                )

    def start_calculation(self, filename):
        # TODO implement ACTUAL calculation starter
        outfilename = "SnMLbands.relax.out"
        call(["cp", "relaxoutfile", outfilename])
        return RelaxOutput(outfilename)


class VcRelaxCalculation(PwxCalculation):
    """ A variable cell relaxation calculation.
        In essence, this mimics a regular relaxation calculation.
    """
    def __init__(self, parameters, structure):
        super().__init__(parameters, structure)

        # Input generation
        inputstring = self.generate_input(parameters, structure)
        self.inputfilename = parameters['prefix'] + '.vcrelax.in'
        write_to_file(inputstring, self.inputfilename)

        # Run pw.x and store output
        self.output = self.start_calculation(self.inputfilename)

    def control_input(self, p):
        return ("calculation = 'vc-relax' \n" +
                super().control_input(p) +
                "etot_conv_thr = " + p['etot_conv_thr'] + "\n"
                "forc_conv_thr = " + p['forc_conv_thr'] + "\n"
                )

    def cell_input(self):
        return ("&cell\n"
                "cell_dofree = '2Dxy'\n"
                "/\n"
                )

    def start_calculation(self, filename):
        # TODO implement ACTUAL calculation starter
        outfilename = "SnMLbands.vcrelax.out"
        call(["cp", "vcrelaxoutfile", outfilename])
        return VcRelaxOutput(outfilename)


class BandsCalculation(PwxCalculation):
    def __init__(self, parameters, structure):
        super().__init__(parameters, structure)

        # pw.x Input generation
        inputstring = self.generate_input(parameters, structure)
        self.inputfilename = parameters['prefix'] + '.bands.in'
        write_to_file(inputstring, self.inputfilename)

        # bands.x input generation
        bandsinputstring = self.generate_bandsinput(parameters)
        print(bandsinputstring)
        # Run pw.x and store output
        self.output = self.start_calculation(self.inputfilename)

    def control_input(self, p):
        return ("calculation = 'bands'\n" +
                super().control_input(p)
                )

    def kpts_input(self, p):
        inputstr = """
                    K_POINTS (crystal_b)¬
                    4¬
                    0.5   0.0   0.0   100¬
                    0.0   0.0   0.0   100¬
                    0.333333333333   0.333333333333   0.0   100¬
                    0.5   0.5   0.0   40¬ """
        return dedent(inputstr)

    def generate_bandsinput(self, p):
        """ Generate the bands.in input file.

        The file is presented in a Template string, which we can substitute
        against the parameters dictionary.
        """
        inputstr = """
                   &bands
                   prefix = '$prefix'
                   outdir = '/tmp/$jobname'
                   no_overlap = .true.
                   filband = .false.
                   plot_2d = .false.
                   lsym = .true.
                   /"""

        return Template(dedent(inputstr)).substitute(p)

    def start_calculation(self, filename):
        # TODO implement ACTUAL calculation starter
        outfilename = "SnMLbands.bands.out"
        # call(["cp","bandsoutfile", outfilename])
        return BandsOutput(outfilename, "bands.dat")


class ParitiesCalculation(PwxCalculation):
    """ A parities calculation.

    A non-scf calculation in TRI points (I'll assume these are Gamma and M, in a
    hexagonal lattice!).
    """
    def __init__(self, parameters, structure):
        super().__init__(parameters, structure)
        outfiles = []
        for point in ["G", "M"]:
            # pw.x input generation
            parameters.update({'point': point})
            inputstring = self.generate_input(parameters, structure)
            inputfilename = Template("$prefix.parities.$point.in").substitute(parameters)
            write_to_file(inputstring, inputfilename)
            outfiles.append(self.start_calculation(inputfilename, parameters))

        self.output = ParitiesOutput(outfiles)

    def start_calculation(self, filename,p):
        # TODO implement actual calculation
        outputfile = Template("SnML.parities.$point.out").substitute(p)
        return outputfile

    def kpts_input(self,p):
        inputstr = """
                    K_POINTS (crystal_b)
                    1
                    """
        G_string = "0.0     0.0     0.0     100"
        M_string = "0.5     0.0     0.0     100"
        return dedent(inputstr) + G_string if p['point'] is "G" else M_string


class Structure:
    ''' A wrapper for a crystal structure.

    A wrapper to contain all info on the atoms, their masses, pseudopotentials,
    atomic positions, etc...

    Instance variables:
        specieslist: List of species
        coordlist: List of position vectors (as numpy arrays)
        lattice: A Lattice holding the Bravais lattice info
    '''

    def __init__(self, sl, cl, lat):
        self.specieslist = sl
        self.coordlist = cl
        self.lattice = lat


class Element:
    ''' A wrapper to hold element information

    Wrapper to hold element name, mass and pseudopotential used.
    '''
    def __init__(self, name, mass, pseudo):
        self.name = name
        self.mass = mass
        self.pseudo = pseudo

    def info(self):
        return self.name + " " + self.mass + " " + self.pseudo


class Lattice:
    ''' A wrapper to hold lattice information (but NOT atom positions!'''
    def __init__(self, ibrav, alat, ca, ba=1):
        self.ibrav = ibrav
        self.alat = alat
        self.ca = ca
        self.ba = ba


def write_to_file(content, filename):
    handle = open(filename, 'w')
    handle.write(content)
    handle.close()
