

#===================================
#        Chengwen Liu              #
#      liuchw2010@gmail.com        #
#   University of Texas at Austin  #
#===================================


import argparse
import numpy as np
import os
from scipy.optimize import minimize
from scipy.optimize import least_squares

''' align the second molecule to the first one using selected atoms from both '''

def readXYZ(xyz):
  atoms  = np.loadtxt(xyz, usecols=(0,), dtype='str', unpack=True, skiprows=2)
  coords = np.loadtxt(xyz, usecols=(1,2,3), dtype='float', unpack=False, skiprows=2)
  return atoms,coords

def readPDB(pdb):
  atoms  = np.loadtxt(pdb, usecols=(2,), dtype='str', unpack=True, skiprows=1)
  coords = np.loadtxt(pdb, usecols=(6,7,8), dtype='float', unpack=False, skiprows=1)
  return atoms,coords

def distance(coord1, coord2):
  coord1 = np.array(coord1)
  coord2 = np.array(coord2)
  dist = np.sqrt(np.square(coord1-coord2).sum()) 
  return dist

def geomCenter(coords):
  coords = np.array(coords)
  geocent = [coords[:,0].mean(),
             coords[:,1].mean(),
             coords[:,2].mean()]
  return geocent

def sliceCoord(coords, indices):
  coords_p = []
  for idx in indices:
    coords_p.append(coords[idx])
  coords_p = np.array(coords_p)
  return coords_p

def rotMatrix(axis, theta):
  axis = np.asarray(axis)
  axis = axis/np.sqrt(np.dot(axis, axis))
  a = np.cos(theta/2.0)
  b, c, d = -axis*np.sin(theta/2.0)
  aa, bb, cc, dd = a*a, b*b, c*c, d*d
  bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
  rotmat = np.array([[aa+bb-cc-dd, 2.0*(bc+ad), 2.0*(bd-ac)],
                     [2.0*(bc-ad), aa+cc-bb-dd, 2.0*(cd+ab)],
                     [2.0*(bd+ac), 2.0*(cd-ab), aa+dd-bb-cc]])
  return rotmat

def optimize(atoms1, atoms2, coords1, coords2, indices1, indices2, dimer):
  '''cost function of distance summation'''
  def costfunc(params):
    transvec = np.array(params[:3])
    axis = np.array(params[3:6])
    theta = params[6] 
    rotmat = rotMatrix(axis, theta)
    coords2_t = []
    geocenter2 = geomCenter(coords2)
    for n in range(len(coords2)):
      coord2_t = coords2[n] + transvec 
      coords2_t.append(coord2_t)
    coords2_t = np.array(coords2_t)
    coords2_r = []
    for n in range(len(coords2_t)):
      coord2_r = np.dot(rotmat, coords2_t[n]) 
      coords2_r.append(coord2_r)
    coords2_r = np.array(coords2_r)
    coords1_p = sliceCoord(coords1, indices1)
    coords2_r_p = sliceCoord(coords2_r, indices2)
    func = []
    for i,j in zip(coords1_p, coords2_r_p):
      for k in range(3):
        func.append(abs(i[k] - j[k]))
    return np.array(func)

  ''' do the optimization to find the best parameters'''
  x0 = np.ones(7) 
  ret = least_squares(costfunc, x0, verbose=2, diff_step=1e-10, ftol=1e-10, gtol=1e-10, xtol=1e-10)
  np.savetxt("p0.txt", ret.x,fmt='%15.10f')
   
  # optimized parameters 
  transvec = np.array(ret.x[:3])
  axis = np.array(ret.x[3:6])
  theta = ret.x[6] 
 
  # translation
  coords2_t = []
  for n in range(len(coords2)):
    coord2_t = coords2[n] + transvec
    coords2_t.append(coord2_t)
  coords2_t = np.array(coords2_t)
  rotmat = rotMatrix(axis, theta)

  # rotation
  coords2_r = []
  for n in range(len(coords2_t)):
    coord2_r = np.dot(rotmat, coords2_t[n]) 
    coords2_r.append(coord2_r)
  coords2_r = np.array(coords2_r)

  # write the result
  with open(dimer, "w") as f:
    #f.write("%s\n" %(len(atoms1) + len(atoms2)))
    #f.write("%s\n" %(len(atoms1) + len(atoms2)))
    f.write("Generated by lalignment.py\n")
    #for i in range(len(atoms1)):
    #  f.write("%3s %12.5f%12.5f%12.5f\n"%(atoms1[i], coords1[i][0], coords1[i][1], coords1[i][2]))
    for i in range(len(atoms2)):
      f.write("%3s %8.3f%8.3f%8.3f\n"%(len(atoms1) + i + 1, coords2_r[i][0], coords2_r[i][1], coords2_r[i][2]))
  return 

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('-frag1', dest = 'fragment1', required=True, help="The first fragment in xyz/pdb format")  
  parser.add_argument('-frag2', dest = 'fragment2', required=True, help="The second fragment in xyz/pdb format")
  parser.add_argument('-indx1', dest = 'atomindices1', required=True, help="The atom index of the first fragment", type=int, nargs='+',)  
  parser.add_argument('-indx2', dest = 'atomindices2', required=True, help="The atom index of the second fragment", type=int, nargs='+',)
  parser.add_argument('-dimer', dest = 'dimername', required=True, help="The filename of to-be-generated molecule")  
  args = vars(parser.parse_args())
  frag1 = args["fragment1"]
  frag2 = args["fragment2"]
  indices1 = []
  indices2 = []
  indx1 = args["atomindices1"]
  indx2 = args["atomindices2"]
  for idx1, idx2 in zip(indx1, indx2):
    indices1.append(idx1 - 1)
    indices2.append(idx2 - 1)
  dimer = args["dimername"]
  if frag1.endswith(".xyz"):
    atoms1, coords1 = readXYZ(frag1)
    atoms2, coords2 = readXYZ(frag2)
  if frag1.endswith(".pdb"):
    atoms1, coords1 = readPDB(frag1)
    atoms2, coords2 = readPDB(frag2)
  optimize(atoms1, atoms2, coords1, coords2, indices1, indices2, dimer)
  return

if __name__ == "__main__":
  main()
