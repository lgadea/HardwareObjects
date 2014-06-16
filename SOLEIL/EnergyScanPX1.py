from qt import *
from HardwareRepository.BaseHardwareObjects import Equipment
from HardwareRepository.TaskUtils import *
import logging
import PyChooch
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
import os
import time
import types
import math
import gevent

<<<<<<< HEAD:SOLEIL/EnergyScanPX1.py
class EnergyScanPX1(Equipment):    
    MANDATORY_HO={"BLEnergy":"BLEnergy"}
    
    
=======
class EnergyScan(Equipment):
>>>>>>>  	modified:   HardwareObjects/EnergyScan.py:EnergyScan.py
    def init(self):
        self.ready_event = gevent.event.Event()
        self.scanning = None
<<<<<<< HEAD:SOLEIL/EnergyScanPX1.py
#        self.moving = None
        self.scanThread = None
        self.pk = None
        self.ip = None
        self.roiwidth = 0.35 # en keV largeur de la roi 
        self.before = 0.10  #  en keV Ecart par rapport au seuil pour le point de depart du scan
        self.after = 0.20   # en keV Ecart par rapport au seuil pour le dernier point du scan
        self.canScan = True
        self.nbsteps = 100 #
        self.integrationtime = 5.0
        self.directoryPrefix = None

        self.directoryPrefix=self.getProperty("directoryprefix")
        if self.directoryPrefix is None:
            logging.getLogger("HWR").error("EnergyScan: you must specify the directory prefix property")
        else :
            logging.getLogger("HWR").info("EnergyScan: directoryPrefix : %s" %(self.directoryPrefix))
            
                    # Load mandatory hardware objects
#         for ho in EnergyScan.MANDATORY_HO:
#             desc=EnergyScan.MANDATORY_HO[ho]
#             name=self.getProperty(ho)
#             if name is None:
#                  logging.getLogger("HWR").error('EnergyScan: you must specify the %s hardware object' % desc)
#                  hobj=None
#                  self.configOk=False
#             else:
#                  hobj=HardwareRepository.HardwareRepository().getHardwareObject(name)
#                  if hobj is None:
#                      logging.getLogger("HWR").error('EnergyScan: invalid %s hardware object' % desc)
#                      self.configOk=False
#             exec("self.%sHO=hobj" % ho)
# 
#         print "BLEnergyHO : ", self.BLEnergyHO
        
        paramscan = self["scan"]   
        self.roiwidth = paramscan.roiwidth
        self.before = paramscan.before
        self.after = paramscan.after
        self.nbsteps = paramscan.nbsteps
        self.integrationTime = paramscan.integrationtime
      
      
        print "self.roiwidth :", self.roiwidth
        print "self.before :", self.before
        print "self.after :", self.after
        print "self.nbsteps :", self.nbsteps
        print "self.integrationtime :", self.integrationtime
        
=======
        self.moving = None
        self.energyMotor = None
        self.energyScanArgs = None
        self.archive_prefix = None
        self.energy2WavelengthConstant=None
        self.defaultWavelength=None
        self._element = None
        self._edge = None
        try:
            self.defaultWavelengthChannel=self.getChannelObject('default_wavelength')
        except KeyError:
            self.defaultWavelengthChannel=None
        else:
            self.defaultWavelengthChannel.connectSignal("connected", self.sConnected)
            self.defaultWavelengthChannel.connectSignal("disconnected", self.sDisconnected)
>>>>>>>  	modified:   HardwareObjects/EnergyScan.py:EnergyScan.py

        if self.defaultWavelengthChannel is None:
            #MAD beamline
            try:
                self.energyScanArgs=self.getChannelObject('escan_args')
            except KeyError:
                logging.getLogger("HWR").warning('EnergyScan: error initializing energy scan arguments (missing channel)')
                self.energyScanArgs=None

            try:
                self.scanStatusMessage=self.getChannelObject('scanStatusMsg')
            except KeyError:
                self.scanStatusMessage=None
                logging.getLogger("HWR").warning('EnergyScan: energy messages will not appear (missing channel)')
            else:
                self.connect(self.scanStatusMessage,'update',self.scanStatusChanged)

<<<<<<< HEAD:SOLEIL/EnergyScanPX1.py
        try:
            self.bstdevice = DeviceProxy(self.getProperty("bst")) #, verbose=False)
            self.bstdevice.timeout = 2000
        except :    
            logging.getLogger("HWR").error("%s not found" %(self.getProperty("bst")))
            self.canScan = False
=======
            try:
                self.doEnergyScan.connectSignal('commandReplyArrived', self.scanCommandFinished)
                self.doEnergyScan.connectSignal('commandBeginWaitReply', self.scanCommandStarted)
                self.doEnergyScan.connectSignal('commandFailed', self.scanCommandFailed)
                self.doEnergyScan.connectSignal('commandAborted', self.scanCommandAborted)
                self.doEnergyScan.connectSignal('commandReady', self.scanCommandReady)
                self.doEnergyScan.connectSignal('commandNotReady', self.scanCommandNotReady)
            except AttributeError,diag:
                logging.getLogger("HWR").warning('EnergyScan: error initializing energy scan (%s)' % str(diag))
                self.doEnergyScan=None
            else:
                self.doEnergyScan.connectSignal("connected", self.sConnected)
                self.doEnergyScan.connectSignal("disconnected", self.sDisconnected)

            self.energyMotor=self.getObjectByRole("energy")
            self.resolutionMotor=self.getObjectByRole("resolution")
            self.previousResolution=None
            self.lastResolution=None
