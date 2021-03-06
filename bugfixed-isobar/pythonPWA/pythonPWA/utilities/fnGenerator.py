from pythonPWA.utilities.minuitLikelihood import minuitLikelihood
import os

class generator(object):
    def __init__(self):
        self.fileName=None

    def createFile(self,numberOfTerms,inputSeedFile=None):
        """
        Writes out a file containing a wrapper function for minuitLn.calcneglnL,
        simply give this function the number of terms (which should be equivalent to
        2*number of waves) and it will write the needed wrapper function to the file
        specified by self.filename.
        """
        outputFile=open(self.fileName,'w')
        if inputSeedFile==None:        
            outputString="def fn("
            
        if inputSeedFile!=None:
            outputString="import numpy\ndef fn("
            
        
        bufferString=""

        reals=[]
        imags=[]

        totalList=[]

        #make dual lists
        for i in range(0,numberOfTerms,2):
            reals.append("t"+str(i))
        
        for i in range(1,numberOfTerms,2):
            imags.append("t"+str(i))

        for i in range(numberOfTerms):
            totalList.append("t"+str(i))

        for i in range(len(totalList)):
            if i!=len(totalList)-1:
                outputString+="t"+str(i)+","
                
            if i==len(totalList)-1:
                outputString+="t"+str(i)
                
        if inputSeedFile==None:
            outputString+="):\n\tretList=["
        if inputSeedFile!=None:
            outputString+="):\n\tinputSeedList=numpy.load("+inputSeedFile+")\n\tretList=["
        
        #construct numpy complexes
        for i in range(len(reals)):
            if i!=len(reals)-1:
                outputString+="numpy.complex("+reals[i]+","+imags[i]+"),"
            if i==len(reals)-1:
                outputString+="numpy.complex("+reals[i]+","+imags[i]+")"

        outputString+="]\n\treturn minuitLn.calcneglnL(retList)\n\n"
        
        outputFile.write(outputString)
        
        stringBuffer="m=Minuit(fn,"
        for i in range(len(totalList)):
            if i!=len(totalList)-1:
                if inputSeedFile==None:
                    stringBuffer+="t"+str(i)+"=.01,"
                if inputSeedFile!=None:
                    stringBuffer+="t"+str(i)+"=inputSeedList["+i+"],"
                
            if i==len(totalList)-1:
                if inputSeedFile==None:                
                    stringBuffer+="t"+str(i)+"=.01"
                if inputSeedFile!=None:
                    stringBuffer+="t"+str(i)+"=inputSeedList["+i+"]"
                
        stringBuffer+=")\n"

        outputFile.write(stringBuffer)
        """        
        outputFile.write("Vvalues = m.values\n")
        outputFile.write("numpy.save(os.path.join(dataDir,\"Vvalues.npy\"),Vvalues)\n")
        outputFile.write("covariance=numpy.array(m.matrix())\n")
        outputFile.write("numpy.save(os.path.join(dataDir,\"minuitCovar3.npy\"),covariance)\n")
        """
        outputFile.close()
