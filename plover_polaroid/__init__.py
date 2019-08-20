
from pathlib import Path
from typing import Optional

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QFileDialog

from plover import system
from plover.config import CONFIG_DIR
from plover.engine import StenoEngine
from plover.steno import Stroke
from plover.gui_qt.i18n import get_gettext
from plover.gui_qt.tool import Tool
from plover.gui_qt.utils import ToolBar

from layout_display.layout_display_ui import Ui_LayoutDisplay

_ = get_gettext()

class Polaroid(Tool, Ui_LayoutDisplay):
    TITLE = 'Plover Polaroid'
    ROLE = 'plover_polaroid'
    ICON = ':/plover_polaroid/icon.svg'
    SHORTCUT = None
    
    def __init__(self, engine: StenoEngine):
        super(Polaroid, self).__init__(engine)
        self.setupUi(self)

        engine.signal_connect('config_changed', self.on_config_changed)
        engine.signal_connect('stroked', self.on_stroke)

    def on_stroke(self, stroke: Stroke):
        keys = stroke.steno_keys[:]
        print(keys)

    def on_config_changed():
        print("config changed!")