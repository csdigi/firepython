# -*- coding: utf-8 -*-
import os
import re
import sys

from paver.easy import *
from paver.setuputils import setup, find_packages

from firepython._setup_common import SETUP_ARGS

ROOT = path('.').abspath()
ADDON = ROOT.parent/'firelogger'
# ^--- firelogger is expected to be at same directory
#      level as firepython project
FIREFOX = ADDON/'firefox'
INSTALL_RDF = FIREFOX/'install.rdf'
BUILD_DIR = ROOT/'build'
DIST_DIR = ROOT/'dist'
FPY = ROOT/'firepython'
FPY_EGG_INFO = ROOT/'FirePython.egg-info'
CRUFT = [
    BUILD_DIR,
    DIST_DIR,
    FPY_EGG_INFO,
    ROOT/'paver-minilib.zip',
]
API_VERSION = re.compile(r'<em:version>([^<]*)<\/em:version>')
PY_API_VERSION_DEF_RE = re.compile('__api_version__ = [\'"][^\'"]+[\'"]')
PY_API_VERSION_DEF = '__api_version__ = \'%s\''


SETUP_ARGS['packages'] = find_packages(exclude=['tests'])
setup(**SETUP_ARGS)


def get_version_from_install_rdf():
    match = API_VERSION.search(INSTALL_RDF.bytes())
    if match:
        return match.groups(1)[0].strip()
    else:
        raise Exception('failed to API determine version from %s'
                        % INSTALL_RDF)


@task
def xpi():
    """Prepare XPI"""
    assert ADDON.exists(), "firepython-addon not found!\n  " \
                           "expected to be in %s" % ADDON
    os.chdir(ADDON)
    sh('rake')


@task
@needs(['sdist'])
def pypi():
    """Update PyPI index and upload library sources"""
    sh('python setup.py register')
    sh('python setup.py sdist --formats=gztar,bztar,zip upload')


@task
def update_api_version():
    """Resets API version in the firepython package base"""
    assert INSTALL_RDF.exists(), \
        "%s not found!, cannot extract version." % INSTALL_RDF

    ver = get_version_from_install_rdf()
    info('found API version %r from %s' % (ver, INSTALL_RDF))
    init = FPY/'__init__.py'
    old_bytes = init.bytes()
    ver_string = PY_API_VERSION_DEF % ver
    new_bytes = PY_API_VERSION_DEF_RE.sub(ver_string, old_bytes)
    if old_bytes != new_bytes:
        init.write_bytes(new_bytes)
    else:
        info('API version is the same, not updating...')


@task
def clean():
    """Clean up generated cruft"""
    for cruft_path in CRUFT:
        if cruft_path.isfile():
            cruft_path.remove()
        elif cruft_path.isdir():
            cruft_path.rmtree()


@task
@needs(['update_api_version', 'minilib', 'distutils.command.sdist'])
def sdist():
    """Combines paver minilib with setuptools' sdist"""
    pass