>>>>>>>  	modified:   HardwareObjects/EnergyScan.py:EnergyScan.py

            self.dbConnection=self.getObjectByRole("dbserver")
            if self.dbConnection is None:
                logging.getLogger("HWR").warning('EnergyScan: you should specify the database hardware object')
            self.scanInfo=None

            self.transmissionHO=self.getObjectByRole("transmission")
            if self.transmissionHO is None:
                logging.getLogger("HWR").warning('EnergyScan: you should specify the transmission hardware object')

            self.cryostreamHO=self.getObjectByRole("cryostream")
            if self.cryostreamHO is None:
                logging.getLogger("HWR").warning('EnergyScan: you should specify the cryo stream hardware object')

            self.machcurrentHO=self.getObjectByRole("machcurrent")
            if self.machcurrentHO is None:
                logging.getLogger("HWR").warning('EnergyScan: you should specify the machine current hardware object')

            self.fluodetectorHO=self.getObjectByRole("fluodetector")
            if self.fluodetectorHO is None:
                logging.getLogger("HWR").warning('EnergyScan: you should specify the fluorescence detector hardware object')

            try:
                #self.moveEnergy.connectSignal('commandReplyArrived', self.moveEnergyCmdFinished)
                #self.moveEnergy.connectSignal('commandBeginWaitReply', self.moveEnergyCmdStarted)
                #self.moveEnergy.connectSignal('commandFailed', self.moveEnergyCmdFailed)
                #self.moveEnergy.connectSignal('commandAborted', self.moveEnergyCmdAborted)
                self.moveEnergy.connectSignal('commandReady', self.moveEnergyCmdReady)
                self.moveEnergy.connectSignal('commandNotReady', self.moveEnergyCmdNotReady)
            except AttributeError,diag:
                logging.getLogger("HWR").warning('EnergyScan: error initializing move energy (%s)' % str(diag))
                self.moveEnergy=None

            if self.energyMotor is not None:
                self.energyMotor.connect('positionChanged', self.energyPositionChanged)
                self.energyMotor.connect('stateChanged', self.energyStateChanged)
                self.energyMotor.connect('limitsChanged', self.energyLimitsChanged)
            if self.resolutionMotor is None:
                logging.getLogger("HWR").warning('EnergyScan: no resolution motor (unable to restore it after moving the energy)')
            else:
                self.resolutionMotor.connect('positionChanged', self.resolutionPositionChanged)

        try:
<<<<<<< HEAD:SOLEIL/EnergyScanPX1.py
            self.fastshutterdevice = DeviceProxy(self.getProperty("fastshutter")) #, verbose=False)
            self.fastshutterdevice.timeout = 2000
        except :    
            logging.getLogger("HWR").error("%s not found" %(self.getProperty("fastshutter")))
            self.canScan = False
        
                            
    def isConnected(self):
        return self.isSpecConnected()
=======
            self.energy2WavelengthChannel=self.getChannelObject('hc_over_e')
        except KeyError:
            self.energy2WavelengthChannel=None
        if self.energy2WavelengthChannel is None:
            logging.getLogger("HWR").error('EnergyScan: error initializing energy-wavelength constant (missing channel)')

        self.thEdgeThreshold = self.getProperty("theoritical_edge_threshold")
        if self.thEdgeThreshold is None:
           self.thEdgeThreshold = 0.01
>>>>>>>  	modified:   HardwareObjects/EnergyScan.py:EnergyScan.py
        
        if self.isConnected():
           self.sConnected()


    def isConnected(self):
        if self.defaultWavelengthChannel is not None:
          # single wavelength beamline
          try:
            return self.defaultWavelengthChannel.isConnected()
          except:
            return False
        else:
          try:
            return self.doEnergyScan.isConnected()
          except:
            return False

    def resolutionPositionChanged(self,res):
        self.lastResolution=res

    def energyStateChanged(self, state):
        if state == self.energyMotor.READY:
          if self.resolutionMotor is not None:
            self.resolutionMotor.dist2res()
    
    # Handler for spec connection
    def sConnected(self):
        if self.energy2WavelengthChannel is not None and self.energy2WavelengthConstant is None:
            try:
                self.energy2WavelengthConstant=float(self.energy2WavelengthChannel.getValue())
            except:
                logging.getLogger("HWR").exception('EnergyScan: error initializing energy-wavelength constant')

        if self.defaultWavelengthChannel is not None and self.defaultWavelength is None:
            try:
                val=self.defaultWavelengthChannel.getValue()
            except:
                logging.getLogger("HWR").exception('EnergyScan: error getting default wavelength')
            else:
                try:
                    self.defaultWavelength=float(val)
                except:
                    logging.getLogger("HWR").exception('EnergyScan: error getting default wavelength (%s)')
                else:
                    logging.getLogger("HWR").debug('EnergyScan: default wavelength is %f' % self.defaultWavelength)

        self.emit('connected', ())

    # Handler for spec disconnection
    def sDisconnected(self):
        self.emit('disconnected', ())

    # Energy scan commands
    def canScanEnergy(self):
<<<<<<< HEAD:SOLEIL/EnergyScanPX1.py
        logging.getLogger("HWR").debug('EnergyScan:canScanEnergy : %s' %(str(self.canScan)))
        return self.canScan

 
#        return self.doEnergyScan is not None
	
    def startEnergyScan(self, 
                        element, 
                        edge, 
                        directory, 
                        prefix, 
                        session_id = None, 
                        blsample_id = None):
        
        logging.getLogger("HWR").debug('EnergyScan:startEnergyScan')
        print 'edge', edge
        print 'element', element
        print 'directory', directory
        print 'prefix', prefix
        #logging.getLogger("HWR").debug('EnergyScan:edge', edge)
        #logging.getLogger("HWR").debug('EnergyScan:element', element)
        #logging.getLogger("HWR").debug('EnergyScan:directory', directory)
        #logging.getLogger("HWR").debug('EnergyScan:prefix', prefix)
        #logging.getLogger("HWR").debug('EnergyScan:edge', edge)
        self.scanInfo={"sessionId":session_id,
                       "blSampleId":blsample_id,
                       "element":element,
                       "edgeEnergy":edge}
#        if self.fluodetectorHO is not None:
#            self.scanInfo['fluorescenceDetector']=self.fluodetectorHO.userName()
=======
        if not self.isConnected():
            return False
        if self.energy2WavelengthConstant is None or self.energyScanArgs is None:
            return False
        return self.doEnergyScan is not None
    def startEnergyScan(self,element,edge,directory,prefix,session_id=None,blsample_id=None):
        self._element = element
        self._edge = edge
        self.scanInfo={"sessionId":session_id,"blSampleId":blsample_id,"element":element,"edgeEnergy":edge}
        if self.fluodetectorHO is not None:
            self.scanInfo['fluorescenceDetector']=self.fluodetectorHO.userName()
