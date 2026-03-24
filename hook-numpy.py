from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Only collect compiled numpy files, not source files
datas = []
hiddenimports = []

# Collect only essential numpy binaries
binaries = []

# Exclude all numpy source and test files
excludedimports = [
    'numpy.distutils',
    'numpy.f2py', 
    'numpy.testing',
    'numpy.tests',
    'numpy.core.tests',
    'numpy.lib.tests',
    'numpy.ma.tests',
    'numpy.random.tests',
    'numpy.linalg.tests',
    'numpy.fft.tests',
    'numpy.polynomial.tests',
]