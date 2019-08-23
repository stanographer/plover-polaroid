from pathlib import Path
from typing import Optional

from PyQt5.QtCore import QSettings
from PyQt5.QtWidgets import QFileDialog

from plover import system
from plover.config import CONFIG_DIR
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

class PloverPolaroid(Tool, Ui_PloverPolaroid):
    ''' Prints your steno notes and/or your realtime output to a generic thermal receipt printer. '''
    
    TITLE = 'Polaroid'
    ROLE = 'plover_polaroid'
    ICON = ':/plover_polaroid/icon.svg'
    SHORTCUT = 'Ctrl+P'
  
    def __init__(self, engine: StenoEngine):
        
        super(PloverPolaroid, self).__init__(engine)
        
        ''' My printer's defaults '''
        VENDOR_ID = 0x0416
        PRODUCT_ID = 0x5011
        IN_EP = 0x81
        OUT_EP = 0x03
        
        self.vendor_id = VENDOR_ID
        self.prod_id = PRODUCT_ID
        self.in_ep = IN_EP
        self.out_ep = OUT_EP
        
        self.setupUi(self)
        self._tape.setFocus()
        self.started = False
        
        ''' Default vendor specs '''
        self._vendor_id.setText(str(hex(self.vendor_id)))
        self._prod_id.setText(str(hex(self.vendor_id)))
        self._in_ep.setText(str(hex(self.in_ep)))
        self._out_ep.setText(str(hex(self.out_ep)))
        
        ''' UI listeners '''
        self._connect.clicked.connect(lambda: self.connect_printer())
        self._quit.clicked.connect(self.close)
        self._both_steno_realtime.setChecked(True)
        self._both_steno_realtime.toggled.connect(self.both_clicked)
        self._raw_only.toggled.connect(self.raw_steno_only_clicked)
        self._text_only.toggled.connect(self.text_only_clicked)
        
        ''' Get the state of the Translator '''
        self.translations = engine._translator.get_state().translations
        self.starting_point = len(self.translations)
        print(self.translations)
        
        engine.signal_connect('config_changed', self.on_config_changed)
        engine.signal_connect('stroked', self.on_stroke)
        self.on_config_changed(engine.config)
        
        ''' Connect printer on init '''
        self.connect_printer()

    def connect_printer(self):
        try:
            self._tape.setPlainText("Printer is ready.")
            self._connect.setEnabled(False)
            self.started = True
            self.printer = Usb(
                self.vendor_id,
                self.prod_id,
                0,
                self.in_ep,
                self.out_ep
            )

        except:
           self._tape.setPlainText("Printer is not connected or cannot establish communication.")
           self._connect.setEnabled(True)

    def on_stroke(self, stroke: Stroke):
        if (self.started):
            raw_steno = ""
            tran_text = ""
            paragraph = ""
            keys = stroke.steno_keys[:]

            formatted = self.translations[-1].english if self.translations else []
            tran_text = formatted or ""
            
            for key in keys:
                if (len(keys) == 2 and key.find("-") != -1):
                    raw_steno += key[0] + key[1].replace("-", "")
                elif (len(keys) > 2):
                    raw_steno += key.replace("-", "")
                else:
                    raw_steno += key
            
            if (self._both_steno_realtime.isChecked()):
                if (self.printer):
                    self._tape.appendPlainText(raw_steno + "\t\t" + tran_text) 
                    self.left_right(self.printer, raw_steno, tran_text)
            
            elif (self._raw_only.isChecked()):
                self._tape.appendPlainText(raw_steno) 
                
                try:
                    self.printer.text(raw_steno)
                    self.printer.text("\n")
                except:
                    self._tape.setPlainText("Printer is not connected or cannot establish communication.")
                    self._connect.setEnabled(True)
                
            else:
                tran_text = self.translations[self.starting_point:]
                formatter = RetroFormatter(self.translations[self.starting_point:]) or ""
                
                for word in formatter.last_words(-1):
                    paragraph += word
                    
                    if (word and word.find("\n" or "\r") > -1):
                        try:
                            self.printer.text(paragraph)
                            self.printer.text("\n\n")
                            self.starting_point = len(self.translations)
                            paragraph = ""
                            
                        except:
                            self._tape.setPlainText("Printer is not connected or establish communication.")
                            self._connect.setEnabled(True)
                            
                self._tape.setPlainText(paragraph)
                
    ''' Formats receipt output so that steno is left and translations on right. '''          
    def left_right(self, p, left, right):
        try:
            p.text("{:<20}{:>12}".format(left, right))
            self.printer.text("\n")
        except:
            self._tape.setPlainText("Printer is not connected or cannot establish communication.")
            self._connect.setEnabled(True)
                
    def both_clicked(self):
        self._tape.setPlainText("Both your steno and translations will appear side by side.")
        self.starting_point = len(self.translations)
        
    def raw_steno_only_clicked(self):
        self._tape.setPlainText("Only your raw steno notes will be printed.")
        self.starting_point = len(self.translations)
    
    def text_only_clicked(self):
        self._tape.setPlainText("In Translations Only mode, send a new line (return or enter strokes) to print your entire output.")
        self.starting_point = len(self.translations) 
        
    def _save_state(self, settings: QSettings):
        '''
        Save state to settings.
        Called via save_state through plover.qui_qt.utils.WindowState
        '''

        settings.setValue('system_file_map', self._system_file_map)

    def on_config_changed(self, config):
        ''' Updates state based off of the new Plover configuration '''

        # If something unrelated changes like a new dictionary
        # being added then the system name will not be in config
        if 'system_name' not in config:
            return
