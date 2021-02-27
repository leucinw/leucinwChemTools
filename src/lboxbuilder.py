
#===================================
#        Chengwen Liu              #
#      liuchw2010@gmail.com        #
#   University of Texas at Austin  #
#===================================


import argparse
import os
import sys
import numpy as np
from random import sample

'''Generate a Box of pure liquid with required density and (cubic) box size'''
def gen_pureLiquidBox(xyz):

  #figure out the total number of molecules according to size and density
  mass = 0.0
  massdict = {"H": 1.0079,  "C": 12.0107,  "N":14.0067,  "O":15.9994, "S":32.0648,  "P":30.9738, \
              "F":18.9984, "CL": 35.4529, "BR":79.9035, "NA":22.9898, "K":39.0983, "MG":24.3051}
  navogadro = 6.02214086 
  atoms = np.loadtxt(xyz, usecols=(1,), skiprows=1, dtype="str", unpack=True)
  for atom in atoms:
    mass += massdict[atom.upper()]
  volume = size**3.0
  nmolecule = (int(navogadro*volume/(mass/density)*0.1))

  #use xyzedit to generate the box and do minimization
  with open("tmp.in", "w") as f:
    f.write("19\n%s\n%s %s %s\nY\n"%(nmolecule, size,size,size))
  with open("shot.key","w") as f:
    f.write(f"parameters {prm}\n")
    f.write("openmp-threads 8\n")
    f.write("polarization mutual\n")
    f.write("polar-eps 10e-2\n")
  cmdstr = "%s %s -k shot.key < tmp.in "%(xyzedit, xyz)
  os.system(cmdstr)

  #rename the generated xyz file
  if not os.path.isfile("%s_2"%xyz):
    print("Box builder failed for %s !"%xyz)
  else:
    boxname = "%s-%sA.xyz"%(os.path.splitext(xyz)[0], int(size))
    os.system("mv %s_2 %s"%(xyz, boxname))
  return boxname

'''Generate a Box of Solvent with solute being soaked in it'''
def gen_soluteSolventBox():
  #generate a pure liquid box of the solvent molecule
  solvbox = gen_pureLiquidBox(solvent)

  #use xyzedit to soak the solute in the box
  cmdstr = "%s %s %s %s %s && wait"%(xyzedit, solute, prm, 20, solvbox)
  os.system(cmdstr)

  #rename the generated xyz file
  if not os.path.isfile("%s.xyz_2"%os.path.splitext(solute)[0]):
    print("Box builder failed for %s !"%solvent)
  else:
    os.system("mv %s.xyz_2 %s_in_%s_box.xyz"%(os.path.splitext(solute)[0], os.path.splitext(solute)[0], os.path.splitext(solvent)[0]))
  return 

