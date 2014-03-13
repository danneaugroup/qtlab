'''copied from Msaximilian's program, unfinished'

"""
PyMeasure

Last changed by:
'$Author: (local) $

'$Rev: 5M $
'$Date: 2012-07-18 16:41:51 +0200 (Mi, 18 Jul 2012) $

"""


from Devices.Globals import PyM_Debug
from Devices.GPIB.GPIB_Device import PyM_GPIBDevice
from Devices.Types.PSU import PSU
from decimal import Decimal
import time


class ldevice(PyM_GPIBDevice, PSU):
    
    """ Overloading variables originating from base class"""
    _PyM_Device__istring = "Yokogawa_GS200"
    
    def __init__(self, gpib_id, name, control="", simulated=False):
        PyM_GPIBDevice.__init__(self, gpib_id, name, control, simulated)
        PSU.__init__(self)

    
    def _PSU__gpib_init(self):    
        """self.write("*RST")"""
        """ clear error queue"""
        if PyM_Debug:
            print self.ask(":STAT:ERR?")
        self.write("*CLS")
        """ turn measurement function on"""
        self.write(":SENS:STAT ON")
        """ set measurement trigger to immediate """
        self.write(":SENS:TRIG IMM")
        
    
    def set_sense_accuracy(self, value):
        if value <= 25:
            self.write(":SENS:NPLC " + str(value))
            """ calculate waiting time for MEAS? commands """
            lfr = self.ask(":SYST:LFR?")
            """ we need twice the time to account for null measurements"""
            if self.simulated:
                self._PSU__mtime = 0
            else:
                self._PSU__mtime = float(1.0)/float(lfr) * value * 2
        else:
            raise Exception(self.exc("Accuracy must be an integer between 1 and 25!"))
        
    
    """ selects range to be used based on maximum voltage vmax parameter"""
    def _PSU__gpib_set_vdc_mode(self, vmax=1, amax=0.001):
        self.write(":SOUR:FUNC VOLT")
        if vmax < 10e-3:
            self.write(":SOUR:RANG 10E-3")
        elif vmax < 100e-3:
            self.write(":SOUR:RANG 100E-3")        
        elif vmax < 1:
            self.write(":SOUR:RANG 1E+0")
        elif vmax < 10:
            self.write(":SOUR:RANG 10E+0")
        elif vmax <= 30:
            self.write(":SOUR:RANG 30E+0")
        else:
            raise Exception(self.exc("sources only support voltages up to 30e0 V!"))
        self.write(":SOUR:PROT:CURR " + str(amax))
    
    
    def _PSU__gpib_set_adc_mode(self, amax=0.001, vmax=1):
        self.write(":SOUR:FUNC CURR")
        if amax < 1e-3:
            self.write(":SOUR:RANG 1E-3")
        elif amax < 10e-3:
            self.write(":SOUR:RANG 10E-3")
        elif amax < 100e-3:
            self.write(":SOUR:RANG 100E-3")
        elif amax <= 200e-3:
            self.write(":SOUR:RANG 200E-3")
        else:
            raise Exception(self.exc("GS200 sources only support currents up to 200e-3 A!"))
        self._PSU__amax = amax
        self.write(":SOUR:PROT:VOLT " + str(vmax))

    
    def _PSU__gpib_set_voltage(self, value):
            self.write(":SOUR:LEV " + str(value))
 
 
    def _PSU__gpib_set_current(self, value):
            self.write(":SOUR:LEV " + str(value))
    
    
    def _PSU__gpib_get_voltage(self):
        """ read the current voltage level (in VDC mode)"""
        self.write(":SOUR:LEV?")
        time.sleep(self.get_mtime())
        return float(self.read())   

    def _PSU__gpib_sense_voltage(self):
        """ sense the voltage when in current output mode (ADC)"""
        self.write(":MEAS?")
        time.sleep(self.get_mtime())
        return float(self.read())   
 
 
    def _PSU__gpib_get_current(self):
        """ read the currently set current level (in ADC mode)"""
        if self._PSU__vmax < 100E-3:
            raise Exception(self.exc("Cannot measure current while in mV source range"))
        else:
            self.write(":SOUR:LEV?")
            time.sleep(self.get_mtime())
            return float(self.read())

    def _PSU__gpib_sense_current(self):
        """ sense the current when in voltage output mode (VDC)"""
        self.write(":MEAS?")
        time.sleep(self.get_mtime())
        return float(self.read())      
    
    
    def _PSU__gpib_enable_output(self):
        self.write(":OUTP:STAT 1")


    def _PSU__gpib_disable_output(self):
        self.write(":OUTP:STAT 0")     
        
    def _PSU__gpib_pulse(self,lo,hi):
        self.write(":SOUR:LEV " + str(hi) + ";*TRG;*CLS;:SOUR:LEV " + str(lo))
        
        """
        self.write("PROG:REP ON")
        self.write("PROG:SLOP 0")
        self.write("PROG:TRIG MEND")
        
        self.write(":OUTP:STAT 0")  
        self.write("PROG:EDIT:STAR")   
        self.write("SOUR:LEV " + str(float(lo)))
        self.write("SOUR:LEV " + str(float(hi)))
        self.write("SOUR:LEV " + str(float(lo)))
        self.write("PROG:EDIT:END") 
        self.write(":OUTP:STAT 1") """
        
        







if __name__ == "__main__":
    inst = ldevice(1, "yk", "", True)
    print inst.quantities
    inst.set_mode("ADC", 1, 0.001)
    inst.set_sense_accuracy(25)
    inst.enable_output()
    print inst._PSU__amax
    inst.set_value(0.00001)
    time.sleep(1)
    
    val = Decimal(inst.get_voltage())/Decimal(inst.get_current())
    print "Reistance is : " + str(val)
    
    
    inst.disable_output()
    """
    dev = ldevice(1, "GS200_test", "", True);
    dev.set_vdc_mode(30)
    dev.set_voltage(30)
    dev.get_voltage()
    dev.get_current()
    dev.beep()"""