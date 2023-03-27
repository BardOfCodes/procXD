"""Specify the default values for excalidraw primitives."""
import copy
import os

# Settings for Rectangle, Ellipse, Diamond
EPSILON = 1e-9
BOX_DEFAULTS = dict(
    x=0,
    y=0,
    width=100,
    height=100,
    angle=0,
    strokeColor="#000000",
    backgroundColor="#ffffff",
    fillStyle="hachure",
    strokeStyle="solid",
    strokeWidth=1,
    roughness=1,
    opacity=100,
    groupIds=[],
    roundness={"type": 3},
    version=1,
    versionNonce=0,
    isDeleted=False,
    boundElements=[],
    updated=0,
    link=None,
    locked=False,
)

# Quick extension to solid with some color
BOX_SOLID_DEFAULTS = copy.deepcopy(BOX_DEFAULTS)
BOX_SOLID_DEFAULTS["fillStyle"] = "solid"
BOX_SOLID_DEFAULTS["backgroundColor"] = "#e64980"
BOX_SOLID_DEFAULTS["roundness"] = None

# Keys to export
BOX_EXPORT_KEYS = list(BOX_DEFAULTS.keys())

# Extra properties for Text
text_defaults = dict(
    text="default text",
    fontSize=20,
    fontFamily=1,
    textAlign="left",
    verticalAlign="top",
    baseline=18,
    containerId=None,
    originalText="default text",
    roundness=None,
)
TEXT_DEFAULTS = copy.deepcopy(BOX_DEFAULTS)
TEXT_DEFAULTS.update(text_defaults)

# Quick extension to code text
CODE_TEXT = copy.deepcopy(TEXT_DEFAULTS)
CODE_TEXT["fontFamily"] = 3

# Additional Text keys to export
TEXT_EXPORT_KEYS = list(TEXT_DEFAULTS.keys())

# Font family for estimating font size
current_file_dir = os.path.dirname(os.path.abspath(__file__))
FONT_FAMILY = {
    1: "fonts/Virgil.ttf",
    2: "fonts/Assistant-VariableFont.ttf",
    3: "fonts/CascadiaCode.ttf",
}
FONT_FAMILY = {x: os.path.join(current_file_dir, y) for x, y in FONT_FAMILY.items()}

# lines:
line_defaults = dict(
    points=[[0, 0], [100, 100]],
    lastCommitedPoint=None,
    startBinding=None,
    endBinding=None,
    startArrowhead=None,
    endArrowhead=None,
    roundess={"type": 2},  # It has only two configurations None and type 2
)
LINE_DEFAULTS = copy.deepcopy(BOX_DEFAULTS)
LINE_DEFAULTS.update(line_defaults)

LINE_EXPORT_KEYS = list(LINE_DEFAULTS.keys())


ARROW_DEFAULTS = copy.deepcopy(LINE_DEFAULTS)
ARROW_DEFAULTS["endArrowhead"] = "arrow"

additional_keys = ["type", "id", "seed"]
updatelist = [BOX_EXPORT_KEYS, TEXT_EXPORT_KEYS, LINE_EXPORT_KEYS]
for keylist in updatelist:
    keylist.extend(additional_keys)
