Plover Polaroid
===============

This plugin enables Plover users to print "steno Polaroids" by printing stenographic and translated output to a generic thermal receipt tape printer (ESCPOS).

Installation
============

This plugin is not currently on the official Plugin Manager.

1. Clone the repository.
2. cd into directory.
3. `pip3 install . --user --no-cache-dir`
4. Restart Plover.
5. Launch Plover and click on "Polaroid."
6. Check settings, choose mode, and start writing.

* idVendor is the Vendor ID
* VendorID is the Vendor ID
* ProdID is the Product ID
* in_ep is the input end point (default = 0x82) but my printer model takes 0x81
* out_ep is the output end point (default = 0x01) but my printer model takes 0x3

These values can be found out by going into Apple menu => About This Mac => System Report
and finding the printer on the list of USB devices. Should look something like this::


  Product ID:	0x5011
  Vendor ID:	0x0416  (Winbond Electronics Corp.)
  Version:	2.00
  Serial Number:	Printer
  Speed:	Up to 12 Mb/sec
  Manufacturer:	STMicroelectronics
  Location ID:	0x14500000 / 48
  Current Available (mA):	500
  Current Required (mA):	100
  Extra Operating Current (mA):	0

FYI: I'm using the MUNBYN IMP017 58MM Bluetooth Thermal Receipt Printer.
https://www.amazon.com/gp/product/B07N86R5RB/ref=ppx_yo_dt_b_asin_image_o04_s00?ie=UTF8&psc=1

License
=======

This plugin is licensed under GNU General Public License v3 or later (GPLv3+).

Icon made by `Freepik`_ from `www.flaticon.com`_ is licensed by `CC 3.0
BY`_.

.. _Freepik: http://www.freepik.com/
.. _www.flaticon.com: http://www.flaticon.com/
.. _CC 3.0 BY: http://creativecommons.org/licenses/by/3.0/