"""
Iterative point cloud
"""

import numpy as np
import matplotlib.pyplot as plt


def icp_complex(points_a, points_b, max_iterations=50, tolerance=1e-6):
    """
    Perform ICP (Iterative Closest Point) to align points_b to points_a using complex numbers.
    Parameters:
        points_a: list or array of complex (target)
        points_b: list or array of complex (source)
    Returns:
        aligned_b: transformed source points
        R: complex rotation
        t: complex translation
    """
    A = np.array(points_a, dtype=np.complex128)
    B = np.array(points_b, dtype=np.complex128)
    B_aligned = B.copy()

    for _ in range(max_iterations):
        # Find closest points in A for each point in B_aligned
        indices = np.array([np.argmin(np.abs(a - B_aligned)) for a in A])
        A_matched = A
        B_matched = B_aligned[indices]

        # Compute centroids
        centroid_A = np.mean(A_matched)
        centroid_B = np.mean(B_matched)

        # Center the point sets
        A_centered = A_matched - centroid_A
        B_centered = B_matched - centroid_B

        # Compute rotation using complex scalar
        H = np.sum(B_centered * np.conj(A_centered))
        R = H / np.abs(H)

        # Compute translation
        t = centroid_A - R * centroid_B

        # Apply transformation
        B_new = R * B_aligned + t

        # Check convergence
        mean_shift = np.mean(np.abs(B_new - B_aligned))
        B_aligned = B_new

        if mean_shift < tolerance:
            break

    return B_aligned, R, t

if __name__ == "__main__":
    # Sample input
    theta = np.pi / 4  # 45 degrees
    R_true = np.exp(1j * theta)
    t_true = 1 + 2j

    # Original points (target)
    points_a = np.array([1 + 1j, 2 + 1j, 2 + 2j, 1 + 2j])

    # Transformed points (source)
    points_b = R_true * points_a + t_true
    points_b_initial = points_b.copy()

    # Run ICP
    aligned_b, R_est, t_est = icp_complex(points_a, points_b)

    # Plotting
    plt.figure(figsize=(6, 6))
    plt.scatter(points_a.real, points_a.imag, c='green', label='Target A (Green)', s=100, alpha=0.5)
    plt.scatter(points_b_initial.real, points_b_initial.imag, c='orange', label='Source B (Initial)', s=100, alpha=0.5)
    plt.scatter(aligned_b.real, aligned_b.imag, c='blue', label='Source B (Aligned)', s=100, marker='x', alpha=0.5)

    # Draw movement vectors
    for i in range(len(points_a)):
        plt.plot([points_b_initial[i].real, aligned_b[i].real],
                 [points_b_initial[i].imag, aligned_b[i].imag], 'k--', linewidth=1)

    plt.legend()
    plt.axis('equal')
    plt.title("ICP Alignment of Complex 2D Points")
    plt.xlabel("Real")
    plt.ylabel("Imaginary")
    plt.grid(True)
    plt.show()