>>>>>>>  	modified:   HardwareObjects/EnergyScan.py:EnergyScan.py
        if not os.path.isdir(directory):
            logging.getLogger("HWR").debug("EnergyScan: creating directory %s" % directory)
            try:
                os.makedirs(directory)
            except OSError,diag:
                logging.getLogger("HWR").error("EnergyScan: error creating directory %s (%s)" % (directory,str(diag)))
                self.emit('scanStatusChanged', ("Error creating directory",))
                return False
        try:
            curr=self.energyScanArgs.getValue()
        except:
            logging.getLogger("HWR").exception('EnergyScan: error getting energy scan parameters')
            self.emit('scanStatusChanged', ("Error getting energy scan parameters",))
            return False
        try:
            curr["escan_dir"]=directory
            curr["escan_prefix"]=prefix
        except TypeError:
            curr={}
            curr["escan_dir"]=directory
            curr["escan_prefix"]=prefix

        self.archive_prefix = prefix

        try:
            self.energyScanArgs.setValue(curr)
        except:
            logging.getLogger("HWR").exception('EnergyScan: error setting energy scan parameters')
            self.emit('scanStatusChanged', ("Error setting energy scan parameters",))
            return False
        try:
            self.doEnergyScan("%s %s" % (element,edge))
        except:
            logging.getLogger("HWR").error('EnergyScan: problem calling spec macro')
            self.emit('scanStatusChanged', ("Error problem spec macro",))
            return False
        return True
    def cancelEnergyScan(self, *args):
        if self.scanning:
            self.doEnergyScan.abort()
            self.ready_event.set()
    def scanCommandReady(self):
        if not self.scanning:
            self.emit('energyScanReady', (True,))
    def scanCommandNotReady(self):
        if not self.scanning:
            self.emit('energyScanReady', (False,))
    def scanCommandStarted(self, *args):
        self.scanInfo['startTime']=time.strftime("%Y-%m-%d %H:%M:%S")
        self.scanning = True
        self.emit('energyScanStarted', ())
    def scanCommandFailed(self, *args):
        self.scanInfo['endTime']=time.strftime("%Y-%m-%d %H:%M:%S")
        self.scanning = False
        self.storeEnergyScan()
        self.emit('energyScanFailed', ())
        self.ready_event.set()
    def scanCommandAborted(self, *args):
        self.emit('energyScanFailed', ())
        self.ready_event.set()
    def scanCommandFinished(self,result, *args):
        with cleanup(self.ready_event.set):
            self.scanInfo['endTime']=time.strftime("%Y-%m-%d %H:%M:%S")
            logging.getLogger("HWR").debug("EnergyScan: energy scan result is %s" % result)
            self.scanning = False
            if result==-1:
                self.storeEnergyScan()
                self.emit('energyScanFailed', ())
                return

            try:
              t = float(result["transmissionFactor"])
            except:
              pass
            else:
              self.scanInfo["transmissionFactor"]=t
            try:
                et=float(result['exposureTime'])
            except:
                pass
            else:
                self.scanInfo["exposureTime"]=et
            try:
                se=float(result['startEnergy'])
            except:
                pass
            else:
                self.scanInfo["startEnergy"]=se
            try:
                ee=float(result['endEnergy'])
            except:
                pass
            else:
                self.scanInfo["endEnergy"]=ee

            try:
                bsX=float(result['beamSizeHorizontal'])
            except:
                pass
            else:
                self.scanInfo["beamSizeHorizontal"]=bsX

            try:
                bsY=float(result['beamSizeVertical'])
            except:
                pass
            else:
                self.scanInfo["beamSizeVertical"]=bsY

            try:
                self.thEdge=float(result['theoreticalEdge'])/1000.0
            except:
                pass

            self.emit('energyScanFinished', (self.scanInfo,))


    def doChooch(self, scanObject, elt, edge, scanArchiveFilePrefix, scanFilePrefix):
        symbol = "_".join((elt, edge))
        scanArchiveFilePrefix = "_".join((scanArchiveFilePrefix, symbol))

        i = 1
        while os.path.isfile(os.path.extsep.join((scanArchiveFilePrefix + str(i), "raw"))):
            i = i + 1

        scanArchiveFilePrefix = scanArchiveFilePrefix + str(i)
        archiveRawScanFile=os.path.extsep.join((scanArchiveFilePrefix, "raw"))
        rawScanFile=os.path.extsep.join((scanFilePrefix, "raw"))
        scanFile=os.path.extsep.join((scanFilePrefix, "efs"))

        if not os.path.exists(os.path.dirname(scanArchiveFilePrefix)):
            os.makedirs(os.path.dirname(scanArchiveFilePrefix))
        
        try:
            f=open(rawScanFile, "w")
            pyarch_f=open(archiveRawScanFile, "w")
        except:
            logging.getLogger("HWR").exception("could not create raw scan files")
            self.storeEnergyScan()
            self.emit("energyScanFailed", ())
            return
        else:
            scanData = []
            
            if scanObject is None:
                raw_data_file = os.path.join(os.path.dirname(scanFilePrefix), 'data.raw')
                try:
                    raw_file = open(raw_data_file, 'r')
                except:
                    self.storeEnergyScan()
                    self.emit("energyScanFailed", ())
                    return
                
                for line in raw_file.readlines()[2:]:
                    (x, y) = line.split('\t')
                    x = float(x.strip())
                    y = float(y.strip())
                    x = x < 1000 and x*1000.0 or x
                    scanData.append((x, y))
                    f.write("%f,%f\r\n" % (x, y))
                    pyarch_f.write("%f,%f\r\n"% (x, y))
            else:
                for i in range(len(scanObject.x)):
                    x = float(scanObject.x[i])
                    x = x < 1000 and x*1000.0 or x
                    y = float(scanObject.y[i])
                    scanData.append((x, y))
                    f.write("%f,%f\r\n" % (x, y))
                    pyarch_f.write("%f,%f\r\n"% (x, y))

            f.close()
            pyarch_f.close()
            self.scanInfo["scanFileFullPath"]=str(archiveRawScanFile)

        pk, fppPeak, fpPeak, ip, fppInfl, fpInfl, chooch_graph_data = PyChooch.calc(scanData, elt, edge, scanFile)
        rm=(pk+30)/1000.0
        pk=pk/1000.0
        savpk = pk
        ip=ip/1000.0
        comm = ""
        logging.getLogger("HWR").info("th. Edge %s ; chooch results are pk=%f, ip=%f, rm=%f" % (self.thEdge, pk,ip,rm))

        if math.fabs(self.thEdge - ip) > self.thEdgeThreshold:
          pk = 0
          ip = 0
          rm = self.thEdge + 0.03
          comm = 'Calculated peak (%f) is more that 10eV away from the theoretical value (%f). Please check your scan' % (savpk, self.thEdge)
   
          logging.getLogger("HWR").warning('EnergyScan: calculated peak (%f) is more that 20eV %s the theoretical value (%f). Please check your scan and choose the energies manually' % (savpk, (self.thEdge - ip) > 0.02 and "below" or "above", self.thEdge))

        archiveEfsFile=os.path.extsep.join((scanArchiveFilePrefix, "efs"))
        try:
          fi=open(scanFile)
          fo=open(archiveEfsFile, "w")
        except:
          self.storeEnergyScan()
          self.emit("energyScanFailed", ())
          return
        else:
          fo.write(fi.read())
          fi.close()
          fo.close()

        self.scanInfo["peakEnergy"]=pk
        self.scanInfo["inflectionEnergy"]=ip
        self.scanInfo["remoteEnergy"]=rm
        self.scanInfo["peakFPrime"]=fpPeak
        self.scanInfo["peakFDoublePrime"]=fppPeak
        self.scanInfo["inflectionFPrime"]=fpInfl
        self.scanInfo["inflectionFDoublePrime"]=fppInfl
        self.scanInfo["comments"] = comm

        chooch_graph_x, chooch_graph_y1, chooch_graph_y2 = zip(*chooch_graph_data)
        chooch_graph_x = list(chooch_graph_x)
        for i in range(len(chooch_graph_x)):
          chooch_graph_x[i]=chooch_graph_x[i]/1000.0

        logging.getLogger("HWR").info("<chooch> Saving png" )
        # prepare to save png files
        title="%10s %6s %6s\n%10s %6.2f %6.2f\n%10s %6.2f %6.2f" % ("energy", "f'", "f''", pk, fpPeak, fppPeak, ip, fpInfl, fppInfl)
        fig=Figure(figsize=(15, 11))
        ax=fig.add_subplot(211)
        ax.set_title("%s\n%s" % (scanFile, title))
        ax.grid(True)
        ax.plot(*(zip(*scanData)), **{"color":'black'})
        ax.set_xlabel("Energy")
        ax.set_ylabel("MCA counts")
        ax2=fig.add_subplot(212)
        ax2.grid(True)
        ax2.set_xlabel("Energy")
        ax2.set_ylabel("")
        handles = []
        handles.append(ax2.plot(chooch_graph_x, chooch_graph_y1, color='blue'))
        handles.append(ax2.plot(chooch_graph_x, chooch_graph_y2, color='red'))
        canvas=FigureCanvasAgg(fig)

        escan_png = os.path.extsep.join((scanFilePrefix, "png"))
        escan_archivepng = os.path.extsep.join((scanArchiveFilePrefix, "png"))
        self.scanInfo["jpegChoochFileFullPath"]=str(escan_archivepng)
        try:
          logging.getLogger("HWR").info("Rendering energy scan and Chooch graphs to PNG file : %s", escan_png)
          canvas.print_figure(escan_png, dpi=80)
        except:
          logging.getLogger("HWR").exception("could not print figure")
        try:
          logging.getLogger("HWR").info("Saving energy scan to archive directory for ISPyB : %s", escan_archivepng)
          canvas.print_figure(escan_archivepng, dpi=80)
        except:
          logging.getLogger("HWR").exception("could not save figure")

        self.storeEnergyScan()
        self.scanInfo=None

        logging.getLogger("HWR").info("<chooch> returning" )
        self.emit('chooch_finished', (pk, fppPeak, fpPeak, ip, fppInfl, fpInfl, rm, chooch_graph_x, chooch_graph_y1, chooch_graph_y2, title))
        return pk, fppPeak, fpPeak, ip, fppInfl, fpInfl, rm, chooch_graph_x, chooch_graph_y1, chooch_graph_y2, title

    def scanStatusChanged(self,status):
        self.emit('scanStatusChanged', (status,))
    def storeEnergyScan(self):
        if self.dbConnection is None:
            return
        try:
            session_id=int(self.scanInfo['sessionId'])
        except:
            return
        gevent.spawn(StoreEnergyScanThread, self.dbConnection,self.scanInfo)
        #self.storeScanThread.start()

    def updateEnergyScan(self,scan_id,jpeg_scan_filename):
        pass

    # Move energy commands
    def canMoveEnergy(self):
        return self.canScanEnergy()
    
    def getCurrentEnergy(self):
        if self.energyMotor is not None:
            try:
                return self.energyMotor.getPosition()
            except:
                logging.getLogger("HWR").exception("EnergyScan: couldn't read energy")
                return None
        elif self.energy2WavelengthConstant is not None and self.defaultWavelength is not None:
            return self.energy2wavelength(self.defaultWavelength)
        return None


    def get_value(self):
        return self.getCurrentEnergy()
    
    
    def getEnergyLimits(self):
        lims=None
        if self.energyMotor is not None:
            if self.energyMotor.isReady():
                lims=self.energyMotor.getLimits()
        return lims
    def getCurrentWavelength(self):
        if self.energyMotor is not None:
            try:
                return self.energy2wavelength(self.energyMotor.getPosition())
            except:
                logging.getLogger("HWR").exception("EnergyScan: couldn't read energy")
                return None
        else:
            return self.defaultWavelength
    def getWavelengthLimits(self):
        lims=None
        if self.energyMotor is not None:
            if self.energyMotor.isReady():
                energy_lims=self.energyMotor.getLimits()
                lims=(self.energy2wavelength(energy_lims[1]),self.energy2wavelength(energy_lims[0]))
                if lims[0] is None or lims[1] is None:
                    lims=None
        return lims
    
    def startMoveEnergy(self,value,wait=True):
        logging.getLogger("HWR").info("Moving energy to (%s)" % value)
        try:
            value=float(value)
        except (TypeError,ValueError),diag:
            logging.getLogger("HWR").error("EnergyScan: invalid energy (%s)" % value)
            return False

        try:
            curr_energy=self.energyMotor.getPosition()
        except:
            logging.getLogger("HWR").exception("EnergyScan: couldn't get current energy")
            curr_energy=None

        if value!=curr_energy:
            logging.getLogger("HWR").info("Moving energy: checking limits")
            try:
                lims=self.energyMotor.getLimits()
            except:
                logging.getLogger("HWR").exception("EnergyScan: couldn't get energy limits")
                in_limits=False
            else:
                in_limits=value>=lims[0] and value<=lims[1]
                
            if in_limits:
                logging.getLogger("HWR").info("Moving energy: limits ok")
                self.previousResolution=None
                if self.resolutionMotor is not None:
                    try:
                        self.previousResolution=self.resolutionMotor.getPosition()
                    except:
                        logging.getLogger("HWR").exception("EnergyScan: couldn't get current resolution")
                self.moveEnergyCmdStarted()
                def change_egy():
                    try:
                        self.moveEnergy(value, wait=True)
                    except:
                        self.moveEnergyCmdFailed()
                    else:
                        self.moveEnergyCmdFinished(True)
                if wait:
                    change_egy()
                else:
                    gevent.spawn(change_egy)
            else:
                logging.getLogger("HWR").error("EnergyScan: energy (%f) out of limits (%s)" % (value,lims))
                return False
        else:
            return None

        return True
    def startMoveWavelength(self,value, wait=True):
        energy_val=self.energy2wavelength(value)
        if energy_val is None:
            logging.getLogger("HWR").error("EnergyScan: unable to convert wavelength to energy")
            return False
        return self.startMoveEnergy(energy_val, wait)
    def cancelMoveEnergy(self):
        self.moveEnergy.abort()
    def energy2wavelength(self,val):
        if self.energy2WavelengthConstant is None:
            return None
        try:
            other_val=self.energy2WavelengthConstant/val
        except ZeroDivisionError:
            other_val=None
        return other_val
    def energyPositionChanged(self,pos):
        wav=self.energy2wavelength(pos)
        if wav is not None:
            self.emit('energyChanged', (pos,wav))
            self.emit('valueChanged', (pos, ))
    def energyLimitsChanged(self,limits):
        self.emit('energyLimitsChanged', (limits,))
        wav_limits=(self.energy2wavelength(limits[1]),self.energy2wavelength(limits[0]))
        if wav_limits[0]!=None and wav_limits[1]!=None:
            self.emit('wavelengthLimitsChanged', (wav_limits,))
        else:
            self.emit('wavelengthLimitsChanged', (None,))
    def moveEnergyCmdReady(self):
        if not self.moving:
            self.emit('moveEnergyReady', (True,))
    def moveEnergyCmdNotReady(self):
        if not self.moving:
            self.emit('moveEnergyReady', (False,))
    def moveEnergyCmdStarted(self):
        self.moving = True
        self.emit('moveEnergyStarted', ())
    def moveEnergyCmdFailed(self):
        self.moving = False
        self.emit('moveEnergyFailed', ())
    def moveEnergyCmdAborted(self):
        pass
        #self.moving = False
        #self.emit('moveEnergyFailed', ())
    def moveEnergyCmdFinished(self,result):
        self.moving = False
        self.emit('moveEnergyFinished', ())

    def getPreviousResolution(self):
        return (self.previousResolution,self.lastResolution)

    def restoreResolution(self):
        if self.resolutionMotor is not None:
            if self.previousResolution is not None:
                try:
                    self.resolutionMotor.move(self.previousResolution)
                except:
                    return (False,"Error trying to move the detector")
                else:
                    return (True,None)
            else:
                return (False,"Unknown previous resolution")
        else:
            return (False,"Resolution motor not defined")

    # Elements commands
    def getElements(self):
        elements=[]
        try:
            for el in self["elements"]:
                elements.append({"symbol":el.symbol, "energy":el.energy})
        except IndexError:
            pass
        return elements

    # Mad energies commands
    def getDefaultMadEnergies(self):
        energies=[]
        try:
            for el in self["mad"]:
                energies.append([float(el.energy), el.directory])
        except IndexError:
            pass
        return energies