'''Generate a Box of binary mixtures with specified molar fraction and size'''
def gen_binaryMixtureBox():
  #generate a pure liquid box of the solvent molecule
  solvbox = gen_pureLiquidBox(solvent)

  #some maths
  fsolv,_ = os.path.splitext(solvent)
  fsolu,_ = os.path.splitext(solute)
  atmgas = int(open(solvent).readlines()[0].split()[0])
  atmgal = int(open(solute).readlines()[0].split()[0])
  atmliq = int(open(solvbox).readlines()[0].split()[0])
  boxinfo= open(solvbox).readlines()[1]
  nmol = int(atmliq/atmgas)
  nsolute = int(molar1*nmol)
  nsolvent = nmol - nsolute

  #randomly replace part of solvent molecules with solute
  molidx = list(range(nmol))
  soluidx = sample(molidx, nsolute)
  solvidx = [i for i in molidx if i not in soluidx]
  xs, ys, zs = np.loadtxt(solvbox, usecols=(2,3,4), unpack=True, skiprows=2)
  atoms, atypes = np.loadtxt(solvbox, usecols=(1,5), unpack=True, skiprows=2, dtype="str")
  lines = open(solvent).readlines()[1:]
  connections = []
  for line in lines:
    dd = line.split()
    connections.append(dd[6:])

  xl, yl, zl = np.loadtxt(solute, usecols=(2,3,4), unpack=True, skiprows=1)
  atoml, atypel = np.loadtxt(solute, usecols=(1,5), unpack=True, skiprows=1, dtype="str")
  lines = open(solute).readlines()[1:]
  connectionl = []
  for line in lines:
    dd = line.split()
    connectionl.append(dd[6:])
  xcl = xl.mean()
  ycl = yl.mean()
  zcl = zl.mean()
  totalatms = nsolvent*atmgas + nsolute*atmgal

  #write solvent molecules
  atmnumber = 1 
  molnumber = 0
  fname = "%s_%s_mixture.xyz"%(fsolv, fsolu)
  with open(fname, 'w') as f:
    f.write("%5s Generated with lboxbuilder.py\n"%totalatms)
    f.write(boxinfo)
    for idx in solvidx:
      atmidx = (idx*atmgas)
      for i in range(atmidx, atmidx+atmgas):
        constr = "  ".join([str(int(j)+molnumber*atmgas) for j in connections[i-atmidx]])
        f.write("%4s%3s%12.6f%12.6f%12.6f%4s %s\n"%(atmnumber, atoms[i], xs[i], ys[i], zs[i], atypes[i], constr))
        atmnumber += 1
      molnumber += 1

    #write solute molecules
    molnumberl = 0
    atmnumberl = atmnumber
    for idx in soluidx:
      atmidx = (idx*atmgas)
      xc = xs[atmidx:atmidx+atmgas].mean()
      yc = ys[atmidx:atmidx+atmgas].mean()
      zc = zs[atmidx:atmidx+atmgas].mean()
      v = np.array([xc-xcl, yc-ycl, zc-zcl])
      for i in range(atmgal):
        constr = "  ".join([str(int(j)+atmnumber+molnumberl*atmgal-1) for j in connectionl[i]])
        f.write("%4s%3s%12.6f%12.6f%12.6f%4s %s\n"%(atmnumberl, atoml[i], xl[i]+v[0], yl[i]+v[1], zl[i]+v[2], atypel[i], constr))
        atmnumberl += 1
      molnumberl += 1

  #write keywords for liquid sim.
  with open("shot.key", "a") as f:
    f.write("ewald\n")
    f.write("ewald-cutoff 7\n")
    f.write("vdw-cutoff 9\n")
    f.write("neighbor-list\n")
  hasExe = False
  if os.path.isfile(os.path.join(path, "minimize")):
    minimize = os.path.join(path, "minimize")
    hasExe = True
  elif os.path.isfile(os.path.join(path, "minimize.x")):
    minimize = os.path.join(path, "minimize.x")
    hasExe = True
  else:
    print(f"minimize/minimize.x does not exist in {path}")
    
  #minimize the structure to RMS 1.0
  if hasExe:
    cmdstr = f"{minimize} {fname} -k shot.key 1.0"
    os.system(cmdstr)
  os.system(f"mv {fname}_2 {fname}")
  return

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-mode',   dest='mode',   required=True, help="mode choice: 1=pure liquid; 2=solvation; 3=binary mixture")  
  parser.add_argument('-solute', dest='solute', required=True, help="tinker xyz file of solute molecule")  
  parser.add_argument('-solvent',dest='solvent',required=False,help="tinker xyz file of solvent molecule")  
  parser.add_argument('-prm',    dest='prm',    required=True, help="tinker prm file")  
  parser.add_argument('-size',   dest='size',   required=True, help="box size in angstrom")  
  parser.add_argument('-density',dest='density',required=True, help="liquid density in g/cm^3")  
  parser.add_argument('-tinker', dest='path',   required=True, help="tinker path where executable located in")  
  parser.add_argument('-molar1', dest='molar1', required=False,help="molar fraction of the first/solute substance")  
  args = vars(parser.parse_args())

  global solute,solvent,prm,size,path,density,xyzedit,xyz

  mode = args["mode"]
  solute = args["solute"]
  solvent = args["solvent"]
  prm = args["prm"]
  size = float(args["size"])
  path = args["path"]
  density = float(args["density"])
  xyzedit = os.path.join(path, "xyzedit.x")
  if not os.path.isfile(xyzedit):
    xyzedit = os.path.join(path, "xyzedit")

  if mode == "1":
    gen_pureLiquidBox(solute)
  elif mode == "2":
    gen_soluteSolventBox()
  elif mode == "3":
    global molar1
    molar1 = float(args["molar1"])
    if not (0 < molar1 < 1):
      sys.exit("molar fraction must be between (0,1)")
    gen_binaryMixtureBox()
  else:
    sys.exit(f"Mode {mode} is not supported!")

if len(sys.argv) == 1:
  print('\033[93m' + " please use '-h' option to see usage" + '\033[0m')
else:
  main()
