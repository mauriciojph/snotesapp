import streamlit_drawable_canvas as st_cv
from svgpathtools import parse_path
import streamlit_extras.row as st_r
from copy import deepcopy as copy
import streamlit as st
from PIL import Image
import math


# note: these functions may or may not have been written by AI

def rect_to_path(rect):
    """Convert a rectangle dict (assumes no rotation) into an svgpathtools Path."""

    x, y, w, h = rect['left'], rect['top'], rect['width'], rect['height']
    d = f"M {x},{y} L {x+w},{y} L {x+w},{y+h} L {x},{y+h} Z"

    return parse_path(d)

def commands_to_path(commands):
    """Convert a list-of-commands (e.g., [['M', 10, 20], ['L', 30, 40]]) into a Path."""

    d = " ".join(cmd[0] + " " + " ".join(map(str, cmd[1:])) for cmd in commands)

    return parse_path(d)

def path_intersects(path1, path2):
    """Return True if any segment in path1 intersects any segment in path2."""

    for seg1 in path1:
        for seg2 in path2:
            if seg1.intersect(seg2):
                return True
            
    return False

def circle_to_path(circle_obj):
    """
    Convert a circle dict into an svgpathtools Path.
    Assumes the circle always has originX 'left' and originY 'center'.
    The center is computed as (left + radius, top).
    """

    r = circle_obj['radius']
    left = circle_obj['left']
    top = circle_obj['top']
    cx = left + r
    cy = top

    cx = circle_obj["left"] + circle_obj["radius"] * math.cos(circle_obj["angle"] * math.pi / 180)
    cy = circle_obj["top"] + circle_obj["radius"] * math.sin(circle_obj["angle"] * math.pi / 180)
    d = (
        f"M {cx + r},{cy} "
        f"A {r},{r} 0 1,0 {cx - r},{cy} "
        f"A {r},{r} 0 1,0 {cx + r},{cy} Z"
    )
    return parse_path(d)

def has_point_inside(path, rect):
    """
    Check if any coordinate point in the commands list is inside the rectangle.
    Assumes commands have coordinate pairs starting at index 1.
    """

    x0, y0 = rect['left'], rect['top']
    x1, y1 = x0 + rect['width'], y0 + rect['height']

    def check_single_point(px, py):
        if x0 <= px <= x1 and y0 <= py <= y1:
            return True
        else:
            return False

    for t in path:
        if t[0] in "ML":
            if check_single_point(t[1], t[2]):
                return True

        elif t[0] == "Q":
            if check_single_point(t[1], t[2]) or check_single_point(t[3], t[4]):
                return True
            
    return False

def circle_intersects_rect(circle_obj, rect):
    """
    Check if a circle intersects an axis-aligned rectangle.
    Assumes the circle has originX 'left' and originY 'center', so its center is (left + radius, top).
    """
    r = circle_obj['radius']
    cx = circle_obj['left'] + r
    cy = circle_obj['top']
    cx = circle_obj["left"] + circle_obj["radius"] * math.cos(circle_obj["angle"] * math.pi / 180)
    cy = circle_obj["top"] + circle_obj["radius"] * math.sin(circle_obj["angle"] * math.pi / 180)
    rx, ry = rect['left'], rect['top']
    rw, rh = rect['width'], rect['height']
    # Find the closest point on the rectangle to the circle's center
    closest_x = max(rx, min(cx, rx + rw))
    closest_y = max(ry, min(cy, ry + rh))
    dist_sq = (cx - closest_x) ** 2 + (cy - closest_y) ** 2
    return dist_sq < r * r

def remove_intersecting_lines(obj_list, rect_obj):
    """
    Given a list of SVG objects and a rectangle object (with type 'rect'),
    return a new list with the rectangle removed and every path that
    intersects the rectangle also removed.
    """
    
    rect_path = rect_to_path(rect_obj)
    new_objs = []
    
    for obj in obj_list:
        if obj is rect_obj:
            continue
        
        elif obj["type"] == "path":
            if has_point_inside(obj["path"], rect_obj) or path_intersects(commands_to_path(obj["path"]), rect_path):
                continue

        elif obj["type"] == "line":
            temp = [
                ("M", obj["left"] + obj["x1"], obj["top"] + obj["y1"]),
                ("L", obj["left"] + obj["x2"], obj["top"] + obj["y2"])
            ]
            
            if has_point_inside(temp, rect_obj) or path_intersects(commands_to_path(temp), rect_path):
                continue

        elif obj["type"] == "circle":
            if circle_intersects_rect(obj, rect_obj) or path_intersects(circle_to_path(obj), rect_path):
                continue

        new_objs.append(obj)
        
    return new_objs