def StoreEnergyScanThread(db_conn, scan_info):
    scanInfo = dict(scan_info)
    dbConnection = db_conn
    
<<<<<<< HEAD:SOLEIL/EnergyScanPX1.py
    def newScan(self,scanParameters):
        logging.getLogger("HWR").debug('EnergyScan:newScan')
        self.emit('newScan', (scanParameters,))
        
    def startMoveEnergy(self, value):   # Copie du code ecrit dans BLEnergy.py pour gestion du backlash onduleur.
   
        # MODIFICATION DE CETTE FONCTION POUR COMPENSER LE PROBLEME D'HYSTERESIS DE L"ONDULEUR
        # PAR CETTE METHODE ON APPLIQUE TOUJOURS UN GAP CROISSANT
        backlash = 0.1 # en mmte
        gaplimite = 5.5  # en mm
        self.doBacklashCompensation = False # True #MS 2013-05-21
#        self.mono_mt_rx_device.On()
        #time.sleep(5)
        
        if (str(self.BLEnergydevice.State()) != "MOVING") :# MS .State -> .State() 06.03.2013
            if self.doBacklashCompensation :
                try : 
                    # Recuperation de la valeur de gap correspondant a l'energie souhaitee
                    self.U20Energydevice.autoApplyComputedParameters = False
                    self.U20Energydevice.energy = value
                    newgap = self.U20Energydevice.computedGap
                    actualgap = self.U20Energydevice.gap

                    self.U20Energydevice.autoApplyComputedParameters = True
                
                    # On applique le backlash que si on doit descendre en gap	    
                    if newgap < actualgap + backlash:
                        # Envoi a un gap juste en dessous (backlash)    
                        if newgap-backlash > gaplimite :
                            self.U20Energydevice.gap = newgap - backlash
                        else :
                            self.U20Energydevice.gap = gaplimite
                            self.U20Energydevice.gap = newgap + backlash
                        time.sleep(1)
                except :           
                    logging.getLogger("HWR").error("%s: Cannot move undulator U20 : State device = %s", self.name(), self.U20Energydevice.State())

            try :
                # Envoi a l'energie desiree    
                self.BLEnergydevice.energy = value
            except :           
                logging.getLogger("HWR").error("%s: Cannot move BLEnergy : State device = %s", self.name(), self.BLEnergydevice.State())
        
        else : 
            statusBLEnergydevice = self.BLEnergydevice.Status()
            logging.getLogger("HWR").error("%s: Cannot move : State device = %s", self.name(), self.BLEnergydevice.State())

            for i in statusBLEnergydevice.split("\n") :
                logging.getLogger().error("\t%s\n" % i)
            logging.getLogger().error("\tCheck devices")
                # Envoi a l'energie desiree    
