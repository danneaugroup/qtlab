# Keithley_236.py driver for Keithley 236 DMM
# Jens Mohrmann 
#
# Based on Keithley_2700.py driver
# Pieter de Groot <pieterdegroot@gmail.com>, 2008
# Martijn Schaafsma <qtlab@mcschaafsma.nl>, 2008
# Reinier Heeres <reinier@heeres.eu>, 2008
# Update december 2009:
# Michiel Jol <jelle@michieljol.nl>
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

class Keithley_236(Instrument):
    '''
    This is the driver for the Keithley 2700 Multimeter

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'Keithley_2700',
        address='<GBIP address>',
        reset=<bool>,
        change_display=<bool>,
        change_autozero=<bool>)
    '''


    
    
    def __init__(self, name, address, reset=False,
            range=10, filter=0):
        '''
        Initializes the Keithley_2700, and communicates with the wrapper.

        Input:
            name (string)           : name of the instrument
            address (string)        : GPIB address
            reset (bool)            : resets to default values
            change_display (bool)   : If True (default), automatically turn off
                                        display during measurements.
            change_autozero (bool)  : If True (default), automatically turn off
                                        autozero during measurements.
        Output:
            None
        '''
        # Initialize wrapper functions
        logging.info('Initializing instrument Keithley_236')
        Instrument.__init__(self, name, tags=['physical'])

        # Add some global constants
        self._address = address
        self._visainstrument = visa.instrument(self._address)
        
        self._source_modes = ['VOLT', 'CURR']
        self._source_mode # current source mode
        
        # self._modes = ['VOLT:DC', 'CURR:DC']

        # self._trigger_sent = False
        
        # Save settings into variables since they can not be read from the instrument
        self._range = range
        self._filter = filter
        
        self._voltage_compliance = 1e-3
        self._current_compliance = 1e-6
        
        
        
        
        
        # Add parameters to wrapper
        self.add_parameter('readval', flags=Instrument.FLAG_GET,
            units='AU',
            type=types.FloatType,
            tags=['measure'])

        self.add_parameter('range',
            flags=Instrument.FLAG_SET,
            units='', minval=0.1, maxval=1000, type=types.FloatType)
            
        self.add_parameter('filter', flags=Instrument.FLAG_SET,
            type=types.IntType, minval=0, maxval=5)
            
        self.add_parameter('source_current_compliance',
            flags=Instrument.FLAG_SET,
            units='A', minval=1e-9, maxval=105e-3, type=types.FloatType)
        self.add_parameter('source_voltage_compliance',
            flags=Instrument.FLAG_SET,
            units='V', minval=1e-12, maxval=210., type=types.FloatType)
            
        self.add_parameter('source_current_level',
            flags=Instrument.FLAG_SET,
            units='A', minval=-105e-3, maxval=105e-3, type=types.FloatType)
        self.add_parameter('source_voltage_level',
            flags=Instrument.FLAG_SET,
            units='V', minval=-105., maxval=105., type=types.FloatType)     

        self.add_parameter('output_on',
            flags=Instrument.FLAG_SET,
            type=types.BooleanType)         

        self.add_parameter('source_mode',
            flags=Instrument.FLAG_SET,
            type=types.StringType, units='')
        '''
        self.add_parameter('sense_mode',
            flags=Instrument.FLAG_GETSET,
            type=types.StringType, units='')            
        '''
        
        # Add functions to wrapper
        self.add_function('set_source_mode_volt')
        self.add_function('set_source_mode_curr')
        
        self.add_function('reset')
        # self.add_function('get_all')
        self.add_function('read')

        # Connect to measurement flow to detect start and stop of measurement
        qt.flow.connect('measurement-start', self._measurement_start_cb)
        qt.flow.connect('measurement-end', self._measurement_end_cb)

        if reset:
            self.reset()
        else:
            # self.get_all()
            self.set_defaults()

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
        logging.debug('Resetting instrument')
        self._visainstrument.write('DCL')
        # self.get_all()

    def set_defaults(self):
        '''
        Set to driver defaults:
        Output=data only
        Mode=Volt:DC
        Digits=7
        Trigger=Continous
        Range=10 V
        NPLC=1
        Averaging=off
        '''

        self._visainstrument.write('G4,2,0X') # Set output to measured value (4) (1: source value), format to ascii without prefix and suffix(2) (0: prefix and suffix), one line output     
        self.set_source_mode_volt()
        print "test1"
        self.set_source_current_compliance(1e-6, measurementRange=1)
        print "test"
        self.set_source_voltage_compliance(1e-3, measurementRange=1)
        self.set_range(10)
        self.set_filter(0)
        
    """
    def get_all(self):
        '''
        Reads all relevant parameters from instrument

        Input:
            None

        Output:
            None
        '''
        # data can not be read from device...
        logging.info('Get all relevant data from device')
        self.get_mode()
        self.get_range()
        self.get_mode()
        self.get_filter()
    """
    
