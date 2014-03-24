# itest.py driver for Yokogawa_7651 Voltage source
# Fan Wu 2013
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from instrument import Instrument

import visa
import types
import logging
import numpy

import qt

def bool_to_str(val):
    '''
    Function to convert boolean to 'ON' or 'OFF'
    '''
    if val == True:
        return "ON"
    else:
        return "OFF"

class itest(Instrument):
    '''
    This is the driver for the Itest system

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'Itest',
        address='<GBIP address>',
        reset=<bool>,
        change_display=<bool>,
        change_autozero=<bool>)
    '''

    def __init__(self, name, address, reset=False):
#                  change_display=True, change_autozero=True):
        '''
        Initializes the Itest, and communicates with the wrapper.

        Input:
            name (string)           : name of the instrument
            address (string)        : GPIB address
            reset (bool)            : resets to default values

        Output:
            None
        '''
        # Initialize wrapper functions
        logging.info('Initializing instrument Itest')
        Instrument.__init__(self, name, tags=['physical'])

        # Add some global constants
        self._address = address
        self._visainstrument = visa.instrument(self._address)
   
#         self._modes = ['VOLT:DC', 'CURR:DC']  # DC volt or DC curr mode

        # Add parameters to wrapper
        self.add_parameter('ActiveInstrument',
            flags=Instrument.FLAG_GETSET,
            units='', minval=1, maxval=5, type=types.IntType)
        self.add_parameter('readset', flags=Instrument.FLAG_GET,
            units='AU',
            type=types.FloatType,
            tags=['setvalue'])
        self.add_parameter('readmeas', flags=Instrument.FLAG_GET,
            units='AU',
            type=types.FloatType,
            tags=['measvalue'])
			
        # Add functions to wrapper
        self.add_function('reset')
        
#        self.add_function('set_ActiveInstrument')
#        self.add_function('get_ActiveInstrument')
        self.add_function('get_ActiveInstrument_type')
        self.add_function('get_instruments_list')
        self.add_function('output_on')
        self.add_function('output_off')
        self.add_function('sensor_on')
        self.add_function('sensor_off')
        self.add_function('set_volt')
        self.add_function('get_volt')
        self.add_function('meas_volt')
        self.add_function('get_output_state')
        self.add_function('get_sensor_state')
       

        # Connect to measurement flow to detect start and stop of measurement
#         qt.flow.connect('measurement-start', self._measurement_start_cb)
#         qt.flow.connect('measurement-end', self._measurement_end_cb)

        if reset:
            self.reset()
        self.get_instruments_list()
        self._activeinst = self.get_ActiveInstrument()
        self._activeBE586channel = 1

#         else:
# #             self.get_all()
#             self.set_defaults()

# --------------------------------------
#           functions
# --------------------------------------
    def reset(self):
        '''
        Resets instrument to default values

        Input:
            None

        Output:
            None
        '''
        logging.debug('Resetting instrument Itest')
        self._visainstrument.write('*RST')
#         self.get_all()

                
    def get_output_state(self):
        if self.get_ActiveInstrument_type() == '2102':
            return self.BE2102_get_output_state()
        elif self.get_ActiveInstrument_type() == '586':
            return self.BE586_get_output_state()
        else:
            print 'unfinished for other modules'
                
    def get_sensor_state(self):
        if self.get_ActiveInstrument_type() == '2102':
            return self.BE2102_get_sensor_state()
        else:
            print 'unfinished for other modules'
                    
    def output_on(self):
        if self.get_ActiveInstrument_type() == '2102':
#             activeinstrtemp = self._activeinst
#             self.set_ActiveInstrument(val)
            self.BE2102_output_on()
        elif self.get_ActiveInstrument_type() == '586':
            self.BE586_output_on()            
        else:
            print 'unfinished for other modules'
                       
    def output_off(self):
        if self.get_ActiveInstrument_type() == '2102':
            self.BE2102_output_off()
        elif self.get_ActiveInstrument_type() == '586':
            self.BE586_output_off()   
        else:
            print 'unfinished for other modules'
                
    def sensor_on(self):
        if self.get_ActiveInstrument_type() == '2102':
            self.BE2102_sensor_on()
        else:
            print 'unfinished for other modules'
                        
    def sensor_off(self):
        if self.get_ActiveInstrument_type() == '2102':
            self.BE2102_sensor_off()
        else:
            print 'unfinished for other modules'
                        
    def set_volt(self, val):
        if self.get_ActiveInstrument_type() == '2102':
            self.BE2102_set_volt(val)
        elif self.get_ActiveInstrument_type() == '586':
            self.BE586_set_volt(val)   
        else:
            print 'unfinished for other modules'

    def set_voltrange(self, val):
        if self.get_ActiveInstrument_type() == '2102':
            self.BE2102_set_voltrange(val)
        else:
            print 'unfinished for other modules'

    def get_volt(self):
