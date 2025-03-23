#* SNotesApp

from os.path import exists
import streamlit as st
import tomli


# this has to go before imports because imports use secrets.toml
DEFAULT_SECRETS = """
author = "Anonymous"
data_dir = "./data/"
months_language = "en" # supported: "en", "es"
"""

if not exists("./secret.toml"):
    with open("./secrets.toml", "w") as f:
        f.write(DEFAULT_SECRETS)

SECRETS = tomli.load(open("./secrets.toml", "rb"))
SAVE_EVERY = 60 * 5 # in seconds, set to 5 minutes

st.set_page_config(
    layout="centered", # centered is optional.
    initial_sidebar_state="auto", # this or "expanded" # todo change this depending on if mobile
    page_title="SNotesApp",
    # page_icon=None, # todo make a logo
)


import streamlit_extras.row as st_r
from copy import deepcopy as copy
from typing import Literal, Any
import code_editor as st_ce
from random import randint
import sprinting as st_p
import scanvas as st_cv
from os import listdir
from PIL import Image
import numpy
import time
import dill
import re


global_editing = True #? keep this in the app itself? idk



def restart_app_singleton() -> None:
    st.session_state.app = App()
    st.session_state.app.block_id = 0
    st.session_state.app.blocks.append(Block("title", "Insert title"))

def get_app() -> "App":
    # note: cant be used for setting
    return st.session_state.app


class App:
    def __init__(self):
        self.blocks: list["Block"] = []
        self.block_id = 0
        self.name = "new_notes_" + str(randint(100000, 999999)) + ".notes" # if this overwrites you, you're cooked
        self.saved = False
        self.last_saved = None

    def collapse_block_editing(self) -> None:
        # for each block, set their inner editing variable to False
        for block in self.blocks:
            block.editing = False

    def delete_block_by_id(self, id: int) -> None:
        index = -1

        for i, block in enumerate(self.blocks):
            if block.id == id:
                index = i

        assert index != -1
        self.blocks.pop(index)

    def get_new_block_id(self) -> int:
        self.block_id += 1

        return self.block_id - 1
    
    def get_title(self) -> str:
        assert self.blocks[0].type == "title"
        return self.blocks[0].content
    
    def make_printable(self) -> list[str | Image.Image]:
        return [block.content for block in self.blocks[1:]] # todo rerank headers, add replacements ("->")
    
    def name_is_new(self) -> bool:
        return re.match(r"new_notes_([123456789]+)\.notes", self.name)
    

class Block:
    def __init__(self, type: Literal["text", "image"], content: Any) -> None:
        self.type = type
        self.content = content
        self.editing = False
        self.id = get_app().get_new_block_id()

        assert type in ["title", "text", "image"]

    def activate_editing(self) -> None:
        get_app().collapse_block_editing() # used to ensure only 1 editing block is active at a time.
        get_app().saved = False
        st_p.set_uncompiled()
        self.editing = True

        if self.type == "image":
            st_cv.canvas_save(f"canvas_{self.id}")

    def save_edits(self) -> None:
        self.editing = False

    def delete_block(self) -> None:
        get_app().delete_block_by_id(self.id) # commits suicide

    def render_text_normal(self):
        st.markdown(self.content) # todo check for "#" to not enable titles # expensive?

    def render_text_gediting(self, column):
        if self.editing:
            with column:
                buffer = st_ce.code_editor(
                    self.content,
                    lang="markdown",
                    height=2**128,
                    focus=True,
                    response_mode=["blur", "debounce"],
                    props={ # thoroughly craft this later:
                        # https://github.com/securingsincity/react-ace/blob/master/docs/Ace.md
                        # https://github.com/ajaxorg/ace/wiki/Configuring-Ace#editor-options
                        "showGutter": False,
                        "enableBasicAutocompletion": False,
                        "enableLiveAutocompletion": False,
                    },
                    options={
                        "highlightActiveLine": False,
                        "wrap": True,
                        "wrapEnabled": True,
                    },
                    key=f"editor_{self.id}", # makes it stable
                )["text"]

                if buffer:
                    self.content = buffer

        else:
            with column:
                self.render_text_normal()
                #//st.markdown(f'<div style="text-align: justify;">{self.content}\n</div>', unsafe_allow_html=True)
                #* for now: keep it justified by default but later add it as an option
                #* and include a settings option in the JSON file format
                # remake this, compatible with latex (it simply wont work if i use html.)
                #? is it even worth it?

    def render_image_normal(self):
        if self.content is not None:
            st.image(self.content)

    def render_image_gediting(self, column): #? can this be centered?
        with column:
            if self.editing:
                canvas_result = st_cv.canvas(
                    width=500,
                    key=f"canvas_{self.id}"
                )

                if canvas_result.image_data is not None:
                    self.content = canvas_result.image_data

            else:
                self.render_image_normal()

    def render(self, global_editing: bool) -> None:
        with st.container(border=(self.type != "title")):
            if global_editing:
                if self.type == "title":
                    def on_change():
                        get_app().saved = False
                        st_p.set_uncompiled()

                    self.content = st.text_input("Title", self.content, on_change=on_change, key="TITLE")
                    return

                col1, col2 = st.columns([60, 1])
                
                match self.type:
                    case "text":
                        self.render_text_gediting(col1)

                    case "image":
                        self.render_image_gediting(col1)

                with col2:
                    if self.editing:
                        st.button("", icon=":material/check:", help="Add new block",
                            on_click=self.save_edits, key=f"save_{self.id}")
                    else:
                        st.button("", icon=":material/edit:", help="Edit this block",
                            on_click=self.activate_editing, key=f"edit_{self.id}")

                    st.button("", icon=":material/delete:", help="Delete this block",
                        on_click=self.delete_block, key=f"del_{self.id}")
                    st.button("", icon=":material/library_add:", help="Add new block after this one",
                        on_click=add_block, args=(get_app().blocks.index(self) + 1,), key=f"add_{self.id}")

            else:
                match self.type:
                    case "title":
                        st.divider()
                        st.title(self.content)
                        st.divider()

                    case "text":
                        self.render_text_normal()

                    case "image":
                        self.render_image_normal()


