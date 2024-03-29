#!/usr/bin/env python3

__requires__ = '''
PyQt5
python-escpos
hidapi
plover>=4.0.0.dev2
pyusb
Pillow
libusb
setuptools>=36.4.0
'''


from setuptools import setup

setup()

from plover_build_utils.setup import BuildPy, BuildUi, Test

BuildPy.build_dependencies.append('build_ui')
BuildUi.hooks = ['plover_build_utils.pyqt:fix_icons']
cmdclass = {
    'build_py': BuildPy,
    'build_ui': BuildUi,
}

setup(cmdclass=cmdclass, install_requires=['plover', 'PyQt5', 'escpos'])