# Link old read and readlast to new routines:
    # Parameters are for states of the machnine and functions
    # for non-states. In principle the reading of the Keithley is not
    # a state (it's just a value at a point in time) so it should be a
    # function, technically. The GUI, however, requires an parameter to
    # read it out properly, so the reading is now done as if it is a
    # parameter, and the old functions are redirected.
    
    def read(self):
        '''
        Link to get_readval
        '''
        return self.do_get_readval()
        
    def do_get_readval(self):
        '''
        Old function for read-out, links to get_readval()
        '''
        text = self._visainstrument.read()
        return float(text)


    def do_set_source_mode(self, mode):
        '''
        Set the source_mode to the specified value

        Input:
            mode (string) : mode to be set. Choose from self._source_modes

        Output:
            None
        '''

        logging.debug('Set source_mode to %s', mode)
        if mode in self._source_modes:
            i = self._source_modes.index(mode)
            string = 'F%s,0' % i
            self._visainstrument.write(string)
        else:
            logging.error('invalid source_mode %s' % source_mode)


    
    def set_source_mode_volt(self):
        '''
        Set source mode to DC Voltage
        (measure Current)

        Input:
            None

        Output:
            None
        '''
        self.set_source_mode('VOLT')
        
        self._change_units('V')
        # self.get_all()
        # Get all values again because some paramaters depend on mode
        

    def set_source_mode_curr(self):
        '''
        Set mode to DC Current

        Input:
            None

        Output:
            None
        '''
        self.set_source_mode('CURR')
        self._change_units('I') # measured unit
        # self.get_all()
        # Get all values again because some paramaters depend on mode


        
# --------------------------------------
#           parameters
# --------------------------------------

    def do_set_output_on(self,val):
        '''
        Set Output on
        '''
        
        logging.debug('Set output on: %s' % val)
        
        self._visainstrument.write('N%i' % val)
    

    def do_set_range(self, val, mode=self._mode):
        '''
        Set range to the specified value for the
        designated mode. If mode=None, the current mode is assumed

        Input:
            val (float)   : Range in specified units
            mode (string) : mode to set property for. Choose from self._modes

        Output:
            None
        '''
        
        logging.debug('Set range variable to %s' % val)
        self._meas_voltage_range = val # (range has to be specified when voltage is set)
        # self._set_func_par_value(mode, 'RANG', val)


    def do_set_filter(self, val, mode=None):
        '''
        Set filter (P[0-5])

        Input:
            val (float)   : 0-5, filters 2^n readings, 0=off
            mode (string) : mode to set property for. Choose from self._modes.

        Output:
            None
        '''
        logging.debug('Set filter to %s ' % val)
        self._filter = val
        self._visainstrument.write('P%s' % val) # P[0-5] sets filter to 2^n readings

        
        
        
    def do_set_source_voltage_compliance(self, val, measurementRange=self._meas_voltage_range):
        '''
        Set Compliance
        L level,range
        
        Input:
            val:                compliance level
            measurementRange:   measurement/compliance range
        '''

        logging.debug('Set voltage compliance to %s, range %s' %(val, measurementRange))
        self._voltage_compliance =  val
        self._visainstrument.write('L%s,%s' % (val, measurementRange))
        
    def do_set_source_current_compliance(self, val, measurementRange=self._meas_current_range):
        '''
        Set Compliance
        L level,range
        
        Input:
            val:                compliance level
            measurementRange:   measurement/compliance range
        '''
        logging.debug('Set current compliance to %s, range %s' %(val, measurementRange))
        self._current_compliance = val
        self._visainstrument.write('L%s,%s' % (val, measurementRange))
        
        
    def do_set_source_current_level(self, val, measurementRange):
        '''
        Set Compliance
        L level,range
        
        Input:
            val:                compliance level
            measurementRange:   measurement/compliance range
        '''
        logging.debug('Set voltage compliance to %s, range %s' %(val, measurementRange))
        self._voltage_compliance =  val
        self._visainstrument.write('F%s,%s' % (val, measurementRange))
    
        
    def do_set_source_voltage_level(self, val, measurementRange):
        '''
        Set Compliance
        L level,range
        
        Input:
            val:                compliance level
            measurementRange:   measurement/compliance range
        '''
        logging.debug('Set voltage compliance to %s, range %s' %(val, measurementRange))
        self._voltage_compliance =  val
        self._visainstrument.write('F%s,%s' % (val, measurementRange))


        
# --------------------------------------
#           Internal Routines
# --------------------------------------

    def _change_units(self, unit):
        self.set_parameter_options('readval', units=unit)

    def _determine_mode(self, mode):
        '''
        Return the mode string to use.
        If mode is None it will return the currently selected mode.
        '''
        logging.debug('Determine mode with mode=%s' % mode)
        if mode is None:
            mode = self.get_mode(query=False)
        if mode not in self._modes and mode not in ('INIT', 'TRIG', 'SYST', 'DISP'):
            logging.warning('Invalid mode %s, assuming current' % mode)
            mode = self.get_mode(query=False)
        return mode



    def _measurement_start_cb(self, sender):
        '''
        Things to do at starting of measurement
        '''
        #if self._change_display:
            # self.set_display(False)
            #Switch off display to get stable timing
        #if self._change_autozero:
            # self.set_autozero(False)
            #Switch off autozero to speed up measurement

    def _measurement_end_cb(self, sender):
        '''
        Things to do after the measurement
        '''
        #if self._change_display:
            # self.set_display(True)
        #if self._change_autozero:
            # self.set_autozero(True)

