import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

def _inverse_point_through_circle(center, radius, point):
    return center + (radius**2 / (center-point)**2) * (point - center)

def circle(center, radius, color='blue'):
    c = plt.Circle((center.real, center.imag), radius, color=color, fill=False)
    plt.gca().add_patch(c)

def pt(z, color="red"):
    plt.gca().add_patch(plt.Circle((z.real, z.imag), 0.05, color=color))

def plot_arc(center, radius, theta1, theta2, color='blue'):
    c = plt.Circle((center.real, center.imag), radius, color=color, fill=False, alpha=0.1)
    plt.gca().add_patch(c)

    if (theta2-theta1) % (2 * math.pi) > math.pi:
        theta1, theta2 = theta2, theta1

    circular_arc = patches.Arc((center.real, center.imag), 2*radius, 2*radius,
                               theta1=math.degrees(theta1), theta2=math.degrees(theta2),
                               edgecolor="cyan",
                               alpha=0.7
                               )
    plt.gca().add_patch(circular_arc)


if __name__ == '__main__':
    fig, ax = plt.subplots()
    ax.set_xlim([-6, 6])
    ax.set_ylim([-6, 6])
    ax.set_aspect('equal', adjustable='box')

    import cmath

    z = 1 + 0.5j
    r = 3.2

    v = -1+1j
    i0 = z + r * v / abs(v)
    v = +3-1.5j
    i1 = z + r * v / abs(v)

    p = 0.5 * (i0 + i1)  # midpoint of i0 and i1




    p_ = _inverse_point_through_circle(z, r, p)
    out_r = abs(p_ - i0)

    alpha_1 = cmath.phase(i0-p_)
    alpha_2 = cmath.phase(i1-p_)

    print(alpha_1, alpha_2
        )

    circle(z, r)
    pt(i0)
    pt(i1)
    pt(p)
    pt(p_, color="green")
    plot_arc(p_, out_r, alpha_1, alpha_2)
    #circle(p_, out_r)

    plt.show()