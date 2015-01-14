from __future__ import print_function, division, absolute_import

from timeit import default_timer as timer
import numpy as np

from numba import unittest_support as unittest
from numba import hsa


class TestMatMul(unittest.TestCase):
    def test_matmul_naive(self):
        @hsa.jit
        def matmul(A, B, C):
            i = hsa.get_global_id(0)
            j = hsa.get_global_id(1)

            if i >= C.shape[0] or j >= C.shape[1]:
                return

            tmp = 0

            for k in range(A.shape[1]):
                tmp += A[i, k] * B[k, j]

            C[i, j] = tmp

        N = 256
        A = np.random.random((N, N)).astype(np.float32)
        B = np.random.random((N, N)).astype(np.float32)
        C = np.zeros_like(A)

        with hsa.register(A, B, C):
            ts = timer()
            matmul[(N // 16, N // 16), (16, 16)](A, B, C)
            te = timer()
            print("GPU time:", te - ts)

        ts = timer()
        ans = np.dot(A, B)
        te = timer()
        print("CPU time:", te - ts)
        np.testing.assert_allclose(ans, C, rtol=1e-5)


if __name__ == '__main__':
    unittest.main()
