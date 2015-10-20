from calculation import *
import numpy as np

sn = Element("Sn", "118.71", "Sn.pz-bhs.UPF")
lat = Lattice(4, 8.4410653932, 10)

specieslist = [sn, sn]
coordlist = [np.array([0.33333333, 0.66666666, 0.0]),
             np.array([0.66666666, 0.33333333, 0.0])]
st = Structure(specieslist, coordlist, lat)

params = dict(prefix='SnMLbands',
              jobname='SnMLbands.80105.mn.hopper.antwerpen.vsc',
              nstep=200,
              ecutwfc=50,
              ecutrho=200,
              nbnd=8,
              lspinorb='.false.',
              noncolin='.false.',
              conv_thr='10d-8',
              nkpt=20,
              etot_conv_thr='1.0d-4',
              forc_conv_thr='1.0d-5'
              )
cal = ParitiesCalculation(params, st)
print(cal.output.outfiles)