#        self.BLEnergydevice.energy = value
    def getChoochValue(self, pk, ip) :
        logging.getLogger("HWR").debug('EnergyScan:getChoochValue')
        self.pk = pk
        self.ip = ip

class EnergyScanThread(QThread):
    def __init__(self,
                 parent,
                 e_edge,
                 roi_center,
                 filenameIn):

        QThread.__init__(self)
        
        self.parent     = parent
        self.e_edge     = e_edge
        self.roi_center = roi_center
        self.filenameIn = filenameIn
#        self.mrtx = DeviceProxy('i11-ma-c03/op/mono1-mt_rx')
        self.miniSteps = 1 #30
        self.integrationTime = 1.
        
    def run(self):
        self.result = -1
        logging.getLogger("HWR").debug('EnergyScanThread:run')
#        	mono = SimpleDevice("i10-c-c02/op/mono1")
#         qbpm1 = SimpleDevice("i10-c-c02/dt/xbpm_diode.1")
#         counter = SimpleDevice("i10-c-c00/ca/bai.1144-pci.1h-cpt.1")
#        if self.parent.BLEnergyHO is not None:
#            self.parent.connect(self.parent.BLEnergyHO,qt.PYSIGNAL('setEnergy'),self.energyChanged)
#             self.parent.BLEnergyHO.setEnergy(7.0)
        self.prepare4EScan()
        self.scan (((self.parent.counterdevice, "counter1"), (self.parent.xbpmdevice, "intensity")), # sSensors
                    (self.parent.monodevice, "energy"),                                              # sMotor
                     self.e_edge - self.parent.before,                                               # sStart
                     self.e_edge + self.parent.after,                                                # sEnd
                     self.parent.nbsteps,                                                            # nbSteps
                     sFileName = self.filenameIn,                                                    # sFileName 
                     integrationTime = self.integrationTime/self.miniSteps) #integrationTime=self.parent.integrationtime
        
        
        self.parent.scanCommandFinished(self.result)
        self.afterScan()
   
    def prepare4EScan(self):
        logging.getLogger("HWR").debug('EnergyScanThread:prepare4EScan')
