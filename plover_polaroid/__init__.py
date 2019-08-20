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
from escpos.printer import Usb
from layout_display.layout_display_ui import Ui_LayoutDisplay

_ = get_gettext()
printer = Usb(0x0416, 0x5011, 0, 0x81, 0x03)


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
        
        raw_steno = ""
        keys = stroke.steno_keys[:]

        for key in keys:
            if (len(keys) >= 2):
                raw_steno += key.replace("-", "")
            else:
                raw_steno += key
        
        print(raw_steno)
        printer.text(raw_steno)
        printer.text("\n")

    def on_config_changed():
        print("config changed!")
