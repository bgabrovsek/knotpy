
_DEFAULT_ROTATION = 0.0
# Arc
_DEFAULT_ARC_COLOR = "tab:blue"
_DEFAULT_ARC_WIDTH = 4.0  # strand width
_DEFAULT_ARC_STYLE = "solid"  # 'dashed', 'dotted', 'dashdot'
_DEFAULT_ARC_ALPHA = None  # transparency, None = fully opaque
_DEFAULT_ARC_STROKE_WIDTH = None # stroke around the
_DEFAULT_ARC_STROKE_COLOR = "white" # stroke around the
_DEFAULT_ARC_STROKE_ALPHA = None # stroke transparnecy
_DEFAULT_GAP = 0.1  # arc break gap at under-passing
_DEFAULT_CMAP = None
# Vertex
_DEFAULT_VERTEX_COLOR = "black"
_DEFAULT_VERTEX_SIZE = 0.15
_DEFAULT_VERTEX_ALPHA = None
_DEFAULT_VERTEX_STROKE_COLOR = "black"
_DEFAULT_VERTEX_STROKE_WIDTH = 0
_DEFAULT_VERTEX_STROKE_ALPHA = None
# Arrow
_DEFAULT_ARROW_COLOR = None # defaults to arc_color
_DEFAULT_ARROW_WIDTH = 0.15
_DEFAULT_ARROW_LENGTH = 0.12
_DEFAULT_ARROW_STYLE = "open"  # "open" or "closed"
_DEFAULT_ARROW_CAP_STYLE = "round"
_DEFAULT_ARROW_POSITION = "middle"
_DEFAULT_ARROW_ALPHA = None
# Labels
_DEFAULT_LABEL_ENDPOINTS = False
_DEFAULT_LABEL_ARCS = False
_DEFAULT_LABEL_NODES = False
_DEFAULT_LABEL_COLOR = "black"
_DEFAULT_LABEL_FONT_SIZE = 14
_DEFAULT_LABEL_FONT_FAMILY = "serif"  # or 'sans-serif', 'monospace', etc.
_DEFAULT_LABEL_HORIZONTAL_ALIGNMENT = "left"
_DEFAULT_LABEL_VERTICAL_ALIGNMENT = "top"
_DEFAULT_LABEL_ALPHA = None
# Title
_DEFAULT_TITLE = False,  # or string
_DEFAULT_TITLE_COLOR = "black"
_DEFAULT_TITLE_FONT_SIZE = 16,
_DEFAULT_TITLE_FONT_FAMILY = "serif"
_DEFAULT_TITLE_ALPHA = None
# Other
_DEFAULT_SHOW_CIRCLE_PACKING = False  # visualize circle-packing circles
_DEFAULT_PADDING_FRACTION = 0.05
_DEFAULT_SHOW_AXIS = False
_DEFAULT_SHOW = False

# Z-order (stacking) for plot elements; lower values are drawn first.
_Z_CIRCLES = 0
_Z_ARC_STROKE = 1
_Z_ARC = 2
_Z_ENDPOINT_STROKE_UNDER = 1
_Z_ENDPOINT_UNDER = 2
_Z_ENDPOINT_STROKE_OVER = 3
_Z_ENDPOINT_OVER = 4
_Z_ARROW = 5
_Z_VERTEX = 6
_Z_TEXT = 7