#        self.mrtx.On()
        
        self.parent.connectTangoDevices()
        if not self.parent.canScan :     
            return
        # Rontec configuration
        if self.parent.fluodetdevice.State().name == "RUNNING" :
            self.parent.fluodetdevice.Abort()
            while self.parent.fluodetdevice.State().name != 'STANDBY':
                pass
        #self.parent.fluodetdevice.energyMode = 1
        #time.sleep(0.5)
        #self.parent.fluodetdevice.readDataSpectrum = 0
        #time.sleep(0.5)
        #self.parent.fluodetdevice.SetSpeedAndResolutionConfiguration(0)
        #time.sleep(0.5)
        self.parent.fluodetdevice.presettype = 1
        self.parent.fluodetdevice.peakingtime = 2.5 #2.1
        self.parent.fluodetdevice.presetvalue = 0.64 #1.
        
        #conversion factor: 2048 channels correspond to 20,000 eV hence we have approx 10eV per channel
        #channelToeV = self.parent.fluodetdevice.dynamicRange / len(self.parent.fluodetdevice.channel00)
        channelToeV = 10. #MS 2013-05-23
        roi_debut = 1000.0*(self.roi_center - self.parent.roiwidth / 2.0) #values set in eV
        roi_fin   = 1000.0*(self.roi_center + self.parent.roiwidth / 2.0) #values set in eV
        print 'roi_debut', roi_debut
        print 'roi_fin', roi_fin
        
        
        channel_debut = int(roi_debut / channelToeV) 
        channel_fin   = int(roi_fin / channelToeV)
        print 'channel_debut', channel_debut
        print 'channel_fin', channel_fin
        
        # just for testing MS 07.03.2013, has to be removed for production
        ##### remove for production ####
        #roi_debut = 1120.
        #roi_fin = 1124.
        ##### remove for production ####
       
        self.parent.fluodetdevice.SetROIs(numpy.array((channel_debut, channel_fin)))
        time.sleep(0.1)
        #self.parent.fluodetdevice.integrationTime = 0
        
        # Beamline Energy Positioning and Attenuation setting
        #self.parent.startMoveEnergy(self.e_edge - (self.parent.before - self.parent.after)/2.0)
        self.parent.startMoveEnergy(self.e_edge + (self.parent.after - self.parent.before)/2.0)
        
        #self.parent.attdevice.computedAttenuation = currentAtt
        
        # Positioning Light, BST, Rontec
        self.parent.lightdevice.Extract()
