""" SketchBuilder class for creating Excalidraw JSON files."""
import json
import math
import random
import numpy as np
from . import primitives
from .color_utils import random_hex_color, sample_color, RANDOM_PALLETE


class SketchBuilder():
    """SketchBuilder class for creating Excalidraw files."""

    def __init__(self):
        self.refresh()

    def refresh(self):
        """Reload the builder.
        """
        self.data = {
            "type": "excalidraw",
            "version": 1,
            "source": "procXD",
            "elements": [],
            "appState": {
                "viewBackgroundColor": "#ffffff",
                "gridSize": None,
            }
        }
        self.draw_objs = []
        self.groups = []

    def add_element(self, *args, element_type, return_elem=False, **kwargs):
        """Add an excalidraw primitive to the sketch.
        Args:
            element_type (str)
        """
        element_class = getattr(primitives, element_type)
        element = element_class(*args, **kwargs)
        self.draw_objs.append(element)
        if return_elem:
            return element

    def export_to_file(self, save_path):
        """Export the sketch to a excalidraw file."""
        for element in self.draw_objs:
            json_obj = element.export()
            self.data['elements'].append(json_obj)

        if save_path[-5:] != ".excalidraw":
            save_path += ".excalidraw"

        with open(save_path, "w") as file_reader:
            json.dump(self.data, file_reader, indent=4)

    def create_bounding_element(self, element, element_type="Rectangle",
                                backgroundColor="#e64980", padding=10,
                                return_group=True, disolve_prior_group=True):
        """Create a bounding box around the given element/group.

        Args:
            element (primitives.ExcaliDrawPrimitive)
            element_type (str, optional): Defaults to "Rectangle".
            backgroundColor (str, optional): Defaults to "#e64980".
            padding (int, optional): Defaults to 10.
            return_group (bool, optional): Defaults to True.
            disolve_prior_group (bool, optional): Defaults to True.

        Returns:
            primitives.ExcaliDrawPrimitive: Can be the bounding element 
                or a group containing the bounding element and the original element.
        """
        # Create a bounding box around the element
        # add it before the earliest element from element(if group).
        element_bbox = element.bbox
        new_x = element_bbox[0] - padding
        new_y = element_bbox[1] - padding
        new_width = element_bbox[2] - element_bbox[0] + 2 * padding
        new_height = element_bbox[3] - element_bbox[1] + 2 * padding
        element_class = getattr(primitives, element_type)
        bounding_element = element_class(set_to_solid=True, x=new_x, y=new_y,
                                         width=new_width, height=new_height, backgroundColor=backgroundColor)
        if return_group:
            if isinstance(element, primitives.Group):
                elements = element.elements
            else:
                elements = [element]
            elements.insert(0, bounding_element)
            group = primitives.Group()
            for element in elements:
                group.add_element(element)

            group.x += padding
            group.y += padding
            if disolve_prior_group:
                for element in elements:
                    if isinstance(element, primitives.Group):
                        element.empty_subelements()
            return group
        else:
            return bounding_element

    def create_text_block(self, content, padding=10, set_to_code=True, return_group=True):
        """Create a sequence of Text primitives from the content list.

        Args:
            content (List(srt)):
            padding (int, optional): Defaults to 10.
            set_to_code (bool, optional): Defaults to True.
            return_group (bool, optional): Defaults to True.

        Returns:
            primitives.ExcaliDrawPrimitive: Returns a group containing the text elements
                or a list of text elements.
        """
        elements = []
        for _, line in enumerate(content):
            text_element = primitives.Text(set_to_code=set_to_code, text=line)
            elements.append(text_element)

        self.order_sequence(elements, "order_below", padding=padding)

        group = primitives.Group()
        for element in elements:
            group.add_element(element)

        if return_group:
            return group
        return elements

    def order_sequence(self, element_list, order_type, padding=10):
        """Changes the x, y coordinates of the elements in the list to order them.

        Args:
            element_list (List(primitives.ExcaliDrawPrimitives))
            order_type (str): "order_below" or "order_above" 
                or "order_left" or "order_right
            padding (int, optional): Defaults to 10.
        """
        order_func = getattr(self, order_type)
        for i in range(len(element_list)-1):
            order_func(element_list[i], element_list[i+1], padding=padding)

    def order_below(self, element1, element2, padding=10):
        """Order element2 below element1."""
        element1_bbox = element1.bbox
        element2.y = element1_bbox[3] + padding

    def order_above(self, element1, element2, padding=10):
        """Order element2 above element1."""
        element1_bbox = element1.bbox
        element2.y = element1_bbox[1] - element2.height - padding

    def order_left(self, element1, element2, padding=10):
        """Order element2 to the left of element1."""
        element1_bbox = element1.bbox
        element2.x = element1_bbox[0] - element2.width - padding

    def order_right(self, element1, element2, padding=10):
        """Order element2 to the right of element1."""
        element1_bbox = element1.bbox
        element2.x = element1_bbox[2] + padding

    def horizontal_align(self, element_list, align_type="left"):
        """Align the elements horizontally.

        Args:
            element_list (List(primitives.ExcaliDrawPrimitives))
            align_type (str, optional): Defaults to "left".
        """
        # Align elements horizontally
        # Get the x positions of the elements
        # set them all to the same value (equal to average?)
        if align_type == "left":
            all_x = [element.x for element in element_list]
        elif align_type == "right":
            all_x = [element.x + element.width for element in element_list]

        mean_x = int(np.mean(all_x))
        for element in element_list:
            element.x = mean_x

    def vertical_align(self, element_list, align_type="top"):
        """Align the elements vertically.

        Args:
            element_list (List(primitives.ExcaliDrawPrimitives))
            align_type (str, optional): Defaults to "left".
        """
        if align_type == "top":
            all_y = [element.y for element in element_list]
        elif align_type == "bottom":
            all_y = [element.y + element.height for element in element_list]
        mean_y = int(np.mean(all_y))
        for element in element_list:
            element.y = mean_y

    def create_binding_arrows(self, element_1, element_2, padding=10,
                              startArrowhead="arrow", endArrowhead="arrow"):
        """Create a binding arrow between two elements.

        Args:
            element_1 (primitives.ExcaliDrawPrimitives)
            element_2 (primitives.ExcaliDrawPrimitives)
            padding (int, optional) Defaults to 10.
            startArrowhead (str, optional): Defaults to "arrow".
            endArrowhead (str, optional): Defaults to "arrow".

        Returns:
            primitives.Arrow: Returns an arrow primitive.
        """
        assert isinstance(element_1, (primitives.Rectangle, primitives.Text))
        assert isinstance(element_2, (primitives.Rectangle, primitives.Text))

        center_1 = element_1.center
        center_2 = element_2.center
        dx = center_2[0] - center_1[0]
        dy = center_2[1] - center_1[1]
        theta = math.atan2(dy, dx)
        theta = (theta + math.pi) % (2*math.pi) - math.pi
        inverted_theta = (theta) % (2*math.pi) - math.pi
        point_1 = element_1.get_edge_midpoint(theta, padding=padding)
        point_2 = element_2.get_edge_midpoint(
            inverted_theta, padding=padding)
        points = [[0, 0], [point_2[0] - point_1[0], point_2[1] - point_1[1]]]

        line = primitives.Arrow(x=point_1[0], y=point_1[1], points=points)
        line.set_start_binding(element_1, padding=padding)
        line.set_end_binding(element_2, padding=padding)
        line.startArrowhead = startArrowhead
        line.endArrowhead = endArrowhead
        return line

    def render_networkx_graph(self, graph, content_key="label", scale_factor=500,
                              set_text_to_code=True, directed=True, padding=10):
        """Render a networkx graph.

        Args:
            graph (networkx.diGraph): Function expects the nodes to contain a "label" and "pos" key.
                You can generate "pos" using layout functions in networkx.
            content_key (str, optional): The key to add into each box. Defaults to "label".
            scale_factor (int, optional): Scaling factor applied to "pos". Defaults to 500.
            set_text_to_code (bool, optional):  Defaults to True.
            directed (bool, optional): Directed arrow or not. Defaults to True.
            padding (int, optional): Defaults to 10.
        """
        # First we need size of each node
        node_dict = {}
        # Nodes
        for node_name in graph.nodes():
            node = graph.nodes()[node_name]
            content = node[content_key]
            if not isinstance(content, list):
                content = [content]
            text_group = self.create_text_block(
                content, set_to_code=set_text_to_code, padding=padding)
            backgroundColor = random_hex_color()
            out_group = self.create_bounding_element(text_group, element_type="Ellipse",
                                                     padding=padding, return_group=True,
                                                     backgroundColor=backgroundColor,
                                                     disolve_prior_group=True)
            node_position = node["pos"] * scale_factor
            out_group.x = int(node_position[0])
            out_group.y = int(-node_position[1])
            node_dict[node_name] = out_group

        # Edges
        edges = []
        for edge in graph.edges():
            in_key = edge[0]
            out_key = edge[1]
            in_group = node_dict[in_key]
            out_group = node_dict[out_key]
            in_bbox = in_group.elements[0]
            out_bbox = out_group.elements[0]
            if directed:
                endArrowhead = "arrow"
            else:
                endArrowhead = None
            startArrowhead = None
            arrow = self.create_binding_arrows(in_bbox, out_bbox, startArrowhead=startArrowhead,
                                               endArrowhead=endArrowhead, padding=padding)
            edges.append(arrow)

        for edge in edges:
            self.draw_objs.append(edge)
        for _, group in node_dict.items():
            for element in group.elements:
                self.draw_objs.append(element)

    # Specifically for the configuration visualizer
    def render_stack_sketch(self, graph, stacking="horizontal", content_key="content",
                            padding=10, shift=None, return_node_dict=False):
        """Render a stack sketch. Used for the configuration visualizer."""
        roots = [node for node, degree in graph.in_degree() if degree == 0]
        root_node = graph.nodes()[roots[0]]
        if return_node_dict:
            node_dict = dict()
        else:
            node_dict = None
        master_group, node_dict = self._node_recursive_call(graph, root_node, stacking=stacking,
                                                           content_key=content_key, padding=padding,
                                                           return_node_dict=return_node_dict,
                                                           global_dict=node_dict)

        if shift:
            master_group.x = shift[0]
            master_group.y = shift[1]
        for element in master_group.elements:
            self.draw_objs.append(element)

        if return_node_dict:
            return node_dict

    def _node_recursive_call(self, graph, node, stacking="horizontal", set_text_to_code=True,
                            content_key="content", backgroundColor=None, padding=10, color_technique=0,
                            return_node_dict=False, global_dict=None):
        """Internal recursive function for sketch stack."""
        if backgroundColor is None:
            if color_technique == 0:
                backgroundColor = random_hex_color()
            else:
                backgroundColor = random.sample(RANDOM_PALLETE, 1)[0]
        if content_key in node.keys():
            # convert content into text block:
            if node[content_key]:
                text_group = self.create_text_block(
                    node[content_key], set_to_code=set_text_to_code, padding=padding)
            else:
                text_group = None
        else:
            text_group = None
        successors = list(graph.successors(node['label']))
        if successors:
            if color_technique == 1:
                colors = [x for x in RANDOM_PALLETE if x != backgroundColor]

            all_successor_groups = []
            for successor in successors:
                successor_node = graph.nodes()[successor]
                if color_technique == 0:
                    successor_color = sample_color(backgroundColor)
                else:
                    successor_color = random.sample(colors, 1)[0]
                cur_successor, global_dict = self._node_recursive_call(graph, successor_node,
                            stacking=stacking, backgroundColor=successor_color,
                            content_key=content_key, padding=padding,
                            return_node_dict=return_node_dict, global_dict=global_dict,)
                all_successor_groups.append(cur_successor)
            if stacking == "horizontal":
                self.order_sequence(all_successor_groups,
                                    "order_right", padding=padding)
            elif stacking == "vertical":
                self.order_sequence(all_successor_groups,
                                    "order_below", padding=padding)
            successor_group = primitives.Group()
            for element in all_successor_groups:
                successor_group.add_element(element)
            if text_group:
                node_level_order = [text_group, successor_group]
                # Having this fixed?
                self.order_sequence(
                    node_level_order, "order_below", padding=padding)
            main_group = primitives.Group()
            if text_group:
                main_group.add_element(text_group)
            main_group.add_element(successor_group)
        else:
            main_group = text_group
        # Creat a bounding box:
        out_group = self.create_bounding_element(main_group, padding=padding, return_group=True,
                                                 backgroundColor=backgroundColor, 
                                                 disolve_prior_group=True)
        if return_node_dict:
            global_dict[node['label']] = out_group
        return out_group, global_dict

    def render_comparitive_stack_sketch(self, config_dict, base_config_name, stacking="horizontal", content_key="content", padding=10):
        """Render comparison of multiple stack sketch.
        Arrows indicate node match.
        Used for the configuration visualizer.
        """
        # First, base config is rendered fully.
        base_graph = config_dict[base_config_name]
        base_node_dict = self.render_stack_sketch(
            base_graph, stacking=stacking, content_key=content_key, 
            padding=padding, return_node_dict=True)
        master_group = base_node_dict["cfg"]
        bbox, _ = self._decorate_config_box(
            master_group, label=base_config_name, padding=padding, stacking=stacking)
        base_node_dict["bbox"] = bbox
        # for the next one, we need to find the common nodes, and then render the rest.
        all_ids_added = []
        prev_config_dict = base_node_dict
        for key, graph in config_dict.items():
            match_arrows = []
            if key == base_config_name:
                continue
            roots = [node for node, degree in graph.in_degree() if degree == 0]
            root_node = graph.nodes()[roots[0]]
            node_dict = dict()
            master_group, node_dict = self._node_recursive_call(graph, root_node, stacking=stacking,
                                                               content_key=content_key, 
                                                               padding=padding,
                                                               return_node_dict=True,
                                                               global_dict=node_dict)
            if stacking == "horizontal":
                # next config should be vertically below:
                shift = (
                    0, prev_config_dict['bbox'].y + prev_config_dict['bbox'].height + 2 * padding)
            elif stacking == "vertical":
                shift = (
                    prev_config_dict['bbox'].x + prev_config_dict['bbox'].width + 2 * padding, 0)
            master_group.x = shift[0]
            master_group.y = shift[1]
            # for each node check if you should render key:
            for node_name in graph.nodes():
                node = graph.nodes()[node_name]
                if node_name in base_graph.nodes():
                    # at least name matches check content:
                    base_match = base_graph.nodes()[node_name]
                    content_match = node[content_key] == base_match[content_key]
                    successor_match = list(graph.successors(node_name)) == list(
                        base_graph.successors(node_name))
                    if content_match and successor_match:
                        node_dict[node_name].render = False
                    else:
                        node_dict[node_name].render = True
                        # Add a line:
                        base_element = base_node_dict[node_name].elements[0]
                        cur_element = node_dict[node_name].elements[0]
                        cur_element.backgroundColor = base_element.backgroundColor
                        arrow = self.create_binding_arrows(
                            base_element, cur_element, padding=padding)
                        match_arrows.append(arrow)

                else:
                    node_dict[node_name].render = True
            group_id_dict = {y.id: y for _, y in node_dict.items()}
            master_group = node_dict['cfg']
            for element in master_group.elements:
                render_vals = [
                    group_id_dict[x].render for x in element.groupIds if x in group_id_dict.keys()]
                render = any(render_vals)
                # TODO: Check if this causes double counting.
                if render:
                    all_ids_added.append(element.id)
                    self.draw_objs.append(element)
            for arrow in match_arrows:
                self.draw_objs.append(arrow)
            # Add a bounding box to the configuration:
            master_group = node_dict['cfg']
            bbox, _ = self._decorate_config_box(
                master_group, label=key, padding=padding, stacking=stacking)
            node_dict["bbox"] = bbox
            prev_config_dict = node_dict

    def _decorate_config_box(self, master_group, label, padding=10, stacking="horizontal"):
        """ Helper function to add a bounding box and title to a configuration."""
        out_box = self.create_bounding_element(master_group, padding=padding, return_group=False,
                                               backgroundColor="transparent")
        out_box.strokeStyle = "dashed"

        # Also add title:
        text = primitives.Text(text=label, fontSize=24)
        # set text above the out_box:
        if stacking == "horizontal":
            text.x = out_box.x - 2 * text.height - padding
            text.y = out_box.y + out_box.height/2
            text.angle = -math.pi / 2
        elif stacking == "vertical":
            text.x = out_box.x + out_box.width/2 - text.width/2
            text.y = out_box.y - text.height - padding

        self.draw_objs.insert(0, text)
        self.draw_objs.insert(0, out_box)
        return out_box, text
