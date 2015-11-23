"""
Tools needed for the various Amplitude analysing utilities.
"""
__author__ = "Mark Jones"
__credits__ = ["Mark Jones"]
__license__ = "MIT"
__version__ = "2.0.0"
__maintainer__ = "Mark Jones"
__email__ = "maj@jlab.org"
__status__ = "Beta0"

import iminuit, warnings, sys, numpy

class Minimalizer(object):
    """Object based off of iminuit, provides an easy way to run minimalization
    Args:
        calc_function (object): function that holds the calculations.
        parameters (list): List of the parameters
        settings (dict): Dictionary of the settings for iminuit
        strategy (int): Iminuits strategy
        set_up (int): Todo
        ncall (int): Max number of calls
    """

    def __init__(self, calc_function, parameters, settings, strategy, set_up, ncall):
        self._calc_function = calc_function
        self._parameters = parameters
        self._settings = settings
        self._strategy = strategy
        self._set_up = set_up
        self._ncall = ncall


    def min(self):
        """Method to call to start minimalization process"""
        minimal = iminuit.Minuit(self._calc_function, forced_parameters=self._parameters, **self._settings )
        minimal.set_strategy(self._strategy)
        minimal.set_up(self._set_up)
        minimal.migrad(ncall=self._ncall)


class FunctionLoading(object):
    """Object that loads the user defined functions from file
    Args:
        cwd (str): Path to folder with the functions
        function_location (str): Path to the file
        function_name (str): Name of Amplitude function
        setup_name (str): Name of Setup function.
    """

    def __init__(self, cwd, function_location, function_name, setup_name ):
        self._users_amplitude, self._users_setup = self._import_function(cwd, function_location, function_name, setup_name)


    def _import_function(self, cwd, function_location, function_name, setup_name):
        """Imports and sets up functions for usage.
        Args:
            cwd (str): Path to folder with the functions
            function_location (str): Path to the file
            function_name (str): Name of Amplitude function
            setup_name (str): Name of Setup function.
        Returns:
            list: [ amplitude function, setup function ]
        """
        sys.path.append(cwd)
        try:
            imported = __import__(function_location.strip(".py"))
        except ImportError:
            raise

        try:
            users_amplitude = getattr(imported, function_name)
        except:
            raise

        try:
            setup_function = getattr(imported, setup_name)
        except AttributeError:
            warnings.warn("Setup fucntion {0} was not found in {1}, going without setup function".format(setup_function, function_location ), UserWarning)
            def empty(): pass
            setup_function = empty

        return [ users_amplitude, setup_function ]


    def return_amplitude(self):
        """Retuns amplitude
        Returns:
            object: Amplitude Function
        """
        return self._users_amplitude


    def return_setup(self):
        """Returns setup
        Returns:
            object: Setup Function
        """
        return self._users_setup


class DataSplitter(object):
    """Splits data up depending on time into defined number of chunks"""

    def split(self, data, num_chunks):
        """Entry point for object.
        Args:
            data (object): Data to be split up
            num_chunks (int): Number of chunks to return
        Retuns:
            list: Each index is a chunck of the returned data in order
        """
        if num_chunks == 1:
            return [data]

        if type(data) == dict:
            return self._dictionary_split(data, num_chunks)
        elif type(data) == numpy.ndarray:
            return self._array_split(data, num_chunks)

        return self._split_data


    def _dictionary_split(self, dictionary, num_chunks):
        """Splits dictionary into user defined number of chunks
        Args:
            dictionary (dict): Dictionary of arrays that needs to be split
            num_chunks (int): Number of chunks
        Returns:
            list: Each index is a chunck of the returned data in order
        """
        split_dictionary = []

        for x in range(num_chunks):
            split_dictionary.append({})

        for key in dictionary:
            for index in range(num_chunks):
                split_dictionary[index][key] = numpy.array_split(dictionary[key],(num_chunks))[index]
        return split_dictionary


    def _array_split(self, array, num_chunks):
        """Splits arrays into a list of arrays
        Args:
            array (numpy.ndarray): Array to split
            num_chunks (int): Number of chunks
        Returns:
            list: List of numpy arrays
        """
        return numpy.array_split(array, num_chunks)
