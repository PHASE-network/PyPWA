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

from PyPWA.builtin_plugins.data import data_templates


class GampDataPlugin(data_templates.TemplateDataPlugin):

    @property
    def plugin_name(self):
        return "gamp"

    def get_plugin_memory_parser(self):
        return GampMemory()

    def get_plugin_writer(self, file_location):
        return GampWriter(file_location)

    def get_plugin_reader(self, file_location):
        return GampReader(file_location)

    def get_plugin_read_test(self):
        return GampDataTest()

    @property
    def plugin_supported_extensions(self):
        return [".gamp"]

    @property
    def plugin_supports_gamp_data(self):
        return True

    @property
    def plugin_supports_flat_data(self):
        return False