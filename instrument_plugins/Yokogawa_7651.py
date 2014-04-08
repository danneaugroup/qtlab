# Yokogawa_7651.py driver for Yokogawa_7651 Voltage source
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

class Yokogawa_7651(Instrument):
    '''
    This is the driver for the Yokogawa 7651 Source Unit

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'Yokogawa_7651',
        address='<GBIP address>',
        reset=<bool>,
        change_display=<bool>,
        change_autozero=<bool>)
    '''

    def __init__(self, name, address, reset=False,
                 change_display=True, change_autozero=True):
        '''
        Initializes the Yokogawa_7651, and communicates with the wrapper.

        Input:
            name (string)           : name of the instrument
            address (string)        : GPIB address
            reset (bool)            : resets to default values

        Output:
            None
        '''
        # Initialize wrapper functions
        logging.info('Initializing instrument Yokogawa_7651')
        Instrument.__init__(self, name, tags=['physical'])

        # Add some global constants
        self._address = address
        self._visainstrument = visa.instrument(self._address)
        self._modes = ['VOLT:DC', 'CURR:DC']  # DC volt or DC curr mode

        # Add parameters to wrapper
#         self.add_parameter('range',
#             flags=Instrument.FLAG_GETSET,
#             units='', minval=0.1, maxval=1000, type=types.FloatType)
#         self.add_parameter('trigger_source',
#             flags=Instrument.FLAG_GETSET,
#             units='')
        self.add_parameter('mode',
            flags=Instrument.FLAG_GETSET,
            type=types.StringType, units='')
        self.add_parameter('readval', flags=Instrument.FLAG_GET,
            units='AU',
            type=types.FloatType,
            tags=['measure'])
#         self.add_parameter('autorange',
#             flags=Instrument.FLAG_GETSET,
#             units='',
#             type=types.BooleanType)

        # Add functions to wrapper
        self.add_function('output_on')
        self.add_function('output_off')
        self.add_function('set_mode_volt_dc')
        self.add_function('set_mode_volt_dc')
        self.add_function('set_mode_curr_dc')
#         self.add_function('set_range_auto')
        self.add_function('reset')
#        self.add_function('get_all')

        self.add_function('read')

        self.add_function('send_trigger')
        self.add_function('fetch')
        self.add_function('set_volt')

        # Connect to measurement flow to detect start and stop of measurement
#         qt.flow.connect('measurement-start', self._measurement_start_cb)
#         qt.flow.connect('measurement-end', self._measurement_end_cb)

        if reset:
            self.reset()
        else:
#             self.get_all()
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
        self._visainstrument.write('RC')
#         self.get_all()

    def set_defaults(self):
        '''
        Set to driver defaults:
        Output=ON
        Mode=Volt:DC
        Range=10 V
        NPLC=1
        Averaging=off
        '''

        self.set_mode_volt_dc()
#         self.set_range(10)
        self._visainstrument.write('R4') # set range to 1V
        self.output_on
    
    def output_on(self):
        self._visainstrument.write('O1E')
        
    def output_off(self):
        self._visainstrument.write('O0E')
        
#     def get_all(self):
#         '''
#         Reads all relevant parameters from instrument
# 
#         Input:
#             None
# 
#         Output:
#             None
#         '''
#         logging.info('Get all relevant data from device')
#         self.get_mode()
#         self.get_range()
#         self.get_trigger_continuous()
#         self.get_trigger_count()
#         self.get_trigger_delay()
#         self.get_trigger_source()
#         self.get_trigger_timer()
#         self.get_mode()
#         self.get_digits()
#         self.get_integrationtime()
#         self.get_nplc()
#         self.get_display()
#         self.get_autozero()
#         self.get_averaging()
#         self.get_averaging_window()
#         self.get_averaging_count()
#         self.get_averaging_type()
#         self.get_autorange()

# Link old read and readlast to new routines:
    # Parameters are for states of the machnine and functions
    # for non-states. In principle the reading of the Keithley is not
    # a state (it's just a value at a point in time) so it should be a
    # function, technically. The GUI, however, requires an parameter to
    # read it out properly, so the reading is now done as if it is a
    # parameter, and the old functions are redirected.

    def read(self):
        '''
        Old function for read-out, links to get_readval()
        '''
        logging.debug('Link to do_get_readval()')
        return self.do_get_readval()
    
    def readval(self):
        '''
        Old function for read-out, links to get_readval()
        '''
        logging.debug('Link to do_get_readval()')
        return self.do_get_readval()

    def get_volt(self):
        '''
        Old function for read-out, links to get_readval()
        '''
        #logging.debug('Link to do_get_readval()')
        return float(self.do_get_readval()[4:]) # readval returns string "NDCV+XX.XXXEX", remove first 4 letters and convert to float
		
    def send_trigger(self):
        '''
        Send trigger to Yokogawa 7651
        '''
        logging.debug('Sending trigger')
        self._visainstrument.write('E')
        self._trigger_sent = True


    def fetch(self):
        '''
        Get data at this instance, not recommended, use get_readlastval.
        Use send_trigger() to trigger the device.
        Note that Readval is not updated since this triggers itself.
        '''

        return self.do_get_readval()

    def set_mode_volt_dc(self):
        '''
        Set mode to DC Voltage

        Input:
            None

        Output:
            None
        '''
        logging.debug('Set mode to DC Voltage')
        self.set_mode('VOLT:DC')

    def set_mode_curr_dc(self):
        '''
        Set mode to DC Current

        Input:
            None

        Output:
            None
        '''
        logging.debug('Set mode to DC Current')
        self.set_mode('CURR:DC')

    def set_volt(self, val):
        logging.debug('Set DC voltage')
        self._visainstrument.write('SA%f' % val)
        self._visainstrument.write('E')
        return self._visainstrument.ask('OD')


