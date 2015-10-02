#!/usr/bin/env python
"""
DataCalc.py: This Caculates the from the General Shell using NumExpr
"""

__author__ = "Mark Jones"
__credits__ = ["Mark Jones", "Josh Pond", "Will Phelps", "Stephanie Bramlett"]
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Mark Jones"
__email__ = "maj@jlab.org"
__status__ = "Beta"

import numpy, multiprocessing, sys

class DataCalc(object):
    """
    This is the object used to calculate data in the arrays for the General Shell using Numexpr
    """
    
    def __init__(self, config ):
        """
        Sets up basic config and checks it for errors
        """
        self.config = config
        self.__preprocessing()
        sys.path.append(self.config["cwd"])
        self.imported = __import__(self.config["Function File"].strip(".py"))

        
    def run(self, *args):
        """
        This is the function is called by minuit and acts as a wrapper for the users function
        Params: 
        Returns: The final value from the likelihood function
        """
        
        the_params = {}
        for parameter, arg in zip(self.parameters, args):
            the_params[parameter] = arg


        users_function = getattr(self.imported, self.config["Function Name"])
        #print the_params
        if self.config["Number of threads"] > 1:
            worker_pool = multiprocessing.Pool(processes=self.config["Number of Threads"])

            jobs = []
            for x in range((self.config["Number of threads"]/2)):
                jobs.append(worker_pool.apply_async(accepted_process, args=(users_function, self.accepted_split[x],the_params, self.processed)))

            for x in range((self.config["Number of threads"]/2)):
                jobs.append(worker_pool.apply_async(data_process, args=(users_function, self.data_split[x], the_params, self.qfactor_split[x])))

            worker_pool.close() #You must close the pool before you can wait until the threads die

            try:
                worker_pool.join()
                final = [completed.get() for completed in jobs ]
                value = numpy.sum(final)
            except KeyboardInterrupt:
                worker_pool.terminate()
                worker_pool.join()
                sys.exit()
        else:
            value = self.__likely_hood_function( users_function(self.kvar_data, the_params), users_function(self.kvar_accepted, the_params), self.qfactor)
            print value
        return value


    def prep_work(self):
        try:
            self.kvar_data.pop("files_hash")
            self.kvar_accepted.pop("files_hash")
        except:
            pass

        if self.config["Number of threads"] > 1:
            self.data_split = []
            self.accepted_split = []
            
            for x in range((self.config["Number of threads"]/2)):
                self.data_split.append({})
                self.accepted_split.append({})

            for key in self.kvar_data:
                for x in range((self.config["Number of threads"]/2)):
                    self.data_split[x][key] = numpy.array_split(self.kvar_data[key],(self.config["Number of threads"]/2))[x]

            for key in self.kvar_accepted:
                for x in range((self.config["Number of threads"]/2)):
                    self.accepted_split[x][key] = numpy.array_split(self.kvar_accepted[key], (self.config["Number of threads"]/2))[x]

            if isinstance(self.qfactor, numpy.ndarray):
                self.qfactor_split = numpy.array_split(self.qfactor, (self.config["Number of threads"]/2))
            else:
                self.qfactor_split = numpy.array_split(numpy.ones(shape=len(self.kvar_data.values()[0]), dtype="float64"), (self.config["Number of threads"]/2))
        else:

            if not isinstance(self.qfactor, numpy.ndarray):
                self.qfactor = numpy.ones(shape=len(self.kvar_data.values()[0]))


    def __preprocessing(self):
        self.processed = (1.0/float(self.config["Generated Length"]))

    def __likely_hood_function(self, array_data, array_accpeted, qfactor):
        return -(numpy.sum(qfactor * numpy.log(array_data))) + ((1/float(self.config["Generated Length"])) * numpy.sum(array_accpeted))
    
def accepted_process(function, array, params, processed):
    values = function(array, params)
    return processed * numpy.sum(values) 

def data_process(function, array, params, qfactor):
    values = function(array, params)
    the_values = numpy.zeros(shape=len(values), dtype="float64")
    for x in range(len(values)):
        the_values[x] = qfactor[x] * numpy.log(values[x])
    return -(numpy.sum(the_values))