#        self.parent.md2device.write_attribute('BackLightIsOn', False)
        time.sleep(1)
#        self.parent.bstdevice.Insert()
        self.parent.ketekinsertdevice.Insert()
#        self.parent.md2device.write_attribute('FluoDetectorBack', 0)
        time.sleep(4)
#        self.parent.safetyshutterdevice.Open()
        while self.parent.ketekinsertdevice.State().name == "MOVING" or self.parent.BLEnergydevice.State().name == "MOVING":
            time.sleep(1)
    
    def scan(self,
             sSensors, 
             sMotor, 
             sStart, 
             sEnd,
             nbSteps = 100, 
             sStepSize = None,
             sFileName = None,
             stabilisationTime = 0.1,
             interactive = False,
             wait_beamline_status = True,
             integrationTime = 0.25,
             mono_mt_rx = None):
        
        logging.getLogger("HWR").debug('EnergyScanThread:scan')
        print 'sSensors', sSensors
        print 'sMotor', sMotor
        #self.mrtx.On()
        time.sleep(1)
        
        if not self.parent.canScan :   
            return
        
        # initialising
        sData = []
        sSensorDevices = []
        sMotorDevice = sMotor[0]
        print "sStepSize:", sStepSize
 
        if not sStepSize:
            sStepSize = float(sEnd - sStart) / nbSteps
            nbSteps += 1
        else:
            nbSteps = int(1 + ((sEnd - sStart)/sStepionTime)) #__setattr__("integrationTime", integrationTime)Size))
        print "nbsteps:", nbSteps
        
        print "Starting new scan using:"
        sSensorDevices = sSensors
        nbSensors = len(sSensorDevices)
        doIntegrationTime = False
        
        # Rechercher les sensors compteur car besoin d'integrer avant de lire la valeur
        sSensorCounters = []
        for sSensor in sSensorDevices:
            try:
                sSensor[0].__getattr__("integrationTime")
            except:
                pass
            else:
                doIntegrationTime = True 
                if sSensor[0].State == "RUNNING" :
                    sSennsor[0].Stop()
                sSensor[0].write_attribute("integrationTime", integrationTime) #__setattr__("integrationTime", integrationTime)
                sSensorCounters.append(sSensor[0])
        print "sSensorDevices", sSensorDevices                
        print "nbSensors = ", nbSensors
        print "Motor  = %s" % sMotorDevice.name()
        print "Scanning %s from %f to %f by steps of %f (nsteps = %d)" % \
                    (sMotorDevice.name(),sStart, sEnd, sStepSize, nbSteps)
        
        t  = time.localtime()
        sDate = "%02d/%02d/%d - %02d:%02d:%02d" %(t[2],t[1],t[0],t[3],t[4],t[5])
        sTitle = 'EScan - %s ' % (sDate)
    
        # Parametrage du SoleilPlotBrick
        scanParameter = {}
        scanParameter['title'] = sTitle        
        scanParameter['xlabel'] = "Energy in keV"
        scanParameter['ylabel'] = "Normalized counts"
        self.parent.newScan(scanParameter)    
        
        # Pre-positioning the motor     
        if  not self.parent.scanning :
            return
        try :
            while str(sMotorDevice.State()) == 'MOVING':
                time.sleep(1)            
            sMotorDevice.write_attribute(sMotor[1], sStart) 
        except :
            print "probleme sMotor"
            self.parent.scanCommandFailed()    
        # while (sMotorDevice.State == 'MOVING')
        
        # complete record of the collect MS 23.05.2013
        # How to represent a fluorescence emission spectra record
        # Element, Edge, DateTime, Total accumulation time per data point, Number of recordings per data point 
        # DataPoints: Undulator energy, Mono energy, ROI counts, InCounts, OutCounts, Transmission, XBPM1 intensity, counts for all Channels
        #collectRecord = {}
        #time_format = "%04d-%02d-%02d - %02d:%02d:%02d"
        #DateTime = time_format % (t[0], t[1], t[2], t[3], t[4], t[5])
        
        #collectRecord['DateTime'] = DateTime
        #collectRecord['Edge'] = self.parent.edge
        #collectRecord['Element'] = self.parent.element
        #collectRecord['TheoreticalEdge'] = self.parent.thEdge
        #collectRecord['ROIwidth'] = self.parent.roiwidth
        #collectRecord['ROIcenter'] = self.roi_center
        #collectRecord['ROIStartsEnds'] = self.roisStartsEnds
        #collectRecord['IntegrationTime'] = integrationTime
        #collectRecord['StabilisationTime'] = stabilisationTime
        #collectRecord['Transmission'] = ''c
        #collectRecord['Filter'] = ''
        #collectRecord['DataPoints'] = {}
        
        # Ecriture de l'entete du fichier
        try :
            f = open(sFileName, "w")
        except :
            print "probleme ouverture fichier"
            self.parent.scanCommandFailed()
            return
        
        f.write("# %s\n" % (sTitle))
        f.write("# Motor  = %s\n" % sMotorDevice.name())
        # On insere les valeurs normalisees dans le deuxieme colonne
        f.write("# Normalized value\n")
        
        for sSensor in sSensorDevices:
            print "type(sSensor) = " ,type(sSensor)
            f.write("# %s\n" % (sSensor[0].name()))
        
        f.write("# Counts on the fluorescence detector: all channels")
        f.write("# Counts on the fluorescence detector: channels up to end of ROI")
        
        tDebut = time.time()
        
        # On ajoute un sensor pour la valeur normalisee (specifique au EScan)
        nbSensors = nbSensors + 1
        fmt_f = "%12.4e" + (nbSensors + 3)*"%12.4e" + "\n"
        _ln = 0
        
        channel_debut, channel_end = self.parent.fluodetdevice.roisStartsEnds
        # Entering the Scan loop
        measurement = 0
        for sI in range(nbSteps): #range(nbSteps): MS. 11.03.2013 lower the number for quick tests
            print 'Step sI', sI, 'of', nbSteps
            # test sur l utilisateur n a pas demande un stop
            if  not self.parent.scanning :
                break
            pos_i = sStart + (sI * sStepSize)
            
            # positionnement du moteur
            while str(sMotorDevice.State()) == 'MOVING':
                time.sleep(1)
            sMotorDevice.write_attribute(sMotor[1], pos_i) #sMotorDevice.__setattr__(sMotor[1], pos_i)
            
            
            # opening the fast shutter
            self.parent.fastshutterdevice.Open()
            #self.parent.md2device.OpenFastShutter() #write_attribute('FastShutterIsOpen', 1)
            #while self.parent.md2device.read_attribute('FastShutterIsOpen') != 1:
                #time.nsleep(0.05)  
                
            # Attente de stabilisation 
            #time.sleep(stabilisationTime)
            
            # starting the measurement for the energy step
            #miniSteps = 3
            roiCounts = 0
            intensity = 0
            eventsInRun = 0
            eventsInRun_upToROI = 0
	    eventsInRun_diffusion = 0
            for mS in range(self.miniSteps):
                measurement += 1
                self.parent.fluodetdevice.Start()
                time.sleep(0.1)
                #self.parent.counterdevice.Start()
                #time.sleep(integrationTime/self.miniSteps)
                #while self.parent.counterdevice.State().name != 'STANDBY':
                    #pass
                #self.parent.fluodetdevice.Abort()
                while self.parent.fluodetdevice.State().name != 'STANDBY':
                    time.sleep(0.1)