# --------------------------------------
#           parameters
# --------------------------------------


    def do_get_readval(self, ignore_error=False):
        '''
        Aborts current trigger and sends a new trigger
        to the device and reads float value.
        Do not use when trigger mode is 'CONT'
        Instead use readlastval

        Input:
            ignore_error (boolean): Ignore trigger errors, default is 'False'

        Output:
            value(float) : currrent value on input
        '''

        # logging.debug('Read current value')
        text = self._visainstrument.ask('OD')
        return text

#     def do_set_range(self, val, mode=None):
#         '''
#         Set range to the specified value for the
#         designated mode. If mode=None, the current mode is assumed
#  
#         Input:
#             val (float)   : Range in specified units
#             mode (string) : mode to set property for. Choose from self._modes
#  
#         Output:
#             None
#         '''
#         logging.debug('Set range to %s' % val)
#         self._set_func_par_value(mode, 'RANG', val)

#     def do_get_range(self, mode=None):
#         '''
#         Get range for the specified mode.
#         If mode=None, the current mode is assumed.
# 
#         Input:
#             mode (string) : mode to set property for. Choose from self._modes
# 
#         Output:
#             range (float) : Range in the specified units
#         '''
#         logging.debug('Get range')
#         return float(self._get_func_par(mode, 'RANG'))

#     def do_set_digits(self, val, mode=None):
#         '''
#         Set digits to the specified value ?? Which values are alowed?
#         If mode=None the current mode is assumed
# 
#         Input:
#             val (int)     : Number of digits
#             mode (string) : mode to set property for. Choose from self._modes
# 
#         Output:
#             None
#         '''
#         logging.debug('Set digits to %s' % val)
#         self._set_func_par_value(mode, 'DIG', val)

#     def do_get_digits(self, mode=None):
#         '''
#         Get digits
#         If mode=None the current mode is assumed
# 
#         Input:
#             mode (string) : mode to set property for. Choose from self._modes
# 
#         Output:
#             digits (int) : Number of digits
#         '''
#         logging.debug('Getting digits')
#         return int(self._get_func_par(mode, 'DIG'))


    def do_set_mode(self, mode):
        '''
        Set the mode to the specified value

        Input:
            mode (string) : mode to be set. Choose from self._modes

        Output:
            None
        '''

        logging.debug('Set mode to %s', mode)
        if mode in self._modes:
            if mode == 'VOLT:DC':
                string = 'F1'
            elif mode == 'CURR:DC':
                string = 'F5'
            self._visainstrument.write(string)

            if mode.startswith('VOLT'):
                self._change_units('V')
            elif mode.startswith('CURR'):
                self._change_units('A')


        else:
            logging.error('invalid mode %s' % mode)

#         self.get_all()
            # Get all values again because some paramaters depend on mode

    def do_get_mode(self):
        '''
        Read the mode from the device

        Input:
            None

        Output:
            mode (string) : Current mode
        '''
        string = 'OS'
        logging.debug('Getting mode')
        ans = self._visainstrument.ask(string)
        return ans.strip('"')


# --------------------------------------
#           Internal Routines
# --------------------------------------

    def _change_units(self, unit):
        self.set_parameter_options('readval', units=unit)
#         self.set_parameter_options('readlastval', units=unit)
#         self.set_parameter_options('readnextval', units=unit)

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

    def _set_func_par_value(self, mode, par, val):
        '''
        For internal use only!!
        Changes the value of the parameter for the function specified

        Input:
            mode (string) : The mode to use
            par (string)  : Parameter
            val (depends) : Value

        Output:
            None
        '''
        mode = self._determine_mode(mode)
        string = ':%s:%s %s' % (mode, par, val)
        logging.debug('Set instrument to %s' % string)
        self._visainstrument.write(string)

#     def _get_func_par(self, mode, par):
#         '''
#         For internal use only!!
#         Reads the value of the parameter for the function specified
#         from the instrument
# 
#         Input:
#             func (string) : The mode to use
#             par (string)  : Parameter
# 
#         Output:
#             val (string) :
#         '''
#         mode = self._determine_mode(mode)
#         string = ':%s:%s?' % (mode, par)
#         ans = self._visainstrument.ask(string)
#         logging.debug('ask instrument for %s (result %s)' % \
#             (string, ans))
#         return ans

    def _measurement_start_cb(self, sender):
        '''
        Things to do at starting of measurement
        '''
        self.set_defaults()

    def _measurement_end_cb(self, sender):
        '''
        Things to do after the measurement
        '''
        self.output_off()

