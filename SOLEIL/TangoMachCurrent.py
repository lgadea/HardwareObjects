<<<<<<< HEAD
from HardwareRepository import HardwareRepository
from HardwareRepository.BaseHardwareObjects import Device

=======
# -*- coding: utf-8 -*-
#$Id: MachCurrent.py,v 1.3 2004/11/23 08:54:06 guijarro Exp guijarro $
from HardwareRepository.BaseHardwareObjects import Device
#from SimpleDevice import SimpleDevice
>>>>>>> Working version of mxCuBE v2.0.2 as of 29th of October
import PyTango
import logging

class TangoMachCurrent(Device):
    def __init__(self, name):
        Device.__init__(self, name)
        self.opmsg = ''
        self.fillmode = ''

    def init(self):
            
        self.device = PyTango.DeviceProxy(self.getProperty("tangoname"))
<<<<<<< HEAD
=======
        self.flux =  PyTango.DeviceProxy('i11-ma-c04/dt/xbpm_diode.1')
        #self.device.timeout = 6000 # Setting timeout to 6 sec
>>>>>>> Working version of mxCuBE v2.0.2 as of 29th of October
        self.setIsReady(True)
        stateChan = self.getChannelObject("current") # utile seulement si statechan n'est pas defini dans le code
        stateChan.connectSignal("update", self.valueChanged)

        #if self.device.imported:
        #    self.setPollCommand('DevReadSigValues')
        #    self.setIsReady(True)

<<<<<<< HEAD
    def updatedValue(self):
        try:
           mach   = self.getCurrent()
           lifetime = self.getLifeTime()
           fillmode = self.getFillMode() + " filling"
           opmsg  = self.getMessage()
           return mach, opmsg, fillmode, lifetime
        except:
           return None

    def getCurrent(self):
        mach = self.device.read_attribute("current").value
        return mach
    def getLifeTime(self):
        lifetime = self.device.read_attribute("lifetime").value
        return lifetime
    def getMessage(self):
        opmsg  = self.device.read_attribute("operatorMessage").value
        return opmsg
    def getFillMode(self):
        fillmode = self.device.read_attribute("fillingMode").value 
        return fillmode

=======
>>>>>>> Working version of mxCuBE v2.0.2 as of 29th of October
    def valueChanged(self, value):
        mach = value
        opmsg = None
        fillmode = None
<<<<<<< HEAD
        lifetime = None
        try:
            lifetime = self.device.read_attribute("lifetime").value
=======
        refill = None
        try:
            refill = self.device.read_attribute("lifetime").value
>>>>>>> Working version of mxCuBE v2.0.2 as of 29th of October
            #opmsg = self.device.DevReadOpMesg() #self.executeCommand('DevReadOpMesg()')
            #opmsg = self.device.read_attribute("message").value
            opmsg = self.device.read_attribute("operatorMessage").value
            opmsg = opmsg.strip()
            opmsg = opmsg.replace(': Faisceau disponible', ':\nFaisceau disponible')
            #' ' #On Gavin's request ;-)
            #fillmode = self.device.DevReadFillMode()
            fillmode = self.device.read_attribute("fillingMode").value + " filling"
            fillmode = fillmode.strip()
<<<<<<< HEAD
            lifetime   = "Lifetime: %3.2f h" % lifetime
            #fillmode += ': ' + opmsg[opmsg.rindex(':') + 2:]
            #logging.getLogger("HWR").info("%s: 000 machinestatus got all info , %s, %s", self.name(), value, opmsg)
=======
            fillmode += ': ' + opmsg[opmsg.rindex(':') + 2:]
>>>>>>> Working version of mxCuBE v2.0.2 as of 29th of October
            
        except AttributeError:
            #self.device.command_inout("Init")
            #self.device.InitDevice()
            #self.device.Init()
<<<<<<< HEAD
            logging.getLogger("HWR").info("%s: AAA AttributeError machinestatus not responding, %s", self.name(), '')
    
        except:
            # Too much error with this Device... stoping the logging (Pierre 22/03/2010).
            logging.getLogger("HWR").error("%s: BBB machinestatus not responding, %s", self.name(), '')
=======
            logging.getLogger("HWR").error("%s: AAA AttributeError machinestatus not responding, %s", self.name(), '')
    
        except:
            # Too much error with this Device... stoping the logging (Pierre 22/03/2010).
            #logging.getLogger("HWR").error("%s: BBB machinestatus not responding, %s", self.name(), '')
>>>>>>> Working version of mxCuBE v2.0.2 as of 29th of October
            pass
        
        if opmsg and opmsg != self.opmsg:
            self.opmsg = opmsg
            logging.getLogger('HWR').info("<b>"+self.opmsg+"</b>")
        
<<<<<<< HEAD
        #opmsg = 'Flux: ' + str(round(self.flux.intensity, 3)) + ' uA' #MS. 29.01.13 ugly hack to have flux in the output instead of opmsg
        #logging.getLogger("HWR").info("%s: CCC machinestatus emitting info to listener, %s, %s, %s, %s", self.name(), value, opmsg, fillmode, lifetime)
        self.emit('valueChanged', (mach, str(opmsg), str(fillmode), str(lifetime)))

def test():
    import os
    hwr_directory = os.environ["XML_FILES_PATH"]

    hwr = HardwareRepository.HardwareRepository(os.path.abspath(hwr_directory))
    hwr.connect()

    conn = hwr.getHardwareObject("/mach")

    print "Machine current is ", conn.getCurrent()
    print "Life time is ", conn.getLifeTime()
    print "Fill mode is ", conn.getFillMode()
    print "Message is ", conn.getMessage()


if __name__ == '__main__':
   test()
=======
        opmsg = 'Flux: ' + str(round(self.flux.intensity, 3)) + ' uA' #MS. 29.01.13 ugly hack to have flux in the output instead of opmsg
        self.emit('valueChanged', (mach, opmsg, fillmode, opmsg))
>>>>>>> Working version of mxCuBE v2.0.2 as of 29th of October

