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
from plover.formatting import RetroFormatter

from escpos.printer import Usb
from plover_polaroid.plover_polaroid_ui import Ui_PloverPolaroid

_ = get_gettext()

try:
    printer = Usb(0x0416, 0x5011, 0, 0x81, 0x03)
except:
    print("There was an error connecting to the printer.")

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
        self.translations = engine._translator.get_state().translations
        self.line = 0

        engine.signal_connect('config_changed', self.on_config_changed)
        engine.signal_connect('stroked', self.on_stroke)
        

    def on_stroke(self, stroke: Stroke):
        raw_steno = ""
        keys = stroke.steno_keys[:]
        
        formatted = RetroFormatter(self.translations)
        
        for key in keys:
            if (len(keys) == 2 and key.find("-") != -1):
                raw_steno += key[0] + key[1].replace("-", "")
            elif (len(keys) > 2):
                raw_steno += key.replace("-", "")
            else:
                raw_steno += key
        last_words = formatted.last_words(0)
        
        final_text = "[" + raw_steno + "]" + "\t\t" + last_words[self.line] or ""
        
        print(raw_steno)
        print(keys)
        print(last_words)
        self.tape.appendPlainText(final_text) 
        if (printer):
            printer.text(final_text) 
            printer.text("\n")
        
        self.line += 1
    
    def on_config_changed(self):
        print("config changed!")

   