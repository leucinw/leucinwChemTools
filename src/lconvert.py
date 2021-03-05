
#===================================
#        Chengwen Liu              #
#      liuchw2010@gmail.com        #
#   University of Texas at Austin  #
#===================================

import argparse
import os,sys,time
import subprocess
import numpy

# color
RED = '\033[91m'
GREEN = '\033[92m'
ENDC = '\033[0m'

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-i',     dest = 'input', required=True, help="input filename")  
  parser.add_argument('-o',     dest = 'output', default=None, help="output filename. Optional")
  parser.add_argument('-it',    dest = 'inType', required=True, choices = ["xyz", "txyz", "g09", "qcout", "mol", "mol2", "sdf", "psi4out"], help="input file type")
  parser.add_argument('-ot',    dest = 'outType', required=True, choices = ["xyz", "qcin", "psi4", "com", "txyz"], help="output file type")
  parser.add_argument('-q',     dest = 'QM', default="HF", type=str.upper, help="QM method")
  parser.add_argument('-b',     dest = 'basis',  default = "STO-3G", help="basis function for quantum job", type=str.lower)
  parser.add_argument('-c',     dest = 'charge', default = "0", help="total charge of the whole system", type=str.lower)
  parser.add_argument('-c1',    dest = 'charge1', default = "0", help="total charge of the first molecule")
  parser.add_argument('-c2',    dest = 'charge2', default = "0", help="total charge of the second molecule")
  parser.add_argument('-s',     dest = 'spin', default = "1", help="total spin of the whole system")
  parser.add_argument('-s1',    dest = 'spin1', default = "1", help="total spin of the first molecule")
  parser.add_argument('-s2',    dest = 'spin2', default = "1", help="total spin of the second molecule")
  parser.add_argument('-n1',    dest = 'number1', default = None, help="number of atoms of the first molecule")
  parser.add_argument('-bsse',  dest = 'bsse', default = None, help = "use bsse correction, e.g. CP")
  parser.add_argument('-j',     dest = 'jobType', default="sp", type=str.lower, help="job type, can be opt, sp, freq, cbs, sapt, opt+freq, dipole, esp. Default: sp")
  parser.add_argument('-d',     dest = 'disk', default = "10GB", help="size of disk to be used. Default: 10GB")
  parser.add_argument('-m',     dest = 'memory', default = "10GB", help="size of memory to be used. Default: 10GB")
  parser.add_argument('-n',     dest = 'nproc', default = "8", help="number of cores for Gaussian job. Default: 8")
  parser.add_argument('-conv',  dest = 'converge', default = " ", help="string, converge cariteria for gaussian opt job. Default: Gaussian default")
  parser.add_argument('-at',    dest = 'atomtype', nargs='+', default = None, help="atom types for txyz file. Please provide in a row")
  parser.add_argument('-tp',    dest = 'template', default = None, help="template txyz file used to convert to new txyz")
  args = vars(parser.parse_args())

  fi = args["input"]
  fo = args["output"]
  ti = args["inType"].upper()
  to = args["outType"].upper()
  fin,_ = os.path.splitexit(fi)[0] 
  fxyz = fin + ".tmpxyz"
  if (fo == None):
    fo = fin + "." + to.lower()
  if (to == "TXYZ"):
    ftxyz = fin + ".tmptxyz"
  cg = args["charge"]
  qm = args["QM"].upper()
  if qm == "CCSD_T":
    qm = "CCSD(T)"
  bf = args["basis"]
  sp = int(args["spin"])
  jt = args["jobType"]
  dk = args["disk"]
  me = args["memory"]
  np = args["nproc"]
  n1 = args["number1"]
  bsse = args["bsse"]
  c1 = args["charge1"]
  c2 = args["charge2"]
  s1 = args["spin1"]
  s2 = args["spin2"]
  at = args["atomtype"]
  tp = args["template"]
  con = args["converge"]

  def ToXYZ(fi,fo):
    if (ti in ["XYZ", "G09", "QCOUT", "MOL", "MOL2", "SDF"]):
      cmdstr = "babel -i%s %s -oxyz %s"%(ti.lower(), fi, fo)
    elif ti == "TXYZ":
      txyz2xyz(fi,fo)
    elif ti == "PSI4OUT":
      psiout2xyz(fi,fo)
    else:
      sys.exit(RED + f"File format {ti} not supported!"+ ENDC)
    subprocess.run(cmdstr,shell=True)
    return

  def ToTXYZ(fi,fo,at):
    # generate a temptxyz file with MM2 atom types
    if (ti in ["XYZ", "G09", "QCOUT", "MOL", "MOL2", "SDF"]):
      cmdstr = "babel -i%s %s -otxyz %s"%(ti.lower(), fi, ftxyz)
    elif ti == "TXYZ":
      cmdstr = ("cp %s %s"%(fi, ftxyz))
    elif ti == "PSI4OUT":
      psiout2xyz(fi, fxyz)
      cmdstr = f"babel -ixyz {fxyz} -otxyz {ftxyz} && rm -f {fxyz}"
    else:
      sys.exit(RED + f"File format {ti} not supported!"+ ENDC)
    subprocess.run(cmdstr,shell=True)
    # read atom types from txyz files
    # temparary solution, only for AMOEBA+ molecules!!!
    apfolder="/home/liuchw/apfolder/"
    if at != None:
      for a in at:
        if os.path.isfile(a):
          fname = os.path.join(os.getcwd(), a)
        elif os.path.isfile(os.path.join(apfolder, "txyz", a)):
          fname = os.path.join(apfolder, "txyz", a)
        else:
          sys.exit(RED + "Could not find atomtype files!"+ ENDC)
        types = numpy.loadtxt(fname, usecols=(5,), dtype="str", unpack=True, skiprows=1)
        atomtypes += list(types)
    # read atom types and connections from txyz file
    atomtypes_connections = []
    if tp != None:
      lines = open(tp).readlines()
      for line in lines[1:]:
        dd = line.split()
        atomtypes_connections.append(dd[5:])
      
    lines = open(ftxyz).readlines()
    with open(fo, "w")  as f:
      f.write("%6s Generated by lconvert.py\n"%lines[0].split()[0])
      for i in range(1,len(lines)):
        dd = lines[i].split()
        newline = "%6s%3s%12.6f%12.6f%12.6f"%(dd[0], dd[1], float(dd[2]), float(dd[3]), float(dd[4]))
        if atomtypes != []:
          dd[5] = atomtypes[i-1]
          newline += "   ".join(["%4s"%i for i in dd[5:]])
        elif atomtypes_connections != []:
          newline = newline + " " +  "   ".join(atomtypes_connections[i-1])
        else:
          print(RED + "[Warning] MM2 atom types used!" + ENDC)
        f.write(newline + "\n")
    os.remove(ftxyz)
    return

  def ToCOM(fi,fo):
    # generate a generic com file
    if (ti in ["XYZ", "COM", "G09", "QCOUT", "MOL", "MOL2", "SDF"]):
      cmdstr = "babel -i%s %s -ogau %s"%(ti.lower(), fi, fo)
    elif ti == "TXYZ":
      txyz2xyz(fi,fxyz)
      cmdstr = "babel -ixyz %s -ogau %s && rm -f %s"%(fxyz, fo, fxyz)
    elif ti == "PSI4OUT":
      psiout2xyz(fi, fxyz)
      cmdstr = "babel -ixyz %s -ogau %s && rm -f %s"%(fxyz, fo, fxyz)
    else:
      sys.exit(RED + f"File format {ti} not supported!"+ ENDC)
    subprocess.run(cmdstr,shell=True)
    # write more settings into com file
    fname, _ = os.path.splitext(fo)
    chk   = "%chk=" + fname + ".chk\n"
    nproc = "%Nproc="+np + "\n" 
    mem   = "%Mem="+me +"\n"
    
    if (jt.upper() == "OPT"):
      if con == ' ':
        extra =  "opt(calcFC, maxcycle=400) IOP(5/13=1) \n"
      else:
        extra =  "opt(calcFC, maxcycle=400, %s) IOP(5/13=1) \n"%con
    elif (jt.upper() == "OPT+FREQ"):
      extra = "IOP(5/13=1)\n"
    else:
      extra = '\n'

    if not bsse:
      counterpoise = ' '
    else:
      counterpoise = "counterpoise=2 " 

    if jt.upper() == "OPT+FREQ":
      key = " ".join(["#P", qm+"/"+bf, "opt", "freq", "MaxDisk=%s"%dk, extra])
    elif jt.upper() == "ESP":
      key = " ".join(["#P", qm+"/"+bf, " SP Density=Current SCF=Save NoSymm", "MaxDisk=%s"%dk, extra])
    elif jt.upper() == "OPT":
      key = " ".join(["#P", qm+"/"+bf,"NoSymm MaxDisk=%s"%dk, extra])
    else:
      key = " ".join(["#P", qm+"/"+bf, jt, "NoSymm MaxDisk=%s"%dk, extra])
    comment = " Generated by lconvert.py for %s job\n"%jt
    chgspin = " ".join([str(cg), str(sp), "\n"])
    
    with open(fo + "_2", 'w') as fout:
      fout.write(chk + mem + nproc + key + "\n" + comment + "\n" + chgspin)
      if not bsse:
        for line in open(fo).readlines()[5:]: 
          fout.write(line)
      else:
        lines = open(fo).readlines()[5:]
        for i in range(len(lines)-1):
          if i < int(n1):
            fout.write(lines[i].split("\n")[0] + "  1 \n")
          else:
            fout.write(lines[i].split("\n")[0] + "  2 \n")
        fout.write("\n")
    os.rename(fo+"_2", fo)
    return

  def ToQCHEM(fi,fo):
    # generate a generic qchem file
    if (ti in ["XYZ", "COM", "G09", "QCOUT", "MOL", "MOL2", "SDF"]):
      cmdstr = "babel -i%s %s -oqcin %s"%(ti.lower(), fi, fo)
    elif ti == "PSI4OUT":
      psiout2xyz(fi, fxyz)
      cmdstr = "babel -ixyz %s -oqcin %s && rm -f %s"%(fxyz, fo, fxyz)
    elif ti == "TXYZ":
      txyz2xyz(fi, fxyz)
      cmdstr = "babel -ixyz %s -oqcin %s && rm -f %s"%(fxyz, fo, fxyz)
    else:
      sys.exit(RED + f"File format {ti} not supported!"+ ENDC)
    subprocess.run(cmdstr,shell=True)
    # write user settings
    basis   = " BASIS=%s\n"%bf
    jobtype = " JOB_TYPE=%s\n"%jt
    method  = " METHOD=%s\n"%qm
    chgspin = cg + " " + sp + "\n"
    with open(fo + "_2", 'w') as fout:
      fout.write("$comment\n Generated by lconvert.py for %s job\n$end\n\n$molecule\n"%jt)
      fout.write(chgspin)
      for line in open(fo).readlines()[6:-3]:
        fout.write(line)
      fout.write("$rem\n" + method + basis + jobtype + "$end\n")
    os.rename(fo+"_2", fo)
    return

  def ToPSI4(fi,fo):
    def XYZ2PSI4(xyz,psi4):
      atoms  = numpy.loadtxt(xyz, usecols=(0,), dtype='str', unpack=True, skiprows=2)
      coords = numpy.loadtxt(xyz, usecols=(1,2,3), dtype='float', unpack=True, skiprows=2)
      with open(psi4,'w') as fout:
        fout.write("#Generated by lconvert.py for %s job\n\n"%jt)
        if (bsse == None) and (jt.upper() != "SAPT"):
          chgspin = str(cg) + " " + str(sp)
          fout.write("memory %s %s\n\nmolecule  {\n%s\n"%(me[:-2], me[-2:], chgspin))
          for n in range(len(atoms)):
            fout.write("%3s   %12.6f%12.6f%12.6f\n"%(atoms[n],float(coords[0][n]),float(coords[1][n]),float(coords[2][n])))
        else: 
          chgspin1 = c1 + " " + s1
          chgspin2 = c2 + " " + s2
          fout.write("memory %s %s\n\nmolecule  {\n%s\n"%(me[:-2], me[-2:], chgspin1))
          for n in range(int(n1)):
            fout.write("%3s   %12.6f%12.6f%12.6f\n"%(atoms[n],float(coords[0][n]),float(coords[1][n]),float(coords[2][n])))
          fout.write("--\n%s\n"%(chgspin2))
          for n in range(int(n1), len(atoms)):
            fout.write("%3s   %12.6f%12.6f%12.6f\n"%(atoms[n],float(coords[0][n]),float(coords[1][n]),float(coords[2][n])))
        fout.write("units angstrom\nno_reorient\n")
        fout.write("symmetry c1\n}\n\n")

        if (qm == "HF"):
          if jt.upper() == "OPT":
            fout.write("set OPT_COORDINATES CARTESIAN\n")
            fout.write("set G_CONVERGENCE GAU\n")
            fout.write("set GEOM_MAXITER 400\n")
            fout.write("set DYNAMIC_LEVEL 2\n")
            fout.write("optimize('%s/%s')\n"%(qm,bf))
            fout.write("\n")
            print(f"{fo} file generated!")
          elif jt.upper() == "SAPT":
            pass
          else:
            sys.exit(RED + "HF with %s is not supported!"%jt.upper() + ENDC)

        elif (qm == "MP2") or (qm == "MP2D"):
          fout.write("set {\nscf_type DF\n")
          fout.write("mp2_type DF\ne_convergence 7\nreference rhf\n}\n\n")
          if jt.upper() == "CBS": 
            if not bsse:
              if bf.upper() == "CC-PVTZ":
                fout.write("energy('%s/cc-pv[tq]z')\n"%qm)
                print(GREEN + f"{fo} file generated!" + ENDC)
              elif bf.upper() == "AUG-CC-PVTZ":
                fout.write("energy('%s/aug-cc-pv[tq]z')\n"%qm)
                print(GREEN + f"{fo} file generated!" + ENDC)
              else:
                sys.exit(RED + "MP2 CBS with %s is not supported!"%bf.upper() + ENDC)
            else:
              if bf.upper() == "CC-PVTZ":
                fout.write("energy('%s/cc-pv[tq]z', bsse_type='%s')\n"%(qm,bsse))
                print(GREEN + f"{fo} file generated!" + ENDC)
              elif bf.upper() == "AUG-CC-PVTZ":
                fout.write("energy('%s/aug-cc-pv[tq]z', bsse_type='%s')\n"%(qm,bsse))
                print(GREEN + f"{fo} file generated!" + ENDC)
              else:
                sys.exit(RED + "MP2 CBS BSSE with %s is not supported!"%bf.upper() + ENDC)
          elif jt.upper() == "SP":
            if not bsse:
              fout.write("energy('%s/%s')\n"%(qm,bf))
              print(GREEN + f"{fo} file generated!" + ENDC)
            else:
              fout.write("energy('%s/%s', bsse_type='%s')\n"%(qm,bf,bsse))
              print(GREEN + f"{fo} file generated!" + ENDC)
          elif jt.upper() == "OPT":
            fout.write("set OPT_COORDINATES CARTESIAN\n")
            fout.write("set G_CONVERGENCE GAU\n")
            fout.write("set GEOM_MAXITER 400\n")
            fout.write("set DYNAMIC_LEVEL 2\n")
            fout.write("optimize('%s/%s')\n"%(qm,bf))
            fout.write("\n")
            print(GREEN + f"{fo} file generated!" + ENDC)
          else:
            sys.exit(RED + "MP2 with %s is not supported!"%jt.upper() + ENDC)

        elif qm == "CCSD(T)":
          fout.write("set {\nscf_type DF\n")
          fout.write("mp2_type DF\ne_convergence 7\nreference rhf\n}\n\n")
          if jt.upper() == "CBS":
            if not bsse:
              fout.write("energy(cbs, corl_wfn='mp2', corl_basis='aug-cc-pv[tq]z', delta_wfn='ccsd(t)', delta_basis='aug-cc-pv[dt]z')\n")
              print(GREEN + f"{fo} file generated!" + ENDC)
            else:
              fout.write("energy(cbs, corl_wfn='mp2', corl_basis='aug-cc-pv[tq]z', delta_wfn='ccsd(t)', delta_basis='aug-cc-pv[dt]z', bsse_type='%s')\n"%bsse)
              print(GREEN + f"{fo} file generated!" + ENDC)
          if jt.upper() == "SP":
            if not bsse:
              fout.write("energy('ccsd(t)/%s')\n"%bf)
              print(GREEN + f"{fo} file generated!" + ENDC)
            else:
              fout.write("energy('ccsd(t)/%s', bsse_type='%s')\n"%(bf, bsse))
              print(GREEN + f"{fo} file generated!" + ENDC)
        else: 
          fout.write("e_convergence 7\nreference rhf\n\n\n")
          if jt.upper() == "SP":
            if not bsse:
              fout.write("energy('%s/%s')\n"%(qm,bf))
              print(GREEN + f"{fo} file generated!" + ENDC)
            else:
              fout.write("energy('%s/%s', bsse_type='%s')\n"%(qm,bf, bsse))
              print(GREEN + f"{fo} file generated!" + ENDC)

        if jt.upper() == "SAPT":
          fout.write("set {\nscf_type DF\n")
          fout.write("e_convergence 7\nreference rhf\n")
          fout.write("basis %s\n"%bf)
          fout.write("freeze_core True\n")
          fout.write("guess SAD\n}\n")
          fout.write("energy('sapt2+')\n")
          print(GREEN + f"{fo} file generated!" + ENDC)
        if jt.upper() == "DIPOLE":
          fout.write('set PROPERTIES_ORIGIN ["COM"]\n')
          fout.write("properties('PBE0/%s', properties=['dipole'], title='Acetate')\n"%bf)
          print(GREEN + f"{fo} file generated!" + ENDC)
      return

    if ti == "XYZ":
      cmdstr = "cp %s %s"%(fi, fxyz)
    elif ti == "PSI4OUT":
      psiout2xyz(fi, fxyz)
    elif (ti in ["COM", "G09", "QCOUT", "MOL", "MOL2", "SDF"]):
      cmdstr = "babel -i%s %s -oxyz %s"%(ti.lower(), fi, fxyz)
    elif ti == "TXYZ":
      txyz2xyz(fi, fxyz)
    else:
      sys.exit(RED + f"File format {ti} not supported!"+ ENDC)
    subprocess.run(cmdstr,shell=True)

    # convert tempxyz to psi4
    XYZ2PSI4(fxyz, fo)
    os.remove(fxyz)
    return
    
  def psiout2xyz(finp, fout):
    lines = open(finp).readlines()
    for n in range(len(lines)):
      if "Final optimized geometry " in lines[n]:
        break
    atoms = []
    coords = []
    for n in range(n+6, len(lines)):
      if lines[n] == "\n":
        break
      dd = lines[n].split()
      atoms.append(dd[0])
      coords.append(dd[1:4])
    with open(fout, "w") as f:
      f.write("%3s\nconverted from %s\n"%(len(atoms), finp))
      for n in range(len(atoms)):
        f.write("%3s%12.6f%12.6f%12.6f\n"%(atoms[n], float(coords[n][0]), float(coords[n][1]), float(coords[n][2])))
    return
          
  def txyz2xyz(finp, fout):
    atoms = np.loadtxt(finp, usecols=(1,), dtype="str", unpack=True,skiprows=1)
    xs,ys,zs = np.loadtxt(finp, usecols=(2,3,4), dtype="float", unpack=True,skiprows=1)
    with open(fout, "w") as f:
      f.write("%3s\nconverted from %s\n"%(len(atoms), finp))
      for atom,x,y,z in zip(atoms,xs,ys,zs):
        f.write("%3s%12.6f%12.6f%12.6f\n"%(atom, x, y, z))
    return

  if (to == "COM"):
    ToCOM(fi, fo)
  elif (to == "PSI4"):
    ToPSI4(fi, fo)
  elif (to == "QCIN"):
    ToQCHEM(fi, fo)
  elif (to == "XYZ"):
    ToXYZ(fi, fo)
  elif (to == "TXYZ"):
    ToTXYZ(fi, fo, at)
  else:
    sys.exit(RED + f"File format {ti} not supported!"+ ENDC)
  return

if len(sys.argv) == 1:
  print(GREEN + " An example: " + ENDC + "python lconvert.py -i water.xyz -it xyz [-o water.com] -ot com -j opt -q MP2 -b cc-pvtz -c 0 -s 1 -d 10GB -m 20GB -n 10")
  sys.exit(RED + " For full usage, please run: " +ENDC + GREEN + "python lconvert.py -h" + ENDC)
else:
  main()
