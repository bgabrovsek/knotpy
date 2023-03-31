import numpy as np
import scipy as sc
from scipy.spatial import ConvexHull
import string
import multiprocessing as mp
# from subprocess import Popen, DEVNULL,STDOUT


global THE_ZERO
THE_ZERO = 1e-10


class Protein:


    def __init__(self,name):
        file=open(name,"r")
        self.protdata=file.readlines()
        file.close()

    def backbone_from_file(self):
        backbone=[]
        for i in range(len(self.protdata)):
            line = str.split(self.protdata[i])
            x = float(line[0])
            y = float(line[1])
            z = float(line[2])
            backbone.append([x,y,z])

        return np.array(backbone)


    def get_backbone_coordinates(self):
        backbone=[]
        for i in range(len(self.protdata)):
                line=str.split(self.protdata[i])
                # print (line[0])
                if(line[0]=="ATOM" and line[2]=="CA" and self.protdata[i][21]=="A"):

                    x=float(self.protdata[i][30:38])
                    y=float(self.protdata[i][38:46])
                    z=float(self.protdata[i][46:54])
                    resid=int(self.protdata[i][22:26])
                    backbone.append([x,y,z,resid])

                if line[0]=="ENDMDL":
                    break
        # print (backbone)
        return np.array(backbone)

    def find_ions(self,backbone):
        ion_bonds={}
        ions=["FE","MG","ZN","CA","CU","NI","MN","K"]
        for i in range(len(self.protdata)-2):
                line=str.split(self.protdata[i])
                if "LINK" == line[0] and line[1] in ions:
                    if line[1] in ion_bonds:
                        ion_bonds[line[1]].append([int(line[4]),int(line[8])])
                    else:
                        ion_bonds[line[1]] = [[int(line[4]),int(line[8])]]
                if line[0]=="ENDMDL":
                    break
        if ion_bonds:
            for ion in ion_bonds:
                for i in range(len(self.protdata)-2):
                    line=str.split(self.protdata[i])
                    if "HETATM" == line[0] and line[2] == ion:
                        x=float(self.protdata[i][30:38])
                        y=float(self.protdata[i][38:46])
                        z=float(self.protdata[i][46:54])
                        resid=int(self.protdata[i][22:26])
                        backbone=np.append(backbone,np.reshape([x,y,z,resid],(1,4)),axis=0)
                    if line[0] == "ENDMDL":
                        break

            return (ion_bonds,backbone)
        else:
            return False

    def find_ssbonds(self):

        cys_bonds=[]
        for i in range(len(self.protdata)-2):
                # print ("i",i)
                line=str.split(self.protdata[i])
                if "SSBOND" == line[0] and "CYS" == line[2] and "CYS" == line[5] and "A" == line[3]:
                    if line[3] == line[6]:
                        # print ("i",i,"line[3]",line[4],"line[6]",line[7])
                        cys_bonds = cys_bonds+[int(line[4]),int(line[7])]
                if line[0]=="ENDMDL":
                    break
        if cys_bonds:
            return cys_bonds
        else:
            return False

    def find_centroid(self,backbone):
        return np.average(backbone[:,:3],axis=0)

    
    def find_bounding_box(self,backbone,x,y,z):
        dist=np.sqrt(x*x+y*y+z*z)
        dx = x/dist
        dy = y/dist
        dz = z/dist
        minx=min(backbone[:,0]);miny=min(backbone[:,1]);minz=min(backbone[:,2])
        maxx=max(backbone[:,0]);maxy=max(backbone[:,1]);maxz=max(backbone[:,2])

        if minx > dx :
            minx = dx
        if maxx < dx:
            maxx = dx
        if miny > dy:
            miny = dy
        if maxy < dy:
            maxy = dy
        if minz > dz:
            minz = dz
        if maxz < dz:
            maxz = dz

        distance = maxx-minx+maxy-miny+maxz-minz
        closure_points=[]
        closure_points.append([backbone[0,-1]+distance*(dx+np.random.randn()*1e-6), backbone[1,-1]+distance*(dy+np.random.randn()*1e-6),backbone[2,-1]+distance*(dz+np.random.randn()*1e-6),-100])
        closure_points.append([backbone[0,0]+distance*(dx+np.random.randn()*1e-6), backbone[1,0]+distance*(dy+np.random.randn()*1e-6),backbone[2,0]+distance*(dz+np.random.randn()*1e-6),-100])
        
        # print (np.array(closure_points))
        return closure_points



    def add_closure(self,backbone,samples=100,randomize=True):
        rnd = 1.
        if randomize:
            rnd = np.random.random() * samples

        closures = [[] for i in range(samples)]
        offset = 2./samples
        increment = np.pi * (3. - np.sqrt(5.));

        for i in range(samples):
            y = ((i * offset) - 1) + (offset / 2);
            r = np.sqrt(1 - np.power(y,2))

            phi = ((i + rnd) % samples) * increment

            x = np.cos(phi) * r
            z = np.sin(phi) * r

            new_points = self.find_bounding_box(backbone,x,y,z)

            closures[i] = np.vstack((backbone,np.array(new_points)))


        return closures

    def intersection_routine(self,backbone,i1,i2,i3,j1,j2,nbpoints,tolerance):

        Q1,Q2,Q3 = [backbone[i1%nbpoints,:3],backbone[i2%nbpoints,:3],backbone[i3%nbpoints,:3]]
        V1 = Q2 - Q1
        V2 = Q3 - Q1

        s = backbone[j2%nbpoints,:3] - backbone[j1%nbpoints,:3]
        n = np.cross(V1,V2)
        norme_n = np.linalg.norm(n)
        if norme_n <THE_ZERO:
            return False

        if np.linalg.norm(s) < THE_ZERO:

            return False

        ns = np.dot(n,s)


        if abs(ns) < THE_ZERO:
            return False
        d = Q1 - backbone[j1,:3]

        t = np.dot(n,d)/ns

        if (t < (-tolerance)) or (t > (1+tolerance)):
            return False

        r = t * s + backbone[j1,:3] - Q1
        u =(np.dot(n,np.cross(r,V2)))/(norme_n*norme_n)
        v = -(np.dot(n,np.cross(r,V1)))/(norme_n*norme_n)


        if (u >= -tolerance) and (v >= -tolerance) and (u+v <= 1 + tolerance):
            # print ("Pierce")
            return True
        return False
    
    def simplify(self,backbone,tolerance = 1e-8,bonds = None):
        PointRemoved = np.zeros(np.size(backbone,0))
        ToBeRemoved = True
        nbpointremoved = 1
        # keep =0

        while nbpointremoved > 0:
            # print (nbpointremoved)

            # print ("--------- LOOP ----------")
            nbpoints = np.size(backbone,0)
            # print ("nbpoints",nbpoints)
            # print ("starting backbone",backbone)
            nbpointremoved=0
            i=0
            while (i < nbpoints) and (nbpoints - nbpointremoved > 3):
                # print (i)
                # if (nbpoints - nbpointremoved < 3):
                    # break
                # else:
                i1 =i
                # print ("i1",i1)
                while PointRemoved[i1%nbpoints] == 1:
                    i1 += 1
                i2 = i1 + 1
                i3 = i2 + 1
                ToBeRemoved = True
                while (ToBeRemoved==True) and (i3 - i1 < nbpoints) and (nbpoints - nbpointremoved > 3):
                    ToBeRemoved = True
                    while PointRemoved[i2%nbpoints] == 1:
                        i2 += 1
                    i3 = i2 + 1
                    while PointRemoved[i3%nbpoints] == 1:
                        i3 += 1
                    dist13_squared = np.sum((backbone[i1%nbpoints,:3] - backbone[i3%nbpoints,:3])*(backbone[i1%nbpoints,:3] - backbone[i3%nbpoints,:3]))
                    if dist13_squared < THE_ZERO * THE_ZERO:
                        print ("degenerate!")
                        ToBeRemoved = False

                    if bonds and (float(backbone[i2%nbpoints,3]) in bonds) and (float(backbone[i2%nbpoints,3]) != -100.0):
                            # print ("in")
                            ToBeRemoved = False
                    i = i1
                    j = 0
                    while (j < nbpoints) and (ToBeRemoved == True) and (nbpoints - nbpointremoved > 3):

                        j1 = j
                        while PointRemoved[j1%nbpoints] == 1:
                            j1 += 1
                        j2 = j1 + 1
                        while PointRemoved[j2%nbpoints] == 1:
                            j2 += 1
                        j = j1
                        if (j1%nbpoints!=i1%nbpoints) and (j1%nbpoints!=i2%nbpoints) and (j1%nbpoints!=i3%nbpoints) and (j2%nbpoints!=i1%nbpoints) and (j2%nbpoints!=i2%nbpoints) and (j2%nbpoints!=i3%nbpoints):
                            if self.intersection_routine(backbone,i1,i2,i3,j1,j2,nbpoints,tolerance):
                                ToBeRemoved = False
                                # print ("keep",keep)


                        j += 1
                        # print ("j",j)
                    if (ToBeRemoved==True) and (nbpoints - nbpointremoved > 3):
                        nbpointremoved += 1
                        # print ("i2 removed", i2%nbpoints)
                        # print ("PointRemoved before",PointRemoved[i2%nbpoints])
                        PointRemoved[i2%nbpoints] = 1
                        # print ("PointRemoved after",PointRemoved[i2%nbpoints])

                        i2 = i3
                i = i2 -1 

                i += 1
            # return PointRemoved
            # print (PointRemoved)
            position = 0

            for k in range(nbpoints):
                if PointRemoved[k] == 0:
                    backbone[position,:] = backbone[k,:]
                    position += 1
                else:
                    PointRemoved[k] = 0

            backbone = backbone[:position,:]

        all_chains.append(backbone)


if __name__ == "__main__":

    #print("Starting.")

    a="pdb/3bjx.pdb" ### 3bjx should form a 6_1 form. 1aoc has bonds and 1a8e has ions. both are trivial.
    b=Protein(a)

    backbone = b.get_backbone_coordinates() ### np.array with 4 columns (x, y, z, resid). Closure points have resid -100.0


    ions = b.find_ions(backbone)

    bonds = b.find_ssbonds()



    closed=(b.add_closure(backbone,samples=2)) ### samples is the number of closures.



### Multiprocessing ###
    manager=mp.Manager()
    all_chains = manager.list()
    pool = mp.Pool(mp.cpu_count())
    for i in range(len(closed)):
        pool.apply_async(b.simplify,args=(closed[i],1e-8,bonds))
    pool.close()
    pool.join()

    print (all_chains) ### all_chains is a list of np.arrays with all the closures.


