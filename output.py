import numpy as np
import re
class PwxOutput:
    def __init__(self, out):
        self.outfile = out
    
    def total_energy(self):
        """Parse output file to get total energy

        Because this method should also work for relaxation 
        runs, in which a total energy is printed for every iteration,
        we traverse the file bottom-up, and return the first total energy we
        find.
        """
        with open(self.outfile) as handle:
            for line in handle.readlines().reverse():
                words = line.split()
                if words and words[0]=='!':
                    return words[4]

    def fermi_energy(self):
        """Parse output file to get Fermi energy

        Because this method should also work for relaxation 
        runs, in which the Fermi energy is printed for every iteration,
        we traverse the file bottom-up, and return the first Fermi energy we
        find.
        """
        with open(self.outfile) as handle:
            for line in handle.readlines().reverse():
                words = line.split()
                if len(words) == 6 and words[1]=='Fermi':
                    return words[4]

class ScfOutput(PwxOutput):
    def __init__(self, out):
        super().__init__(out)

class RelaxOutput(PwxOutput):
    """ A relaxation calculation with variable atomic positions

    A structure relaxation where the cell geometry is kept fixed, and the atoms
    are allowed to move. This is in essence a series of SCF calculations, and we
    have the ability to get the 'relaxed atomic coordinates' from this.
    """
    def __init__(self, out):
        super().__init__(out)
        
    def relaxed_coordinates(self):
        """ Parse output file to get the relaxed coordinates
       
        Split the file content at the 'Begin final coordinates' and "End final
        coordinates' part, and extract the new coordinates.
        """
        with open(self.outfile) as handle:
            content = handle.read()
        # Split content until we get the relevant section
        before, relevant = content.split('Begin final coordinates',1)
        cruft,relevant = relevant.split('ATOMIC_POSITIONS (crystal)',1)
        relevant, after = relevant.split('End final coordinates',1) 
        
        # Get coordinates in a list of string numbers
        coordinates = relevant.splitlines()[0:]
        # Convert them into arrays of floats
        coordarrays = [np.array( list(map(float, x.split()[1:]))) 
                        for x in coordinates]
        return coordarrays

class VcRelaxOutput(RelaxOutput):
    """ Relaxation calculation with variable cell dimensions.

    A special case of a structure relaxation, where both the atoms and the cell
    geometry is allowed to vary. This class extends the usual relaxation
    calculation, and has the added behavior that a 'relaxed lattice constant'
    can be obtained.
    """
    def __init__(self, out):
        super().__init__(out)
    
    def relaxed_alat(self):
        """ Parse output file to get the relaxed coordinates
       
        Split the file content at the 'Begin final coordinates' and "End final
        coordinates' part, and extract the new lattice constant.

        WARNING: We scale the lattice vectors such that the first lattice vector
        is again (1.0, 0.0, 0.0). This means this routine will NOT work if the
        first lattice vector is not along the x-direction!
        """
        
        with open(self.outfile) as handle:
            content = handle.read()
        # Split content until we get the relevant section
        before, relevant = content.split('Begin final coordinates',1)
        cruft,relevant = relevant.split('CELL_PARAMETERS',1)
        lines = relevant.splitlines()
        
        alat = lines[0].split()[1] # Containts trailing ')' !
        # Strip non-numeric characters from alat
        non_decimal = re.compile(r'[^\d.]+')
        alat = float(non_decimal.sub('', alat))

        scale = float(lines[1].split()[0])
        return alat*scale

class BandsOutput(PwxOutput):
    def __init__(self, out, dat):
        super().__init__(out)
        self.dat = dat