#                    pass
#                roiCounts += self.parent.fluodetdevice.roi00_01
                roiCounts += self.parent.fluodetdevice.roi02_01
                intensity += self.parent.xbpmdevice.intensity
                eventsInRun += self.parent.fluodetdevice.eventsInRun02
                #print 5*'\n'
                #print 'realTime00', self.parent.fluodetdevice.realTime00
                #print 5*'\n'
#                eventsInRun_upToROI += sum(self.parent.fluodetdevice.channel00[ :channel_end + 1])
                eventsInRun_upToROI += sum(self.parent.fluodetdevice.channel02[ :channel_end + 1])
		eventsInRun_diffusion += sum(self.parent.fluodetdevice.channel02[ channel_end + 50 :])
                #collectRecord['DataPoints'][measurement] = {}
                #collectRecord['DataPoints'][measurement]['MonoEnergy'] = pos_i
                #collectRecord['DataPoints'][measurement]['ROICounts']  = self.parent.fluodetdevice.roi00_01
                
            #Lecture de la position du moteur            
            pos_readed = sMotorDevice.read_attribute(sMotor[1]).value #__getattr__(sMotor[1])
            
            # On laisse une place pour mettre la valeur normalisee (specifique au EScan)
            measures = [pos_readed, -1.0]
            print "Position: %12.4e   Measures: " % pos_readed
            
            # Lecture des differents sensors           
            measures.append(roiCounts) #measures[2]#(self.parent.fluodetdevice.roi00_01) #eventsInRun00)
            measures.append(intensity) #measures[3]#(self.parent.xbpmdevice.intensity)
            measures.append(eventsInRun) #measures[4]#(self.parent.fluodetdevice.eventsInRun00)
            measures.append(eventsInRun_upToROI)#measures[5]
            measures.append(eventsInRun_diffusion)
            # closing the fastshutter
            self.parent.fastshutterdevice.Close() 
            #self.parent.md2device.CloseFastShutter() #write_attribute('FastShutterIsOpen', 0)
            #while self.parent.md2device.read_attribute('FastShutterIsOpen') != 0:
                #time.sleep(0.05)
               
            # Valeur normalisee specifique au EScan 
            #(Oblige an mettre le sensor compteur en premier et le xbpm en deuxieme dans le liste des sensors)               
            try:
                measures[1] = measures[2] / measures[6] #measures[3]  
#                measures[1] = measures[2] / measures[3]   
#                measures[1] = measures[2]   
            except ZeroDivisionError, e:
                print e
                print 'Please verify that the safety shutter is open.'
                measures[1] = 0.0
            
            # Demande de mise a jour du SoleilPlotBrick
            #if sI % 5 == 0:
            self.parent.newPoint(measures[0], measures[1])    
              
            
            #Ecriture des mesures dans le fichier
            f.write(fmt_f % tuple(measures))
            
            _ln += 1
            if not _ln % 10:
                f.flush() # flush the buffer every 10 lines
        
        # Exiting the Scan loop      
        self.parent.fastshutterdevice.Close()
#        while self.parent.fastshutterdevice.State != 'CLOSE':
#            time.sleep(0.1)
#        self.parent.md2device.CloseFastShutter() 
        #while self.parent.md2device.read_attribute('FastShutterIsOpen') != 0:
            #time.sleep(0.05)
        
        self.parent.fluodetdevice.Abort()
        
#        self.parent.md2device.write_attribute('FluoDetectorBack', 1)
#        time.sleep(2)
        #self.parent.mono_mt_rx_device.On()
        if  not self.parent.scanning :
            self.result = -1
        else :
            self.result = 1

        tScanTotal = time.time() - tDebut
        print "Time taken for the scan = %.2f sec" % (tScanTotal)
        f.write("# Duration = %.2f sec\n" % (tScanTotal))
        f.close()

    def afterScan(self) :
        logging.getLogger("HWR").debug('EnergyScanThread:afterScan')
#        self.parent.safetyshutterdevice.Close()
        if self.parent.pk :
            self.parent.startMoveEnergy(self.parent.pk)
            
=======
    blsampleid = scanInfo['blSampleId']
    scanInfo.pop('blSampleId')
    db_status=dbConnection.storeEnergyScan(scanInfo)
    if blsampleid is not None:
        try:
            energyscanid=int(db_status['energyScanId'])
        except:
            pass
        else:
            asoc={'blSampleId':blsampleid, 'energyScanId':energyscanid}
            dbConnection.associateBLSampleAndEnergyScan(asoc)
>>>>>>>  	modified:   HardwareObjects/EnergyScan.py:EnergyScan.py
