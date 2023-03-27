""" Excalidraw primitives"""
import uuid
import numpy as np
import copy
import math
from PIL import ImageFont
from .defaults import (BOX_DEFAULTS, BOX_SOLID_DEFAULTS, BOX_EXPORT_KEYS,
                       TEXT_DEFAULTS, CODE_TEXT, TEXT_EXPORT_KEYS, FONT_FAMILY,
                       LINE_DEFAULTS, ARROW_DEFAULTS, LINE_EXPORT_KEYS, EPSILON)


class ExcaliDrawPrimitive():
    """Base class for all excalidraw primitives
    """

    def __init__(self, *args, id=None, **kwargs):
        """Initialize the excalidraw primitive

        Args:
            id (str, optional): id of the excalidraw primitive. Defaults to None.
        """

        self.seed = np.random.randint(0, 100000)
        if id is None:
            self.id = str(uuid.uuid4())
        self.export_keys = []

    def export(self):
        export_dict = {}
        for key in self.export_keys:
            export_dict[key] = getattr(self, key)
        return export_dict

    @property
    def bbox(self):
        return [self.x, self.y, self.x + self.width, self.y + self.height]

    @property
    def center(self):
        return [self.x + self.width / 2, self.y + self.height / 2]

    def get_boundary_point(self, theta):
        # given angle theta measured from the positive x-axis, return the boundary points
        theta_lim = math.atan2(self.height, self.width)
        if abs(theta) < theta_lim:
            x = self.x + self.width * (abs(theta) < math.pi/2)
            y = self.y + (self.height / 2) + (self.width/2 * math.tan(theta))
        else:
            sign_indicator = (theta < math.pi)
            x = self.x + self.width / 2 + \
                (self.height/2 * (1/(math.tan(theta) + EPSILON))
                 * (-1 + 2 * sign_indicator))
            y = self.y + self.height * (theta < math.pi) * sign_indicator
        return [x, y]

    def get_quad_boundary_point(self, theta, padding=5):
        # given angle theta measured from the positive x-axis, return the boundary mapped to the center of the edges
        theta_lim = math.atan2(self.height, self.width)
        if abs(theta) < theta_lim or abs(theta) > math.pi - theta_lim:
            sign_indicator = (abs(theta) < math.pi/2)
            x = self.x + self.width * sign_indicator + \
                padding * (-1 + 2 * sign_indicator)
            y = self.y + (self.height / 2)
        else:
            sign_indicator = (theta > 0)
            x = self.x + self.width / 2
            y = self.y + self.height * sign_indicator + \
                padding * (-1 + 2 * sign_indicator)
        return [x, y]


class Group(ExcaliDrawPrimitive):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "group"
        self.elementIds = set()
        self.elements = []
        self.export_keys = ["type", "elementIds"]
        self._x = 0
        self._y = 0
        self._width = 0
        self._height = 0

    def add_element(self, element):
        # if element is a group, add all elements in the group.
        # TODO: Is the the right way?
        if isinstance(element, Group):
            for e in element.elements:
                self.add_element(e)
        else:
            if element.id not in self.elementIds:
                self.elements.append(element)
                self.elementIds.add(element.id)
                element.groupIds.append(self.id)
        self.update_bbox()

    def remove_element(self, element):
        if element.id in self.elementIds:
            self.elements.remove(element)
            self.elementIds.remove(element.id)
            element.groupIds.remove(self.id)
        self.update_bbox()

    def empty_all_subelements(self,):
        elements = [x for x in self.elements]
        for element in elements:
            self.remove_element(element)

    def update_bbox(self):
        # TODO: Can be optmized to only update the bbox if new elements are beyond current bbox.
        all_starts = [[element.x, element.y] for element in self.elements]

        all_starts = np.array(all_starts)
        min_x = np.min(all_starts[:, 0])
        min_y = np.min(all_starts[:, 1])

        all_ends = [[element.x + element.width, element.y + element.height]
                    for element in self.elements]
        all_ends = np.array(all_ends)
        max_x = np.max(all_ends[:, 0])
        max_y = np.max(all_ends[:, 1])

        self._x = int(min_x)
        self._y = int(min_y)
        self._width = int(max_x - min_x)
        self._height = int(max_y - min_y)

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @x.setter
    def x(self, value):
        # Update all elements and call update_bbox
        delta = value - self._x
        for element in self.elements:
            element.x += delta
        self._x = value

    @y.setter
    def y(self, value):
        # Update all elements and call update_bbox
        delta = value - self._y
        for element in self.elements:
            element.y += delta
        self._y = value

    # TODO: Group Scaling (width and height)


