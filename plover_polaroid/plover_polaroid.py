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
        self.translations = engine._translator.get_state().translations
        self.started = False
        self.printer = None
        
        self._vendor_id.setText(str(hex(self.vendor_id)))
        self._prod_id.setText(str(hex(self.vendor_id)))
        self._in_ep.setText(str(hex(self.in_ep)))
        self._out_ep.setText(str(hex(self.out_ep)))
        self._close.clicked.connect(self.close)
        self._start.clicked.connect(self.start_printer)
        
        self._both_steno_realtime.setChecked(True)
        
        engine.signal_connect('config_changed', self.on_config_changed)
        engine.signal_connect('stroked', self.on_stroke)
        self.on_config_changed(engine.config)

    def start_printer(self, engine: StenoEngine):
        try:
            self._tape.setPlainText("Printer is ready.") 
            self.printer = Usb(
                self.vendor_id,
                self.prod_id,
                0,
                self.in_ep,
                self.out_ep
            )
            
            self.started = True

        except:
           self._tape.setPlainText("Printer is not connected or cannot establish communication.") 

    def on_stroke(self, stroke: Stroke):
        if (self.started):
            raw_steno = ""
            tran_text = ""
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
                
            
            else:
                tran_text = self.translations
                formatter = RetroFormatter(self.translations) or ""
                paragraph = ""
                
                for word in formatter.last_words(-1):
                    paragraph += word
                    
                self._tape.setPlainText(paragraph)
                
                if (word.find("\n" or "\r") > -1):
                    try:
                        self.printer.text(paragraph)
                        self.printer.text("\n")
                        paragraph = ""
                    except:
                        self._tape.setPlainText("Printer is not connected or establish communication.") 
                
                
 
            
    def left_right(self, p, left, right):
        try:
            p.text("{:<20}{:>12}".format(left, right))
            
            self.printer.text("\n")
        except:
            self._tape.setPlainText("Printer is not connected or cannot establish communication.") 
        
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
