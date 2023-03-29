"""Using procedural generation with procXD 
   to create a visualization of a tree and a cardioid curve.
"""
import random
import numpy as np
from procXD import SketchBuilder, random_hex_color


def draw_tree(sk_builder, start=(0, 0), end=(0, -65), branch_width=8,
              angle=30, depth=0, max_depth=10, leaf_size=10):
    """Draw a tree recursively.

    Args:
        sk_builder (procXD.SketchBuilder): sketch builder object.
        start (list, optional): Defaults to [0, 0].
        end (list, optional): Defaults to [0, -65].
        branch_width (int, optional): Defaults to 8.
        angle (int, optional): Defaults to 30.
        depth (int, optional): Defaults to 0.
        max_depth (int, optional): Defaults to 10.
        leaf_size (int, optional): Defaults to 10.
    """
    p_termination = depth/float(max_depth)
    if random.uniform(0, 1) < p_termination:
        # if depth == max_depth:
        color = random_hex_color()
        cur_leaf_size = leaf_size * \
            np.sqrt(max_depth/depth) * random.uniform(0.9, 1.1)
        points = [[0, 0], [end[0] - start[0], end[1] - start[1]]]
        sk_builder.add_element(element_type="Line", x=start[0], y=start[1],
                                   points=points, strokeWidth=branch_width)
        sk_builder.add_element(element_type="Ellipse", x=end[0]-cur_leaf_size/2,
                                   y=end[1] - cur_leaf_size/2,
                                   width=cur_leaf_size, height=cur_leaf_size,
                                   backgroundColor=color)
    else:
        # draw_branch(sketch, start, end, branch_width, color)
        points = [[0, 0], [end[0] - start[0], end[1] - start[1]]]
        sk_builder.add_element(element_type="Line", x=start[0], y=start[1],
                                   points=points, strokeWidth=branch_width)

        # Draw a line from start to finish:
        branch_vec = np.array([end[0] - start[0], end[1] - start[1]])

        theta_rad = np.radians(-angle)
        R = np.array([[np.cos(theta_rad), -np.sin(theta_rad)],
                      [np.sin(theta_rad), np.cos(theta_rad)]])
        rot_left = (R).dot(branch_vec) * 0.75
        theta_rad = np.radians(angle)
        R = np.array([[np.cos(theta_rad), -np.sin(theta_rad)],
                      [np.sin(theta_rad), np.cos(theta_rad)]])
        rot_right = (R).dot(branch_vec) * 0.75

        left_end = [end[0] + rot_left[0], end[1] + rot_left[1]]
        right_end = [end[0] + rot_right[0], end[1] + rot_right[1]]

        draw_tree(sk_builder, end, left_end, max(
            branch_width - 2, 1), angle, depth+1, max_depth, leaf_size)
        draw_tree(sk_builder, end, right_end, max(
            branch_width - 2, 1), angle, depth+1, max_depth, leaf_size)


def graph_cardiod(sk_builder, start_shift=(0, 0),  n_curves=10):
    """Draw a cardioid curve.

    Args:
        sk_builder (procXD.SketchBuilder).
        start_shift (tuple, optional): Defaults to (0, 0).
        n_curves (int, optional): Defaults to 10.
    """

    radii = np.linspace(0.5, 1.5, n_curves)
    # Loop through each radius
    scale = 100
    for r in radii:
        # Calculate x and y coordinates
        theta = np.linspace(0, 1.9*np.pi, int(r * 20))
        x = r*(1 - np.cos(theta)) * scale
        y = r*np.sin(theta) * scale
        color = random_hex_color()
        xy_points = [[int(x[i]), int(y[i])] for i in range(len(x))]
        sk_builder.add_element(element_type="Line", x=start_shift[0],
                                   y=start_shift[1], points=xy_points,
                                   strokeWidth=2, strokeColor=color)
        xy_points = [[int(-x[i]), int(y[i])] for i in range(len(x))]
        sk_builder.add_element(element_type="Line", x=start_shift[0],
                                   y=start_shift[1], points=xy_points,
                                   strokeWidth=2, strokeColor=color)
        xy_points = [[int(y[i]), int(x[i])] for i in range(len(x))]
        sk_builder.add_element(element_type="Line", x=start_shift[0],
                                   y=start_shift[1], points=xy_points,
                                   strokeWidth=2, strokeColor=color)
        xy_points = [[int(y[i]), int(-x[i])] for i in range(len(x))]
        sk_builder.add_element(element_type="Line", x=start_shift[0],
                                   y=start_shift[1], points=xy_points,
                                   strokeWidth=2, strokeColor=color)

    sk_builder.add_element(element_type="Line", x=-40 + start_shift[0],
                               y=start_shift[1], points=[[0, 0], [400, 0]], strokeWidth=4)
    sk_builder.add_element(element_type="Line", x=start_shift[0], y=40 + start_shift[1],
                               points=[[0, 0], [0, -400]], strokeWidth=4)


if __name__ == "__main__":
    # EXAMPLE 1: Create a Tree
    sketch_builder = SketchBuilder()
    draw_tree(sketch_builder)
    draw_tree(sketch_builder, start=[-300, 0], end=[-300, -65],)
    draw_tree(sketch_builder, start=[-300, 300], end=[-300, 235],)
    draw_tree(sketch_builder, start=[0, 300], end=[0, 235],)
    SAVE_FILE = "examples/xd_figures/tree.excalidraw"
    sketch_builder.export_to_file(save_path=SAVE_FILE)
    sketch_builder.refresh()

    # EXAMPLE 2: Create a plot of a function
    sketch_builder = SketchBuilder()
    graph_cardiod(sketch_builder, start_shift=[400, 0])
    SAVE_FILE = "examples/xd_figures/cardiod.excalidraw"
    sketch_builder.export_to_file(save_path=SAVE_FILE)
