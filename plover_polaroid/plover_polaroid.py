from pathlib import Path
from typing import Optional

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QFileDialog

from plover import system
from plover.engine import StenoEngine
from plover.gui_qt.i18n import get_gettext
from plover.steno import Stroke
from plover.translation import Translator, Translation
from plover.gui_qt.tool import Tool
from plover.gui_qt.utils import ToolBar

from escpos.printer import Usb
from plover_polaroid.plover_polaroid_ui import Ui_PloverPolaroid

_ = get_gettext()

try:
    printer = Usb(0x0416, 0x5011, 0, 0x81, 0x03)
except:
    print("There was an error connecting to the printer.")
    
def get_translation(translator: Translator):
    return translator.get_state().translations


class PloverPolaroid(Tool, Ui_PloverPolaroid):
    ''' Prints your steno notes and/or your realtime output to a generic thermal receipt printer. '''
    
    TITLE = 'Polaroid'
    ROLE = 'plover_polaroid'
    ICON = ':/plover_polaroid/icon.svg'
    SHORTCUT = 'Ctrl+P'
  
    def __init__(self, engine: StenoEngine):
        super(PloverPolaroid, self).__init__(engine)
        self.setupUi(self)
        self.tape.setFocus()

        engine.signal_connect('config_changed', self.on_config_changed)
        engine.signal_connect('stroked', self.on_stroke)

    def on_stroke(self, stroke: Stroke):
        keys = stroke.steno_keys[:]
        print(keys)
        print(get_translation(stroke))
        
        raw_steno = ''

        for key in keys:
            print(key)
            if (len(keys) == 2 and key.find("-") != -1):
                raw_steno += key[0] + key[1].replace("-", "")
            elif (len(keys) > 2):
                raw_steno += key.replace("-", "")
            else:
                raw_steno += key
        
        print(raw_steno)
        self.tape.appendPlainText(raw_steno)
        # print(translations)

        if (printer):
            printer.text(raw_steno)
            printer.text("\n")
    
    def on_config_changed(self):
        print("config changed!")

   