class App:
    def __init__(self):
        self.key = 0
        self.regen_key()
        self.json_data = None
        self.buffer = None
        self.drawing_mode = "freedraw"

    def get_key(self):
        self.key += 1

        return self.key - 1
    
    def regen_key(self):
        self.curr_key = f"canvas_{self.get_key()}"

def get_app(key) -> App:
    return st.session_state.canvas[key]


TARGET_FILL = "#c751c6"

def canvas_save(key: str = "canvas"):
    """Call this before making the canvas dissapear, to preserve canvas state between different occasions, depending on a key."""

    if "canvas" not in st.session_state or key not in st.session_state.canvas:
        return

    if get_app(key).json_data != get_app(key).buffer:
        get_app(key).json_data = copy(get_app(key).buffer)

def canvas(
    fill_color: str = "#eee",
    stroke_width: int = 5,
    stroke_color: str = "#ccc",
    background_color: str = "",
    background_image: "Image.Image" = None,
    width: int = 600,
    height: int = 400,
    display_toolbar: bool = True,
    additional_toolbar: bool = True,
    point_display_radius: int = 3,
    key: str = "canvas"
) -> st_cv.CanvasResult:
    """Canvas element, expanded from streamlit-drawable-canvas. Supports more built in toolbar features, preserving state, erasing tool, and more."""

    if fill_color == TARGET_FILL:
        st.toast(f"Can't use fill color {TARGET_FILL}! (Reserved for internal functionality)")
        fill_color = "#eee"
        assert TARGET_FILL != "#eee"

    edited = False

    if "canvas" not in st.session_state:
        st.session_state.canvas = {key: App()}
    if key not in st.session_state.canvas:
        st.session_state.canvas[key] = App()

    placeholder = st.container()
    second_placeholder = st.container()

    with second_placeholder.container():
        # todo actually listen to display_toolbar
        row = st_r.row([5, 1], vertical_align="bottom")

        tool = row.selectbox(
            "Tool:",
            ("freedraw", "eraser", "line", "rect", "circle", "polygon", "point"),
        )
        do_clear = row.button("", icon=":material/replay:", help="Clear the canvas")
        real_tool = tool

        if tool == "eraser":
            real_tool = "rect"
            fill_color = TARGET_FILL

    with placeholder.container():
        canvas_result = st_cv.st_canvas(
            fill_color=fill_color,
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color=background_color,
            background_image=background_image,
            update_streamlit=True,
            width=width,
            height=height,
            drawing_mode=real_tool,
            initial_drawing=(get_app(key).json_data),
            display_toolbar=False,
            point_display_radius=point_display_radius,
            key=f"{key}_{get_app(key).curr_key}",
        )

        #//st.text(get_app(key).curr_key)

    with second_placeholder.container():
        if canvas_result.json_data is not None and canvas_result.json_data["objects"]:
            if canvas_result.json_data != get_app(key).buffer:
                edited = True

            get_app(key).buffer = canvas_result.json_data
            #//st.json(get_app().buffer, expanded=True)

        if do_clear:
            get_app(key).regen_key()
            get_app(key).json_data = None
            get_app(key).buffer = None
            st.rerun()

        if tool == "eraser":
            if edited and get_app(key).buffer and get_app(key).buffer["objects"]: # dunno if the second part is redundant
                rect = get_app(key).buffer["objects"][-1]

                if rect["type"] == "rect" and rect["fill"] == TARGET_FILL: # our erasing rect
                    get_app(key).regen_key()
                    get_app(key).json_data = copy(get_app(key).buffer)
                    get_app(key).json_data["objects"] = remove_intersecting_lines(get_app(key).buffer["objects"], rect)
                    st.rerun()

    return canvas_result

if __name__ == "__main__":
    canvas()

# code snippet for when i implement more featuers:
_ = """
stroke_width = st.sidebar.slider("Stroke width: ", 1, 25, 3)
stroke_color = st.sidebar.color_picker("Stroke color hex: ")

drawing_mode = st.sidebar.selectbox(
    "Drawing tool:",
    ("freedraw", "line", "rect", "circle", "polygon", "point"),
)

kwargs = {
    "stroke_width": stroke_width,
    "stroke_color": stroke_color,
    "update_streamlit": True,
    "width": 500,
    #//"drawing_mode": "freedraw", # todo add more drawing modes (how?)
    "drawing_mode": drawing_mode,
    "display_toolbar": True,
    "key": "canvas_editor_key",
}"""
