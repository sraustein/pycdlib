# Copyright (C) 2015  Chris Lalancette <clalancette@gmail.com>

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation;
# version 2.1 of the License.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

import struct

from pyisoexception import *
from utils import *

class PathTableRecord(object):
    '''
    A class that represents a single ISO9660 Path Table Record.
    '''
    FMT = "=BBLH"

    def __init__(self):
        self.initialized = False

    def parse(self, data):
        '''
        Parse an ISO9660 Path Table Record out of a string.

        Parameters:
         data - The string to parse.
        Returns:
         Nothing.
        '''
        if self.initialized:
            raise PyIsoException("Path Table Record already initialized")

        (self.len_di, self.xattr_length, self.extent_location,
         self.parent_directory_num) = struct.unpack(self.FMT, data[:8])

        if self.len_di % 2 != 0:
            self.directory_identifier = data[8:-1]
        else:
            self.directory_identifier = data[8:]
        self.dirrecord = None
        if self.directory_identifier == '\x00':
            # For the root path table record, it's own directory num is 1
            self.directory_num = 1
        else:
            self.directory_num = self.parent_directory_num + 1
        self.initialized = True

    def _record(self, ext_loc, parent_dir_num):
        '''
        An internal method to generate a string representing this Path Table Record.

        Parameters:
         ext_loc - The extent location to place in this Path Table Record.
         parent_dir_num - The parent directory number to place in this Path Table
                          Record.
        Returns:
         A string representing this Path Table Record.
        '''
        return struct.pack(self.FMT, self.len_di, self.xattr_length,
                           ext_loc, parent_dir_num) + self.directory_identifier + '\x00'*(self.len_di % 2)

    def record_little_endian(self):
        '''
        A method to generate a string representing the little endian version of
        this Path Table Record.

        Parameters:
         None.
        Returns:
         A string representing the little endian version of this Path Table Record.
        '''
        if not self.initialized:
            raise PyIsoException("Path Table Record not yet initialized")

        return self._record(self.extent_location, self.parent_directory_num)

    def record_big_endian(self):
        '''
        A method to generate a string representing the big endian version of
        this Path Table Record.

        Parameters:
         None.
        Returns:
         A string representing the big endian version of this Path Table Record.
        '''
        if not self.initialized:
            raise PyIsoException("Path Table Record not yet initialized")

        return self._record(swab_32bit(self.extent_location),
                            swab_16bit(self.parent_directory_num))

    @classmethod
    def record_length(cls, len_di):
        '''
        A class method to calculate the length of this Path Table Record.
        '''
        # This method can be called even if the object isn't initialized
        return struct.calcsize(cls.FMT) + len_di + (len_di % 2)

    def _new(self, name, dirrecord, parent_dir_num):
        '''
        An internal method to create a new Path Table Record.

        Parameters:
         name - The name for this Path Table Record.
         dirrecord - The directory record to associate with this Path Table Record.
         parent_dir_num - The directory number of the parent of this Path Table
                          Record.
        Returns:
         Nothing.
        '''
        self.len_di = len(name)
        self.xattr_length = 0 # FIXME: we don't support xattr for now
        self.extent_location = 0
        self.parent_directory_num = parent_dir_num
        self.directory_identifier = name
        self.dirrecord = dirrecord
        if self.directory_identifier == '\x00':
            # For the root path table record, it's own directory num is 1
            self.directory_num = 1
        else:
            self.directory_num = self.parent_directory_num + 1
        self.initialized = True

    def new_root(self, dirrecord):
        '''
        A method to create a new root Path Table Record.

        Parameters:
         dirrecord - The directory record to associate with this Path Table Record.
        Returns:
         Nothing.
        '''
        if self.initialized:
            raise PyIsoException("Path Table Record already initialized")

        self._new("\x00", dirrecord, 1)

    def new_dir(self, name, dirrecord, parent_dir_num):
        '''
        A method to create a new Path Table Record.

        Parameters:
         name - The name for this Path Table Record.
         dirrecord - The directory record to associate with this Path Table Record.
         parent_dir_num - The directory number of the parent of this Path Table
                          Record.
        Returns:
         Nothing.
        '''
        if self.initialized:
            raise PyIsoException("Path Table Record already initialized")

        self._new(name, dirrecord, parent_dir_num)

    def set_dirrecord(self, dirrecord):
        '''
        A method to set the directory record associated with this Path Table
        Record.

        Parameters:
         dirrecord - The directory record to associate with this Path Table Record.
        Returns:
         Nothing.
        '''
        if not self.initialized:
            raise PyIsoException("Path Table Record not yet initialized")

        self.dirrecord = dirrecord

    def update_extent_location_from_dirrecord(self):
        '''
        A method to update the extent location for this Path Table Record from
        the corresponding directory record.

        Parameters:
         None.
        Returns:
         Nothing.
        '''
        if not self.initialized:
            raise PyIsoException("Path Table Record not yet initialized")

        self.extent_location = self.dirrecord.extent_location()

    def __lt__(self, other):
        return ptr_lt(self.directory_identifier, other.directory_identifier)