#       Old function for read-out, links to get_readset()
        logging.debug('Link to get_readset()')
        return self.get_readset()
            
    def meas_volt(self):
#       Old function for read-out, links to get_readset()
        logging.debug('Link to get_readmeas()')
        return self.get_readmeas()

# --------------------------------------
#           internal functions
# --------------------------------------
    def BE2102_output_on(self):
        if self.BE2102_get_output_state():
            pass
        else:
            tempvolt = self.BE2102_get_volt_set()
            if abs(tempvolt) > 1e-3:
                logging.warn('Itest instrument %i was set to %f volt!' % (self._activeinst, tempvolt))
            logging.debug('Itest instrument %i output on.' % self._activeinst)
            self._visainstrument.write('OUTP on')
        
    def BE2102_output_off(self):
        if self.BE2102_get_output_state():
            tempvolt = self.BE2102_get_volt_set()
            if abs(tempvolt) > 1e-3:
                logging.warn('Itest instrument %i was set to %f volt!' % (self._activeinst, tempvolt))
            logging.debug('Itest instrument %i output off.' % self._activeinst)
            self._visainstrument.write('OUTP off')
            
    def BE2102_sensor_on(self):
        if self.BE2102_get_sensor_state():
            pass
        else:
            logging.debug('Itest instrument %i sensor on.' % self._activeinst)
            self._visainstrument.write('VOLT:REM ON')
        
    def BE2102_sensor_off(self):
        logging.debug('Itest instrument %i sensor off.' % self._activeinst)
        self._visainstrument.write('VOLT:REM OFF')
        
    def BE2102_set_volt(self, val):
        if self.BE2102_get_output_state():
            pass
        else:
            logging.warn('InstNo %i output was off, now turn on.' % self._activeinst)
            self.BE2102_output_on()
        logging.debug('Set DC voltage of instNo %i to %f' % (self._activeinst, val))
        self._visainstrument.write('VOLT %f' % val)
        
    def BE2102_set_voltrange(self, val):
        if self.BE2102_get_output_state():
            logging.error('InstNo %i output is on, voltage output has to be turned off to reset the range.' % self._activeinst)
        logging.debug('Set DC voltage range of instNo %i to %f ' % (self._activeinst, val))
        self._visainstrument.write('VOLT:RANG %f' % val)
        
    def BE2102_set_voltslope(self, val):
        if val < 1.2e-6 or val > 1:
            logging.error('wrong voltage slope.')
        else:
            logging.debug('Set DC voltage slope of instNo %i to %f V/ms' % (self._activeinst, val))
        self._visainstrument.write('VOLT:SLOP %f' % val)

    def BE586_output_on(self):
        if self.BE586_get_output_state():
            pass
        else:
            tempvolt = self.BE586_get_volt_set()
            if abs(tempvolt) > 1e-3:
                logging.warn('Itest instrument %i was set to %f volt, and now turning on from zero!' % (self._activeinst, tempvolt))
            logging.debug('Itest BE586 channel %i output on.' % self._activeBE586channel)
            self._visainstrument.write('OUTP on')
        
    def BE586_output_off(self):
        if self.BE586_get_output_state():
            tempvolt = self.BE586_get_volt_set()
            if abs(tempvolt) > 1e-3:
                logging.warn('Itest instrument %i was set to %f volt, and now turning off to zero!' % (self._activeinst, tempvolt))
            logging.debug('Itest BE586 channel %i output off.' % self._activeBE586channel)
            self._visainstrument.write('OUTP off')

    def BE586_set_volt(self, val):
        if self.BE586_get_output_state():
            pass
        else:
            logging.warn('InstNo %i output was off, now turn on.' % self._activeinst)
            self.BE586_output_on()
        logging.debug('Set DC voltage of instNo %i to %f' % (self._activeinst, val))
        self._visainstrument.write('VOLT %f' % val)
        
