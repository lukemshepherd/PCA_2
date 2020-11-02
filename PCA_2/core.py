# AUTOGENERATED! DO NOT EDIT! File to edit: 01_maths.ipynb (unless otherwise specified).

__all__ = ['bone', 'mag', 'angle']

# Cell
class bone:

    filter_level = 0.001
    default_color = (0.7, 1, 1)

    def __init__(self, data, dtype):
        """
        Performs calculations on the voxel array objects
        array (np.array): binary voxel object)
        filter_level (int/float): sets the threshold level for
        what is considered a voxel. Everything below filter level is
        rounded to 0, everything above rounded to 1 (ie voxel)
        """

        self.dtype = dtype
        self.data = data

        self.get_xyz()



    def get_xyz(self):
        """Convert 3D voxel array or STL to xyz coordinates.

        filter_level (int/float): (inherited from `bone` class) sets the threshold level for
        what is considered a voxel. Everything below filter level is
        rounded to 0, everything above rounded to 1 (ie voxel)

        returns:
            np.array( [n x 3] )"""


        if self.dtype == 'voxel':

            # Everything above filter level is converted to 1
            filtered_array = np.where(self.data < self.filter_level, 0, 1)

            # records coordiates where there is a 1
            x, y, z = np.where(filtered_array == 1)

            self.xyz = np.array([x, y, z]).T


        elif self.dtype == 'stl':
            self.xyz = np.concatenate((self.data.v0,
                                         self.data.v1,
                                         self.data.v2), axis=0)


    def get_pca(self):
        """PCA on the xyz points array

            xyz(np.array): n x 3 array of xyz coordinates

            returns:    self.pc1
                        self.pc2
                        self.pc3"""

        pca = PCA(svd_solver='full')
        pca.fit(self.xyz)

        self.pca_list = pca.components_
        self.pc1 = pca.components_[0]
        self.pc2 = pca.components_[1]
        self.pc3 = pca.components_[2]



    @property
    def mean(self):
        """The mean of the xyz atriube
            returns:
            tupple (mean_of_x, mean_of_y ,mean_of_z)"""

        return (np.mean(self.xyz[:, 0]), np.mean(self.xyz[:, 1]), np.mean(self.xyz[:, 2]))


    def center_to_origin(self):
        """ sets the mean of the bone to 0,0,0"""

        # set transformation (tfm) value
        self.tfm = self.mean

        self.xyz = self.xyz - self.mean

    def reset_position(self):
        """ resets the position of the bone to its orginal one"""
        self.xyz = self.xyz + self.tfm


    def plot(self, user_color=None, mesh=False, PCA_inv=False, PCA=True):
        """ Plot voxels with optional PCA, and colours

            user_color (tupple): RGB color of the bone where 1 is maxium
                                    eg: red = (1,0,0)

            PCA (boolean): plots the PCAs of the voxel

            PCA_inv (boolean): plots the inverse of each PCA so the axes go in both directions
        """

        if hasattr(self, 'pc1') is False:
            self.get_pca()


        if user_color is None:
            user_color = self.default_color



        if mesh is False:
            #plots points
            mlab.points3d(self.xyz[:, 0],
                          self.xyz[:, 1],
                          self.xyz[:, 2],
                          mode = "cube",
                          color= user_color,
                          scale_factor = 1)

        else:
             mlab.mesh(self.data.x, self.data.y, self.data.z)


        def quiver_pca(n,i):
            mlab.quiver3d(*self.mean, *(getattr(self,f'pc{n}')*i),
                                  line_width=6,
                                  scale_factor=100/n,
                                  color=c)

        for n in range(1,4):
            #sets color: red = pc1, blue = pc2, green = pc3
            c = [0,0,0]
            c[n-1] = 1
            c = tuple(c)

            # plots pca arrows
            if PCA is True:
                quiver_pca(n,1)

            #plots the pca *-1
            if PCA_inv is True:
                quiver_pca(n,-1)


    def scale(self, n, algo = 'constant'):
        """ up-scales the bone by n

            n: scale factor

            algo: method of upscaling array
            scipy.ndimagezoom(mode=...)"""

        self.data = zoom(self.data, (n, n, n), mode=algo)

        #update xyz
        self.get_xyz()


    def xyz_to_array(self,array_dim=(256,256,256)):
        """ Converts xyz coordinates to numpy voxel array"""

        #empty array
        vx_array = np.zeros(array_dim,dtype=bool)

        #for every xyz coord: if int(+- tolarance) write to array
        for i in self.xyz:
            if np.allclose(i, np.around(i), rtol= 0.5, equal_nan=True):
                vx_array[tuple(np.around(i).astype(int))] = True

        x = np.count_nonzero(vx_array)/self.xyz.shape[0]

        print(f'{x*100}% reconstructed')

        return vx_array


    @classmethod
    def from_matlab_path(cls, matlab_file):
        """Imports matlab file drectly

           path: path object/string

           retruns np.array (n x n x n )"""

        matlab_file = Path(matlab_file)

        matlab_object = scipy.io.loadmat(matlab_file)
        obj = matlab_object.keys()
        obj = list(obj)
        data = matlab_object[obj[-1]]

        return cls(data, dtype="voxel")

    @classmethod
    def from_stl_path(cls, stl_file):
        """Imports stl file drectly

       path: path object/string

       retruns np.array (n x n x n )"""

        stl_file = Path(stl_file)

        data = mesh.Mesh.from_file(stl_file)

        return cls(data, dtype="stl")

# Cell
def mag(v):
    """ Finds magnitude of vector

        v (np.array): vector"""
    return math.sqrt(np.dot(v, v))

# Cell
def angle(v1, v2):
    """ Finds angel between 2 vectors

    returns: ang , v1"""

    try:

        ang = math.atan2(np.linalg.norm(np.cross(v1,v2)),np.dot(v1,v2))

        if ang > math.pi/2:
            v1 = -v1
            ang = math.atan2(np.linalg.norm(np.cross(v1,v2)),np.dot(v1,v2))

            print(f'{ang} PC inverted')

        else:
            print(f'{ang} no invert')

    except:
        #vang = 0
        print(f'ERROR: vectors v1= {v1}, v2= {v2}')
        ang = 'ERROR'

    return ang, v1
