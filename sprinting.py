from copy import deepcopy as copy
from PIL.Image import Image
import streamlit as st
import numpy as np
import typst
import tomli
import PIL


SECRETS = tomli.load(open("./secrets.toml", "rb"))


class App():
    def __init__(self):
        self.compiled = None

def get_app() -> App:
    return st.session_state.printing

    # note: it could be done like this
    """
    if not "printing" in st.session_state:
        st.session_state.printing = App()

    return st.session_state.printing()
    """ # then theres no need to define it and access it in separate moments

def set_uncompiled():
    get_app().compiled = None


def compile(title: str, printable: list[str, Image]) -> bytes:
    """Compiles the printable into a pdf returning the bytes"""

    body = ""

    # note: TYPST_TEMPLATE **has** to go here because otherwise it bugs out 99% of the time

    # $title, $body #? $author, $lang? -> not for now -> future feature
    TYPST_TEMPLATE = open("./template.typ", "r", encoding="utf-8").read()

    # $path
    IMAGE = '#align(center, [#image("$path")])\n\n'

    # $body
    MD_TEXT = "#cmarker.render(```\n$body\n```, math: mitex)\n\n"

    for i, block in enumerate(printable):
        if type(block) == str:
            body += MD_TEXT.replace("$body", block)
        elif type(block) == np.ndarray:
            numbers = copy(block)
            r, g, b, a = numbers[..., 0], numbers[..., 1], numbers[..., 2], numbers[..., 3]
            non_transparent = a > 0

            luminance = (0.299 * r + 0.587 * g + 0.114 * b)[non_transparent]

            if np.mean(luminance) > 127:
                numbers[..., :3][non_transparent] = 255 - numbers[..., :3][non_transparent]

            img = PIL.Image.fromarray(numbers.astype("uint8"), mode="RGBA")
            img.save("./cache/image_{i}.png", "PNG")

            body += IMAGE.replace("$path", f"image_{i}.png")
        else:
            print(f"unknown type: {type(block)}")

    with open(f"./cache/temp_typst.typ", "w+", encoding="utf-8") as f:
        f.write(TYPST_TEMPLATE.replace("$body", body).replace("$title", title))
        f.close()

    return typst.compile("./cache/temp_typst.typ", format="pdf")


def print_menu(title: str, printable: list[str, Image]):
    if not "printing" in st.session_state:
        st.session_state.printing = App()

    col1, col2 = st.columns([1, 2])

    if col1.button("Compile", use_container_width=True):
        get_app().compiled = compile(title, printable)

    col2.download_button("Download PDF", data=get_app().compiled or bytes(), file_name=f"{title}.pdf", disabled=get_app().compiled is None, use_container_width=True, icon=":material/file_save:")
