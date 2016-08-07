from math import ceil, sqrt
import numpy as np
cimport numpy as np
cimport cython

DTYPE_float64 = np.float64
ctypedef np.float64_t DTYPE_float64_t

DTYPE_int32 = np.int32
ctypedef np.int32_t DTYPE_int32_t

def get_positions_vec(tuple T, double[:] x not None, double[:] y not None):
    """ Return the row and column indices according to grid transform T for
    points in vectors x and y. """
    cdef int i = 0
    cdef int n = len(x)
    cdef double x0, y0, dx, dy, sx, sy
    cdef double i_, j_
    cdef np.ndarray[np.float64_t] I = np.empty(n)
    cdef np.ndarray[np.float64_t] J = np.empty(n)
    x0 = T[0]
    y0 = T[1]
    dx = T[2]
    dy = T[3]
    sx = T[4]
    sy = T[5]
    while i != n:
        j_ = (dy*x[i] - dy*x0 + sx*y0 - sx*y[i]) / (dx*dy - sx*sy)
        i_ = (y[i] - y0 - j_*sy) / dy
        J[i] = j_ - 0.5
        I[i] = i_ - 0.5
        i += 1
    return I, J

def sample_bilinear_long(double[:] I not None, double[:] J not None,
                         np.int32_t[:,:] Z not None):
    cdef int cnt = 0
    cdef int L = len(I)
    cdef double i = 0.0, j = 0.0
    cdef double i0 = 0.0, i1 = 0.0, j0 = 0.0, j1 = 0.0
    cdef int m, n
    m = Z.shape[0]
    n = Z.shape[1]
    cdef np.ndarray[np.int32_t] out = np.empty(L, dtype=np.int32)

    for cnt in range(L):
        i = I[cnt]
        j = J[cnt]
        if (i % 1 != 0):
            i0 = i // 1.0
            i1 = i0 + 1
        elif (i != 0):
            i0 = i - 1.0
            i1 = i
        else:
            i0 = i
            i1 = i + 1.0

        if (j % 1 != 0):
            j0 = j // 1.0
            j1 = j0 + 1
        elif (j != 0):
            j0 = j - 1.0
            j1 = j
        else:
            j0 = j
            j1 = j + 1.0

        out[cnt] = int(float(Z[int(i0),int(j0)])*(i1-i)*(j1-j)
                     + float(Z[int(i1),int(j0)])*(i-i0)*(j1-j) \
                     + float(Z[int(i0),int(j1)])*(i1-i)*(j-j0) \
                     + float(Z[int(i1),int(j1)])*(i-i0)*(j-j0))
    return out

def sample_bilinear_double(double[:] I not None, double[:] J not None,
                           np.float64_t[:,:] Z not None):
    cdef int cnt = 0
    cdef int L = len(I)
    cdef double i = 0.0, j = 0.0
    cdef double i0 = 0.0, i1 = 0.0, j0 = 0.0, j1 = 0.0
    cdef int m, n
    m = Z.shape[0]
    n = Z.shape[1]
    cdef np.ndarray[np.float64_t] out = np.empty(L)

    for cnt in range(L):
        i = I[cnt]
        j = J[cnt]
        if (i % 1 != 0):
            i0 = i // 1.0
            i1 = i0 + 1
        elif (i != 0):
            i0 = i - 1.0
            i1 = i
        else:
            i0 = i
            i1 = i + 1.0

        if (j % 1 != 0):
            j0 = j // 1.0
            j1 = j0 + 1
        elif (j != 0):
            j0 = j - 1.0
            j1 = j
        else:
            j0 = j
            j1 = j + 1.0

        out[cnt] = Z[int(i0),int(j0)]*(i1-i)*(j1-j) + Z[int(i1),int(j0)]*(i-i0)*(j1-j) \
                 + Z[int(i0),int(j1)]*(i1-i)*(j-j0) + Z[int(i1),int(j1)]*(i-i0)*(j-j0)
    return out

@cython.wraparound(False)
def fillarray_double(double[:,:] array not None,
                     int[:] I not None,
                     int[:] J not None,
                     double[:] Z not None,
                     double nodata_value):
    """ fillarray_double places values from *Z* into 2d *array* at the indices
    *I*, *J*. *array* should be a zero array.

    Returns 0 on success and 1 on failure.
    """
    cdef int ny, nx
    cdef int i, j, idx
    cdef double z
    cdef np.ndarray[DTYPE_int32_t, ndim=2] counts

    if (len(I) != len(J)) or (len(I) != len(Z)):
        return 1

    ny = array.shape[0]
    nx = array.shape[1]
    counts = np.zeros([ny, nx], dtype=DTYPE_int32)

    for idx in range(len(I)):
        i = I[idx]
        j = J[idx]
        array[i,j] += Z[idx]
        counts[i,j] += 1

    for i in range(ny):
        for j in range(nx):
            if counts[i,j] != 0:
                array[i,j] = array[i,j] / counts[i,j]
            else:
                array[i,j] = nodata_value
    return 0

