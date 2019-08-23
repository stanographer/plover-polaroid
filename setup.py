#!/usr/bin/env python3

__requires__ = '''
plover>=4.0.0.dev2
setuptools>=36.4.0
libusb>=1.0.22b4
escpos>=1.6
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

setup(cmdclass=cmdclass)