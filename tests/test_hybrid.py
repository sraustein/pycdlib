import pytest
import subprocess
import os
import sys
import StringIO
import struct

prefix = '.'
for i in range(0,3):
    if os.path.exists(os.path.join(prefix, 'pyiso.py')):
        sys.path.insert(0, prefix)
        break
    else:
        prefix = '../' + prefix

import pyiso

from common import *

def test_hybrid_twofiles(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    outfile = tmpdir.join("twofile-test.iso")
    indir = tmpdir.mkdir("twofile")
    outfp = open(os.path.join(str(tmpdir), "twofile", "foo"), 'wb')
    outfp.write("foo\n")
    outfp.close()
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now open up the ISO with pyiso and check some things out.
    iso = pyiso.PyIso()
    iso.open(open(str(outfile), 'rb'))

    barstr = "bar\n"
    iso.add_fp(StringIO.StringIO(barstr), len(barstr), "/BAR.;1")

    out = StringIO.StringIO()
    iso.write(out)

    check_twofile(iso, len(out.getvalue()))

def test_hybrid_rmfile(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    outfile = tmpdir.join("twofile-test.iso")
    indir = tmpdir.mkdir("twofile")
    outfp = open(os.path.join(str(tmpdir), "twofile", "foo"), 'wb')
    outfp.write("foo\n")
    outfp.close()
    outfp = open(os.path.join(str(tmpdir), "twofile", "bar"), 'wb')
    outfp.write("bar\n")
    outfp.close()
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now open up the ISO with pyiso and check some things out.
    iso = pyiso.PyIso()
    iso.open(open(str(outfile), 'rb'))

    iso.rm_file("/BAR.;1")

    out = StringIO.StringIO()
    iso.write(out)

    check_onefile(iso, len(out.getvalue()))

def test_hybrid_rmdir(tmpdir):
    # First set things up, and generate the ISO with genisoimage.
    outfile = tmpdir.join("rmdir-test.iso")
    indir = tmpdir.mkdir("rmdir")
    outfp = open(os.path.join(str(tmpdir), "rmdir", "foo"), 'wb')
    outfp.write("foo\n")
    outfp.close()
    tmpdir.mkdir("rmdir/dir1")
    subprocess.call(["genisoimage", "-v", "-v", "-iso-level", "1", "-no-pad",
                     "-o", str(outfile), str(indir)])

    # Now open up the ISO with pyiso and check some things out.
    iso = pyiso.PyIso()
    iso.open(open(str(outfile), 'rb'))

    iso.rm_directory("/DIR1")

    out = StringIO.StringIO()
    iso.write(out)

    check_onefile(iso, len(out.getvalue()))

# FIXME: add a test to test removing all files and directories
# FIXME: add a test to remove a subdirectory
