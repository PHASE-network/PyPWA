#    PyPWA, a scientific analysis toolkit.
#    Copyright (C) 2016  JLab
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Memory Caching

The objects in this file are dedicated to saving and writing chunks of
memory to file for quick loading when the data is loaded into memory
again.
"""

import io
import logging
import os
import pickle

from PyPWA import VERSION, LICENSE, STATUS
from PyPWA.core import tools

__author__ = ["Mark Jones"]
__credits__ = ["Mark Jones"]
__maintainer__ = ["Mark Jones"]
__email__ = "maj@jlab.org"
__status__ = STATUS
__license__ = LICENSE
__version__ = VERSION


class MemoryCache(object):
    """
    A simple interface object to _WriteCache and _ReadCache.
    """

    @staticmethod
    def write_cache(data, file_location):
        basic_data = _FindBasicInfo(file_location)
        writer = _WriteCache(basic_data)
        writer.write_cache(data)

    @staticmethod
    def read_cache(file_location):
        """
        Raises:
            _cache.CacheError: If the hash has changed, is corrupt, or
                doesn't exist, this error will be raised.
        """
        basic_data = _FindBasicInfo(file_location)
        reader = _ReadCache(basic_data)
        return reader.read_cache()

    @staticmethod
    def delete_cache(file_location):
        basic_data = _FindBasicInfo(file_location)
        os.remove(basic_data.fetch_cache_location)


class _FindBasicInfo(object):
    
    _logger = logging.getLogger(__name__)
    _hash_utility = tools.FileHashString()
    _data_locator = tools.DataLocation()
    _cache_location = ""
    _found_hash = ""
    
    def __init__(self, original_file):
        """
        Finds the hash and cache location for the Cache Module.
        """
        self._setup_basic_cache_data(original_file)
        self._logger.addHandler(logging.NullHandler())

    @property
    def fetch_hash(self):
        return self._found_hash

    @property
    def fetch_cache_location(self):
        return self._cache_location

    def _setup_basic_cache_data(self, original_file):
        self._set_cache_name(original_file)
        self._set_file_hash(original_file)

    def _set_cache_name(self, original_file):
        cache_location = self._get_cache_uri()
        self._set_filename_with_uri(original_file, cache_location)

    def _get_cache_uri(self):
        potential_cache_location = self._data_locator.get_cache_uri()
        self._logger.debug("Found location is %s" % potential_cache_location)
        return potential_cache_location

    def _set_filename_with_uri(self, original_file, found_location):
        beginning_of_uri = "/"
        filename_extension = ".pickle"

        filename_base = os.path.basename(original_file)
        filename_without_extension = filename_base.split(".")[0]

        final_location = (
            found_location + beginning_of_uri +
            filename_without_extension + filename_extension
        )

        self._logger.info("Cache Location set to %s" % final_location)
        self._cache_location = final_location

    def _set_file_hash(self, original_file):
        self._found_hash = self._file_hash(original_file)

        self._logger.info("Found SHA512 hash for %s" % self._cache_location)
        self._logger.debug("File Hash is set to %s" % self._found_hash)

    def _file_hash(self, original_file):
        with io.open(original_file, "rb") as stream:
            return self._hash_utility.get_sha512_hash(stream)


class _ReadCache(object):

    _info_object = _FindBasicInfo
    _packaged_data = {"hash": "", "data": object}
    _logger = logging.getLogger(__name__)

    def __init__(self, basic_info):
        """
        Loads the cache from disk if it exists, will raise CacheError if
        something is wrong with the cache.
        """
        self._logger.addHandler(logging.NullHandler())
        self._info_object = basic_info

    def read_cache(self):
        self._attempt_cache_load()
        return self._packaged_data["data"]

    def _attempt_cache_load(self):
        found_data = self._graciously_load_cache()
        self._if_valid_set_data(found_data)

    def _graciously_load_cache(self):
        self._logger.info(
            "Attempting to load %s" % self._info_object.fetch_cache_location
        )

        try:
            returned_data = self._load_data()
            self._logger.info("Successfully loaded pickle cache!")
        except (OSError, IOError):
            returned_data = self._empty_raw_data
            self._logger.info("No cache exists.")
        except pickle.PickleError as Error:
            returned_data = self._empty_raw_data
            self._logger.info(
                "Pickle is from a different Python version or is damaged."
            )
            self._logger.exception(Error)
        return returned_data

    @property
    def _empty_raw_data(self):
        return {"hash": False, "data": object}

    def _load_data(self):
        with io.open(self._info_object.fetch_cache_location, "rb") as stream:
            return pickle.load(stream)

    def _if_valid_set_data(self, loaded_data):
        if self._check_cache_is_valid(loaded_data):
            self._packaged_data = loaded_data
        else:
            raise CacheError("Cache is invalid.")

    def _check_cache_is_valid(self, loaded_data):
        if loaded_data["hash"] == self._info_object.fetch_hash:
            return self._caches_match()
        elif not loaded_data["hash"]:
            return self._cache_hash_is_false()
        else:
            return self._cache_hash_changed(loaded_data)

    def _caches_match(self):
        self._logger.info("Cache Hashes match!")
        return True

    def _cache_hash_is_false(self):
        self._logger.debug("Cache load failed, hash is false.")
        return False

    def _cache_hash_changed(self, loaded_data):
        self._logger.warning("File hash has changed.")

        self._logger.debug(
            "{0} != {1}".format(
                loaded_data["hash"], self._info_object.fetch_hash
            )
        )

        return False


class _WriteCache(object):

    _packaged_data = {"hash": "", "data": object}
    _logger = logging.getLogger(__name__)
    _info_object = _FindBasicInfo

    def __init__(self, basic_info):
        """
        Writes the cache to disk.
        """
        self._logger.addHandler(logging.NullHandler())
        self._info_object = basic_info

    def write_cache(self, data):
        self._set_packaged_data(data)
        self._write_cache_data()

    def _set_packaged_data(self, data):
        self._packaged_data["hash"] = self._info_object.fetch_hash
        self._packaged_data["data"] = data

    def _write_cache_data(self):
        location = self._info_object.fetch_cache_location

        self._logger.info("Making cache for %s" % location)

        with io.open(location, "wb") as stream:
            pickle.dump(
                self._packaged_data, stream, protocol=pickle.HIGHEST_PROTOCOL
            )


class CacheError(OSError):
    """
    A simple error that is raised whenever something has gone wrong with the
    Cache that is known.
    """
    pass