class Rectangle(ExcaliDrawPrimitive):

    def __init__(self, set_to_solid=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if set_to_solid:
            selected_dict = BOX_SOLID_DEFAULTS
        else:
            selected_dict = BOX_DEFAULTS

        for key, value in selected_dict.items():
            if isinstance(value, (list, dict)):
                setattr(self, key, copy.deepcopy(value))
            else:
                setattr(self, key, value)

        for key, value in kwargs.items():
            if isinstance(value, (list, dict)):
                setattr(self, key, copy.deepcopy(value))
            else:
                setattr(self, key, value)

        self.export_keys = BOX_EXPORT_KEYS
        self.type = "rectangle"


class Diamond(Rectangle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key, value in kwargs.items():
            setattr(self, key, value)
        self.type = "diamond"

    def get_boundary_points(self, theta):
        # given angle theta measured from the positive x-axis, return the boundary points
        ...


class Ellipse(Rectangle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for key, value in kwargs.items():
            setattr(self, key, value)
        self.type = "ellipse"

    def get_boundary_points(self, theta):
        # given angle theta measured from the positive x-axis, return the boundary points
        ...


class Text(ExcaliDrawPrimitive):

    def __init__(self, set_to_code=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "text" in kwargs:
            if not isinstance(kwargs["text"], str):
                kwargs["text"] = str(kwargs["text"])
        # Quick setting for code text:
        if set_to_code:
            selected_dict = CODE_TEXT
        else:
            selected_dict = TEXT_DEFAULTS

        for key, value in selected_dict.items():
            if key in ["width", "height"]:
                continue
            if key in ["fontFamily", "fontSize", "text"]:
                setattr(self, f"_{key}", value)
            else:
                if isinstance(value, (list, dict)):
                    setattr(self, key, copy.deepcopy(value))
                else:
                    setattr(self, key, value)

        self._update_font()
        for key, value in kwargs.items():
            if key in ["width", "height"]:
                continue
            setattr(self, key, value)
        # Load the different fonts, and set it:
        self.text = self._text

        self.type = "text"
        self.export_keys = TEXT_EXPORT_KEYS

    def _update_font(self):
        self._font_file = FONT_FAMILY[self._fontFamily]
        self._font = ImageFont.truetype(self._font_file, self._fontSize)

    def _update_size(self):
        self._width, self._height = self._font.getsize(self._text)

    @property
    def fontFamily(self):
        return self._fontFamily

    @fontFamily.setter
    def fontFamily(self, value):
        self._fontFamily = value
        self._update_font()

    @property
    def fontSize(self):
        return self._fontSize

    @fontSize.setter
    def fontSize(self, value):
        self._fontSize = value
        self._update_font()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.defaul_text = value
        self._update_size()

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height


class Line(ExcaliDrawPrimitive):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if isinstance(self, Arrow):
            selected_dict = ARROW_DEFAULTS
        else:
            selected_dict = LINE_DEFAULTS

        for key, value in selected_dict.items():
            if key in ["width", "height", "points"]:
                continue
            if isinstance(value, (list, dict)):
                setattr(self, key, copy.deepcopy(value))
            else:
                setattr(self, key, value)

        self.points = selected_dict["points"]

        for key, value in kwargs.items():
            setattr(self, key, value)
        self.export_keys = LINE_EXPORT_KEYS
        self.type = "line"

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def points(self):
        return self._points

    @points.setter
    def points(self, values):
        # TODO: Currently, we don't calculate the shape change due to arrowheads.
        xy_shift = (0, 0)
        if values[0] != [0, 0]:
            # move all the points, and the x, y values
            values = [[x[0] - values[0][0], x[1] - values[0][1]]
                      for x in values]
            xy_shift = (values[0][0], values[0][1])

        self._points = [x for x in values]
        self._points = values
        self.x += xy_shift[0]
        self.y += xy_shift[1]

        all_points = np.array(values)
        # get bounding box of all points
        min_x = int(np.min(all_points[:, 0]))
        min_y = int(np.min(all_points[:, 1]))
        max_x = int(np.max(all_points[:, 0]))
        max_y = int(np.max(all_points[:, 1]))
        self._width = max_x - min_x
        self._height = max_y - min_y

    def set_start_binding(self, element, padding=10):
        # TODO: Also have to ensure the start point is within reach of the element?
        self.startBinding = {
            "elementId": element.id,
            "focus": 0,
            "gap": padding
        }
        element.boundElements.append(
            {
                "id": self.id,
                "type": "arrow"
            }
        )

    def set_end_binding(self, element, padding=10):
        # TODO: Also have to ensure the end point is within reach of the element?
        # end_point = self._points[-1]
        self.endBinding = {
            "elementId": element.id,
            "focus": 0,
            "gap": padding
        }
        element.boundElements.append(
            {
                "id": self.id,
                "type": "arrow"
            }
        )

class Arrow(Line):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.type = "arrow"
