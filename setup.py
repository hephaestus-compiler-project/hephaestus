import os
import shutil
import glob
from setuptools import setup, find_packages, Command
from pathlib import Path


here = os.path.abspath(os.path.dirname(__file__))


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    CLEAN_FILES = './build ./dist ./*.pyc ./*.tgz ./*.egg-info ./*/__pycache__/'.split(' ')

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        global here

        for path_spec in self.CLEAN_FILES:
            # Make paths absolute and relative to this path
            abs_paths = glob.glob(os.path.normpath(os.path.join(
                here, path_spec)))
            for path in [str(p) for p in abs_paths]:
                if not path.startswith(here):
                    # Die if path in CLEAN_FILES is absolute
                    raise ValueError("%s is not a path inside %s" % (path,
                                                                     here))
                print('removing %s' % os.path.relpath(path))
                shutil.rmtree(path)


setup(
    name='checktypesystems',
    version='0.0.1',
    description='Check Type Systems',
    python_requires='>=3.4, <4',
    setup_requires=['pytest-runner', 'pytest-pylint'],
    tests_require=['pytest', 'mock', 'pylint'],
    packages=['src'],
    packages_dir={'src': 'src'},
    #  entry_points={
    #      'console_scripts': [
    #          'check-type-systems=main',
    #      ],
    #  },
    cmdclass={
        'clean': CleanCommand,
    },
)
