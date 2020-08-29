
#===================================
#        Chengwen Liu              #
#      liuchw2010@gmail.com        #
#   University of Texas at Austin  #
#===================================


import argparse
import os,sys,time
import subprocess
from colorama import Fore
import numpy

def main():
  #===>>>
  parser = argparse.ArgumentParser()
  parser.add_argument('-i',     dest = 'input', required=True)  
  parser.add_argument('-o',     dest = 'output', required=True)
  parser.add_argument('-it',    dest = 'inType', required=True, choices=["xyz", "txyz", "g09", "qcout", "mol", "mol2", "sdf"])
  parser.add_argument('-ot',    dest = 'outType', required=True, choices = ["xyz", "qcin", "psi4", "com", "txyz"])
  parser.add_argument('-q',     dest = 'QM', choices = ["HF", "MP2", "B3LYP", "wB97XD", "CCSD_T", "PBE0"], default="HF")
  parser.add_argument('-b',     dest = 'basis',  default = "STO-3G")
  parser.add_argument('-c',     dest = 'charge', default = "0")
  parser.add_argument('-c1',    dest = 'charge1', default = None)
  parser.add_argument('-c2',    dest = 'charge2', default = None)
  parser.add_argument('-s',     dest = 'spin', default = "1")
  parser.add_argument('-s1',    dest = 'spin1', default = None)
  parser.add_argument('-s2',    dest = 'spin2', default = None)
  parser.add_argument('-n1',    dest = 'number1', default = None)
  parser.add_argument('-bsse',  dest = 'bsse', default = None)
  parser.add_argument('-j',     dest = 'jobType', choices = ["opt", "sp", "freq", "cbs", "sapt", "opt+freq", "dipole"], default="sp")
  parser.add_argument('-d',     dest = 'disk', default = "10GB")
  parser.add_argument('-m',     dest = 'memory', default = "10GB")
  parser.add_argument('-n',     dest = 'nproc', default = "8")
  parser.add_argument('-at',    dest = 'atomtype', default = None)
  args = vars(parser.parse_args())

  #!==>
  #==========================================================================
  def ToXYZ(fi,fo):
    if ti == "XYZ":
      cmdstr = "babel -ixyz %s -oxyz %s"%(fi, fo)
    elif ti == "TXYZ":
      cmdstr = "babel -itxyz %s -oxyz %s"%(fi, fo)
    elif ti == "G09":
      cmdstr = "babel -ig09 %s -oxyz %s"%(fi, fo)
    elif ti == "QCOUT":
      cmdstr = "babel -iqcout %s -oxyz %s"%(fi, fo)
    elif ti == "MOL":
      cmdstr = "babel -imol %s -oxyz %s"%(fi, fo)
    elif ti == "MOL2":
      cmdstr = "babel -imol2 %s -oxyz %s"%(fi, fo)
    elif ti == "SDF":
      cmdstr = "babel -isdf %s -oxyz %s"%(fi, fo)
    else:
      cmdstr = ("echo 'File format %s not supported!'"%ti)
    subprocess.run(cmdstr,shell=True)
    return
  #==========================================================================
  #!<==

  #!==>
  #==========================================================================
  def ToTXYZ(fi,fo,at):
    if ti == "XYZ":
      cmdstr = "babel -ixyz %s -otxyz %s"%(fi, "tmp.txyz")
    elif ti == "TXYZ":
      cmdstr = "babel -itxyz %s -otxyz %s"%(fi, "tmp.txyz")
    elif ti == "G09":
      cmdstr = "babel -ig09 %s -otxyz %s"%(fi, "tmp.txyz")
    elif ti == "QCOUT":
      cmdstr = "babel -iqcout %s -otxyz %s"%(fi, "tmp.txyz")
    elif ti == "MOL":
      cmdstr = "babel -imol %s -otxyz %s"%(fi, "tmp.txyz")
    elif ti == "MOL2":
      cmdstr = "babel -imol2 %s -otxyz %s"%(fi, "tmp.txyz")
    elif ti == "SDF":
      cmdstr = "babel -isdf %s -otxyz %s"%(fi, "tmp.txyz")
    else:
      cmdstr = ("echo 'File format %s not supported!'"%ti)
    subprocess.run(cmdstr,shell=True)
    atomtypes = numpy.loadtxt(at, usecols=(0,), dtype="str", unpack=True)
    lines = open("tmp.txyz").readlines()
    with open(fo, "w")  as f:
      f.write("%6s Generated by lconvert.py\n"%lines[0].split()[0])
      for i in range(1,len(lines)):
        dd = lines[i].split()
        dd[5] = atomtypes[i-1]
        newline = "%6s%3s%12.6f%12.6f%12.6f"%(dd[0], dd[1], float(dd[2]), float(dd[3]), float(dd[4]))
        newline += "   ".join(["%4s"%i for i in dd[5:]])
        f.write(newline + "\n")
    return
  #==========================================================================
  #!<==

  #!==>
  #==========================================================================
  def ToCOM(fi,fo):
    if ti == "XYZ":
      cmdstr = "babel -ixyz %s -ogau %s"%(fi, fo)
    elif ti == "TXYZ":
      cmdstr = "babel -itxyz %s -ogau %s"%(fi, fo)
    elif ti == "COM":
      cmdstr = "babel -icom %s -ogau %s"%(fi, fo)
    elif ti == "G09":
      cmdstr = "babel -ig09 %s -ogau %s"%(fi, fo)
    elif ti == "QCOUT":
      cmdstr = "babel -iqcout %s -ogau %s"%(fi, fo)
    elif ti == "MOL":
      cmdstr = "babel -imol %s -ogau %s"%(fi, fo)
    elif ti == "MOL2":
      cmdstr = "babel -imol2 %s -ogau %s"%(fi, fo)
    elif ti == "SDF":
      cmdstr = "babel -isdf %s -ogau %s"%(fi, fo)
    else:
      cmdstr = ("echo 'File format %s not supported!'"%ti)
    subprocess.run(cmdstr,shell=True)

    fname, _ = os.path.splitext(fo)
    chk   = "%chk=" + fname + ".chk\n"
    nproc = "%Nproc="+np + "\n" 
    mem   = "%Mem="+me +"\n"
    
    if (jt.upper() == "OPT"):
      extra = "IOP(5/13=1)\n"
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
    else:
      key = " ".join(["#P", qm+"/"+bf, jt, "MaxDisk=%s"%dk, extra])
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
  #==========================================================================
  #!<==


  #!==>
  #==========================================================================
  def ToQCHEM(fi,fo):
    if ti == "XYZ":
      cmdstr = "babel -ixyz %s -oqcin %s"%(fi, fo)
    elif ti == "TXYZ":
      cmdstr = "babel -itxyz %s -oqcin %s"%(fi, fo)
    elif ti == "COM":
      cmdstr = "babel -icom %s -oqcin %s"%(fi, fo)
    elif ti == "G09":
      cmdstr = "babel -ig09 %s -oqcin %s"%(fi, fo)
    elif ti == "QCOUT":
      cmdstr = "babel -iqcout %s -oqcin %s"%(fi, fo)
    elif ti == "MOL":
      cmdstr = "babel -imol %s -oqcin %s"%(fi, fo)
    elif ti == "MOL2":
      cmdstr = "babel -imol2 %s -oqcin %s"%(fi, fo)
    elif ti == "SDF":
      cmdstr = "babel -isdf %s -oqcin %s"%(fi, fo)
    else:
      cmdstr = ("echo 'File format %s not supported!'"%ti)
    subprocess.run(cmdstr,shell=True)

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
  #==========================================================================
  #!<==

  #!==>
  #==========================================================================
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
        fout.write("set {\nscf_type DF\n")
        if qm == "MP2":
          fout.write("mp2_type DF\ne_convergence 7\nreference rhf\n}\n\n")
          if jt.upper() == "CBS" and bf.upper()=="AUG-CC-PVTZ":
            if not bsse:
              fout.write("energy('mp2/aug-cc-pv[tq]z')\n")
            else:
              fout.write("energy('mp2/aug-cc-pv[tq]z', bsse_type='%s')\n"%bsse)
          if jt.upper() == "CBS" and bf.upper()=="CC-PVTZ":
            if not bsse:
              fout.write("energy('mp2/cc-pv[tq]z')\n")
            else:
              fout.write("energy('mp2/cc-pv[tq]z', bsse_type='%s')\n"%bsse)
          if jt.upper() == "SP":
            if not bsse:
              fout.write("energy('mp2/%s')\n"%bf)
            else:
              fout.write("energy('mp2/%s', bsse_type='%s')\n"%(bf,bsse))
        if qm == "CCSD(T)":
          fout.write("mp2_type DF\ne_convergence 7\nreference rhf\n}\n\n")
          if jt.upper() == "CBS":
            if not bsse:
              fout.write("energy(cbs, corl_wfn='mp2', corl_basis='aug-cc-pv[tq]z', delta_wfn='ccsd(t)', delta_basis='aug-cc-pv[dt]z')\n")
            else:
              fout.write("energy(cbs, corl_wfn='mp2', corl_basis='aug-cc-pv[tq]z', delta_wfn='ccsd(t)', delta_basis='aug-cc-pv[dt]z', bsse_type='%s')\n"%bsse)
          if jt.upper() == "SP":
            if not bsse:
              fout.write("energy('ccsd(t)/%s')\n"%bf)
            else:
              fout.write("energy('ccsd(t)/%s', bsse_type='%s')\n"%(bf, bsse))
        if jt.upper() == "SAPT":
          fout.write("basis %s\n"%bf)
          fout.write("freeze_core True\n")
          fout.write("guess SAD\n}\n")
          fout.write("energy('sapt2+')\n")
        if jt.upper() == "DIPOLE":
          fout.write('set PROPERTIES_ORIGIN ["COM"]\n')
          fout.write("properties('PBE0/%s', properties=['dipole'], title='Acetate')\n"%bf)
      return

    rmstr = "rm -rf tmp.xyz"
    subprocess.run(rmstr, shell=True)
    if ti == "XYZ":
      cmdstr = "cp %s tmp.xyz"%fi
    elif ti == "TXYZ":
      cmdstr = "babel -itxyz %s -oxyz %s"%(fi, "tmp.xyz")
    elif ti == "COM":
      cmdstr = "babel -icom %s -oxyz %s"%(fi, "tmp.xyz")
    elif ti == "G09":
      cmdstr = "babel -ig09 %s -oxyz %s"%(fi, "tmp.xyz")
    elif ti == "QCOUT":
      cmdstr = "babel -iqcout %s -oxyz %s"%(fi, "tmp.xyz")
    elif ti == "MOL":
      cmdstr = "babel -imol %s -oxyz %s"%(fi, "tmp.xyz")
    elif ti == "MOL2":
      cmdstr = "babel -imol2 %s -oxyz %s"%(fi, "tmp.xyz")
    elif ti == "SDF":
      cmdstr = "babel -isdf %s -oxyz %s"%(fi, "tmp.xyz")
    else:
      cmdstr = ("echo 'File format %s not supported!'"%ti)
    subprocess.run(cmdstr,shell=True)

    if os.path.isfile("tmp.xyz"):
      XYZ2PSI4("tmp.xyz", fo)
    return
  #==========================================================================
  #!<==
  
  #===>>> 
  fi = args["input"]
  fo = args["output"]
  ti = args["inType"].upper()
  to = args["outType"].upper()
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
    print(Fore.RED + "File format '%s' not supported!"%to)
  return

if __name__ == "__main__":
  main()
