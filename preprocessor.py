from output import *


class BandsPreprocessor:
    def __init__(output):
        self.output = output
        self.processed_data = process_data(output)

    def process_data(file):
        """ Process the bands data in the passed file

        Takes a data file, parses it, and returns a parsed file in a
        gnuplot-compatible format. Turns out, bands.x output files are already
        in a gnuplot-friendly format. :-)
        """
        return file


class ParitiesPreprocessor:
    def __init__(datfiles):
        self.output = output
        self.processed_data = process_data(output)

    def process_data(output):
        """ Process the parities files

        We're passed a list of output files, each containing the symmetries of
        the wavefuncties at a TRI point. Parse each of them individually and
        write the data to a gnuplot-compatible format.
        """
        gstring = "xk=(   0.00000,   0.00000,   0.00000  )"
        for file in output:
        with open(self.file) as handle:
            lines = handle.readlines()

        if gstring in lines:
            parse_gparities(lines)
            return 0