def save_notes():
    with open(SECRETS["data_dir"] + get_app().name, "wb") as f:
        dill.dump(get_app(), f)
    get_app().saved = True
    get_app().last_saved = time.time()
    st.rerun()

@st.dialog("Save notes as")
def save_notes_as():
    st.text("Note: Include the extension (for example: notes.pkl or notes.notes)")
    name = st.text_input("New name", get_app().name)
    col1, col2, col3 = st.columns(3)

    if col1.button("Cancel", type="primary", use_container_width=True):
        st.rerun()

    elif col2.button("Just rename", use_container_width=True):
        get_app().name = name
        get_app().saved = False
        st.rerun()

    elif col3.button("Save", use_container_width=True):
        get_app().name = name
        save_notes()
        st.rerun()

@st.dialog("Open notes")
def open_notes():
    if not get_app().saved and len(get_app().blocks) != 1:
        st.warning("Warning: You have unsaved changes!", icon=":material/warning:")

    name = st.selectbox("Choose a file", listdir(SECRETS["data_dir"]))
    col1, col2 = st.columns(2)

    if col1.button("Cancel", type="primary", use_container_width=True):
        st.rerun()
    
    elif col2.button("Open", use_container_width=True, disabled=name is None):
        with open(SECRETS["data_dir"] + name, "rb") as f:
            loaded_app: App = dill.load(f)
            restart_app_singleton()
            get_app().name = name
            get_app().blocks = loaded_app.blocks
            get_app().block_id = loaded_app.block_id
            get_app().saved = True
            st_p.set_uncompiled()

        st.rerun()

@st.dialog("New notes")
def new_notes():
    if not get_app().saved and len(get_app().blocks) != 1:
        st.warning("Warning: You have unsaved changes!", icon=":material/warning:")

    col1, col2 = st.columns(2)

    if col1.button("Cancel", type="primary", use_container_width=True):
        st.rerun()
    
    elif col2.button("New notes", use_container_width=True):
        restart_app_singleton()
        st_p.set_uncompiled()
        st.rerun()

def sidebar():
    global global_editing

    with st.sidebar:
        st.title("SNOTESAPP")
        st.markdown(f"**Filename**: _{get_app().name}_")
        st.markdown(f"**Status**: _{'saved' if get_app().saved else 'unsaved'}_")

        row = st_r.row(4) #? consider changing for a column
        if row.button("", icon=":material/add_circle:", use_container_width=True, help="New notes"):
            new_notes()

        if row.button("", icon=":material/edit_document:", use_container_width=True, help="Open notes"):
            open_notes()

        if row.button("", icon=":material/save:", use_container_width=True, help="Save notes"):
            save_notes()

        if row.button("", icon=":material/save_as:", use_container_width=True, help="Save notes as"):
            save_notes_as()

        past_ge = global_editing
        global_editing = st.toggle("Edit mode", help="Activates editing mode", value=True)
        if not global_editing:
            get_app().collapse_block_editing()

            if past_ge != global_editing: # just changed
                for block in get_app().blocks:
                    if block.type == "image":
                        st_cv.canvas_save(f"canvas_{block.id}")

        st.text(f"Blocks: {len(get_app().blocks)}")

        if st.toggle("Periodically save", help="Periodically saves the project every 5 minutes if it has been asigned a custom name", value=False):
            if not get_app().name_is_new():
                if get_app().last_saved:
                    if time.time() - get_app().last_saved > SAVE_EVERY:
                        save_notes()
                else:
                    save_notes()


        # add undo, redo here

        st_p.print_menu(get_app().get_title(), get_app().make_printable())


@st.dialog("Add a new block")
def add_block(index=None):
    type = st.selectbox("New block type", ["text", "image"])
    col1, col2 = st.columns(2)

    if index == None:
        index = len(get_app().blocks)

    def add_block_callback():
        st_p.set_uncompiled()
        match type:
            case "text":
                get_app().blocks.insert(index, Block("text", "..."))

            case "image":
                default = numpy.array(Image.new("RGBA", (500, 400),  (0, 0, 0, 0)))
                get_app().blocks.insert(index, Block("image", default))

    if col1.button("Cancel", type="primary", use_container_width=True):
        st.rerun()
        
    if col2.button("Create new block", on_click=add_block_callback, use_container_width=True):
        st.rerun()


def main():
    if "app" not in st.session_state: # first time running this
        restart_app_singleton()

    sidebar()

    # main functionality
    for block in get_app().blocks:
        block.render(global_editing)

    if global_editing:
        _, center, _ = st.columns([1.5, 1, 1.5])
        with center:
            st.button("Add new block", on_click=add_block, icon=":material/library_add:", use_container_width=True)


if __name__ == "__main__":
    main()
