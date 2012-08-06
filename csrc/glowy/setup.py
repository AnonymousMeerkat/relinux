from distutils.core import setup, Extension

module1 = Extension('_glowy',
                    sources = ['main.c'])

setup (name = 'Glowy',
       version = '1.0',
       description = 'Theme for Tkinter',
       ext_modules = [module1])