# --------------------------------------
#           parameters
# --------------------------------------

    def do_set_ActiveInstrument(self, instNo = 1):
        if instNo <1 or instNo >5:
            logging.error('Unexpected Inst number')
        else:
            logging.debug('Set Itest active instrument to %i' % instNo)
            self._visainstrument.write('INST %i' % instNo)
            self._activeinst = instNo
            insttemp = self.get_ActiveInstrument()
            if insttemp != self._activeinst:
                logging.error('Set Itest active instrument failed!!!')
            qt.msleep(0.005)
			
    def do_get_ActiveInstrument(self):
        actinsttemp = int(self._visainstrument.ask('INST ?'))
#         if actinsttemp != self._activeinst:
#             logging.warn('Active instrument incorrect, plz check. actintemp = %i, self.activinst = %i' % (actinsttemp, self._activeinst))
        self._activeinst = actinsttemp 
        return self._activeinst

    def do_get_readset(self):
        if self.get_ActiveInstrument_type() == '2102':
            return self.BE2102_get_volt_set()
        elif self.get_ActiveInstrument_type() == '586':
            return self.BE586_get_volt_set()  
        else:
            print 'unfinished for other modules'

    def do_get_readmeas(self):
        if self.get_ActiveInstrument_type() == '2102':
            return self.BE2102_get_volt_measure()
        elif self.get_ActiveInstrument_type() == '586':
            return self.BE586_get_volt_measure()
        else:
            print 'unfinished for other modules'
			
    def get_instruments_list(self):
        templist = self._visainstrument.ask('INST:LIST?')
        self._instlist = templist.rsplit(';')
        print 'Itest instrument list:', self._instlist
        logging.debug('Itest instrument check:' + str(self._instlist))
        
    def get_ActiveInstrument_type(self):
        activeinst = 'Getting active instrument fail!'
        for instindex in self._instlist:
            insttype = instindex.rsplit(',')
            if int(insttype[0]) ==  self._activeinst:
                activeinst = insttype[1]

#         logging.debug('Itest instrument No.' + insttype[0] + ' is type ' + insttype[1])
        return activeinst
    
    def get_instrument_type(self, val):
        activeinst = 'Getting active instrument fail!'
        for instindex in self._instlist:
            insttype = instindex.rsplit(',')
            if int(insttype[0]) ==  val:
                activeinst = insttype[1]
#         logging.debug('Itest instrument No.' + insttype[0] + ' is type ' + insttype[1])
        return activeinst

    def BE586_set_active_channel(self, chanNo = 1):
        if chanNo <1 or chanNo >3:
            logging.error('Unexpected channel number')
        else:
            logging.debug('Set Itest BE586 active channel to %i' % chanNo)
            self._visainstrument.write('CHAN %i' % chanNo)
            self._activeBE586channel = chanNo
            chantemp = self.BE586_get_active_channel()
            if chantemp != self._activeBE586channel:
                logging.error('Set Itest BE586 active channel failed!!!')
            qt.msleep(0.005)

    def BE586_get_active_channel(self):
        actchantemp = int(self._visainstrument.ask('CHAN ?'))
#         if actchantemp != self._activeBE586channel:
#             logging.warn('Active channel incorrect, plz check BE586 status. actchantemp = %i, self.activechan = %i' % (actchantemp, self._activeBE586channel))
        self._activeBE586channel = actchantemp 
        return self._activeBE586channel

    def BE2102_get_output_state(self):
        return int(self._visainstrument.ask('OUTP ?'))
       
    def BE2102_get_sensor_state(self):
        return int(self._visainstrument.ask('VOLT:REM ?'))
    
    def BE2102_get_volt_set(self):
        return float(self._visainstrument.ask('VOLT ?')) 
    
    def BE2102_get_volt_measure(self):
        return float(self._visainstrument.ask('MEAS:VOLT ?')) 
 
    def BE2102_get_curr_measure(self):
        return float(self._visainstrument.ask('MEAS:CURR ?')) 
    
    def BE586_get_output_state(self):
        return int(self._visainstrument.ask('OUTP ?'))

    def BE586_get_volt_set(self):
        return float(self._visainstrument.ask('VOLT ?')) 
    
    def BE586_get_volt_measure(self):
        return float(self._visainstrument.ask('MEAS:VOLT ?')) 
    
    def BE586_get_curr_measure(self):
        return float(self._visainstrument.ask('MEAS:CURR ?'))
        
# --------------------------------------
#           Internal Routines
# --------------------------------------   