# itest.py driver for AMI_430 Voltage source
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

class AMI_430(Instrument):
    '''
    This is the driver for the AMI_430 system

    Usage:
    Initialize with
    <name> = instruments.create('<name>', 'AMI_430',
        address='<GBIP address>',
        reset=<bool>,
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
        logging.info('Initializing instrument AMI_430 Magnet controller')
        Instrument.__init__(self, name, tags=['physical'])

        # Add some global constants
        self._address = address
        self._visainstrument = visa.instrument(self._address, term_chars='\r\n')
        self._ramprateunits = ['s', 'min']
        self._ramprateunit  = self._ramprateunits[1]
        self._fieldunits = ['kiloGauss', 'Tesla']
        self._fieldunit  = self._fieldunits[0]
        self._rampstates = ['RAMPING', 'HOLDING', 'PAUSED', 'MANUAL UP','MANUAL DOWN', 'ZEROING CURRENT', 'Quench detected!', 'At ZERO', 'Heating persistent switch', 'Cooling persistent switch']
        self._rampstate  = self._rampstates[2]
        self._supplymodes = ['+0 to +5 V', '+0 to +10 V', '-5 to +5 V', '-10 to +10 V', '+0 to -5 V', '+0 to +8 V']
        self._supplymode  = self._supplymodes[0]


        # Add parameters to wrapper
#         self.add_parameter('range',
#             flags=Instrument.FLAG_GETSET,
#             units='', minval=0.1, maxval=1000, type=types.FloatType)
#         self.add_parameter('trigger_source',
#             flags=Instrument.FLAG_GETSET,
#             units='')

        # Add functions to wrapper
        self.add_function('reset')
        self.add_function('get_all')
        self.add_function('get_target_field')
        self.add_function('set_target_field')
        self.add_function('set_ramp_auto')
        self.add_function('set_ramp_pause')
        self.add_function('set_ramp_zero')

       

        # Connect to measurement flow to detect start and stop of measurement
#         qt.flow.connect('measurement-start', self._measurement_start_cb)
#         qt.flow.connect('measurement-end', self._measurement_end_cb)


        if reset:
            self.reset()
        self._visainstrument.read()
        self._visainstrument.read()
        self.set_field_unit('Tesla')
        self.set_ramprate_unit('s')
        self.get_all()

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
        logging.debug('Resetting instrument AMI_430')
        self._visainstrument.write('*RST')

    def get_all(self):
        '''
        Reads all relevant parameters from instrument

        Input:
            None

        Output:
            None
        '''
        logging.info('Get all relevant data from device AMI430')
#         self.get_supply_type()
        self.get_supply_mode()
#         self.get_stability()
        self.get_coilconst()
        self.get_current_limit()
        self.get_pswitch_state()
        self.get_field_unit()
        self.get_ramprate_unit()
        self.get_ramprate_current()
        self.get_ramp_state()

 
#     def get_supply_type(self):
#         tempsupptype = int(self._visainstrument.ask('SUPPly:TYPE?'))
#         logging.debug('Read AMI_430 coil constant as %f' % tempcoilc)
#         
#         self._supptype = self._supptypes[tempsupptype]
#         logging.debug('Read AMI_430 supply type as %s.' % self._supptype)
#         return self._supptype
    
    def get_field(self):
        """
        Returns the current B field
        """
        return float(self._visainstrument.ask("CURRent:MAGnet?"))*self.get_coilconst()
     
    def get_supply_mode(self):
        tempsuppmode = int(self._visainstrument.ask('SUPPly:MODE?'))
        self._suppmode = self._supplymodes[tempsuppmode]
        logging.debug('Read AMI_430 supply mode as %s.' % self._suppmode)
        return self._suppmode


    def get_coilconst(self):
        tempcoilc = float(self._visainstrument.ask('COILconst?'))
        logging.debug('Read AMI_430 coil constant as %f %s/A.' % (tempcoilc, self._fieldunit))
        return tempcoilc

    def set_coilconst(self, val):
        if val <= 0:
            logging.error('AMI_430 coil constant has to be a non-zero positive value!')
        else:
            self._visainstrument.write('CONFigure:COILconst %f' % val)
            logging.debug('Set AMI_430 coil constant to %f' % val)
            
    def get_current_limit(self):
        tempcurrlim = float(self._visainstrument.ask('CURRent:LIMit?'))
        logging.debug('Read AMI_430 current limit as %f A' % tempcurrlim)
        return tempcurrlim

    def set_current_limit(self, val):
        if val <= 0:
            logging.error('AMI_430 current limit has to be a non-zero positive value!')
        else:
            self._visainstrument.write('CONFigure:CURRent:LIMit %f' % val)
            logging.debug('Set AMI_430 current limit to %f A' % val)

    def get_magnet_current_rating(self):
        tempcurrrate = float(self._visainstrument.ask('CURRent:RATING?'))
        logging.debug('Read AMI_430 magnet current rating as %f A' % tempcurrrate)
        return tempcurrrate

    def set_magnet_current_rating(self, val):
        if val <= 0:
            logging.error('AMI_430 magnet current rating has to be a non-zero positive value!')
        else:
            self._visainstrument.write('CONFigure:CURRent:RATING %f' % val)
            logging.debug('Set AMI_430 magnet current rating to %f A' % val)
            
    def get_pswitch_state(self):
        pswitchstate = ['not installed', 'installed']
        temppswitchstate = int(self._visainstrument.ask('PSwitch:INSTalled?'))
        logging.debug('Read AMI_430 persistent switch state as %s' % pswitchstate[temppswitchstate])
        return temppswitchstate

    def get_ramprate_unit(self):
        temprrunit = int(self._visainstrument.ask('RAMP:RATE:UNITS?'))
        self._ramprateunit = self._ramprateunits[temprrunit]
        logging.debug('Read AMI_430 ramp rate unit as %s.' % self._ramprateunit)
        return self._ramprateunit

    def set_ramprate_unit(self, val):
        if val == 0 or val == 's' or val == 'second':
            temprrunit = 0
        elif val == 1 or val == 'min' or val == 'minute':
            temprrunit = 1
        else:
            logging.error('Set AMI_430 ramp rate unit error! Wrong unit!')
        
        self._visainstrument.write('CONFigure:RAMP:RATE:UNITS %i' % temprrunit)
        self._ramprateunit = self._ramprateunits[temprrunit]
        logging.debug('Set AMI_430 ramp rate unit to %s .' % self._ramprateunit)

    def get_rampsegments(self):
        rampratesegm = int(self._visainstrument.ask('RAMP:RATE:SEGments?'))
        logging.debug('Read AMI_430 has %s ramp segments.' % rampratesegm)
        return rampratesegm

    def set_rampsegments(self, val):
        self._visainstrument.write('CONFigure:RAMP:RATE:SEGments %i' % val)
        logging.debug('Set AMI_430 with %s ramp segments.' % val)
        
    def get_field_unit(self):
        tempfunit = int(self._visainstrument.ask('FIELD:UNITS?'))
        self._fieldunit = self._fieldunits[tempfunit]
        logging.debug('Read AMI_430 field unit as %s.' % self._fieldunit)
        return self._fieldunit

    def set_field_unit(self, val):
        if val == 0 or val == 'kG' or val == 'kiloGauss':
            tempfunit = 0
        elif val == 1 or val == 'T' or val == 'Tesla':
            tempfunit = 1
        else:
            logging.error('Set AMI_430 field unit error! Wrong unit!')
        
        self._visainstrument.write('CONFigure:FIELD:UNITS %i' % tempfunit)
        self._fieldunit = self._fieldunits[tempfunit]
        logging.debug('Set AMI_430 field unit to %s .' % self._fieldunit)

    def get_voltage_limit(self):
        tempvoltlim = float(self._visainstrument.ask('VOLTage:LIMit?'))
        logging.debug('Read AMI_430 ramping voltage limit as %f A' % tempvoltlim)
        return tempvoltlim

    def set_voltage_limit(self, val):
        if val <= 0:
            logging.error('AMI_430 ramping voltage limit has to be a non-zero positive value!')
        else:
            self._visainstrument.write('CONFigure:VOLTage:LIMit %f' % val)
            logging.debug('Set AMI_430 ramping voltage limit to %f V' % val)

    def get_target_current(self):
        temptargcurr = float(self._visainstrument.ask('CURRent:TARGet?'))
        logging.debug('Read AMI_430 target current as %f A' % temptargcurr)
        return temptargcurr

    def set_target_current(self, val):
        self._visainstrument.write('CONFigure:FIELD:TARGet %f' % val)
        logging.debug('Set AMI_430 target current to %f A.' % val)

    def get_target_field(self):
        temptargfield = float(self._visainstrument.ask('FIELD:TARGet?'))
        logging.debug('Read AMI_430 target field as %f %s .' % (temptargfield, self._fieldunit))
        return temptargfield

    def set_target_field(self, val):
        self._visainstrument.write('CONFigure:FIELD:TARGet %f' % val)
        logging.debug('Set AMI_430 target field to %f %s .' % (val, self._fieldunit))

    def get_ramprate_current(self, segval=1):
        temprrcurr = float(self._visainstrument.ask('RAMP:RATE:CURRent:%i?' % segval).split(',')[0])
        logging.debug('Read AMI_430 current ramp rate of segment %i as %f A/%s .' % (segval, temprrcurr, self._ramprateunit))
        return temprrcurr

    def set_ramprate_current(self, segval=1, currrate=2, upperbound = 30.3):
        self._visainstrument.write('CONFigure:RAMP:RATE:CURRent %i,%f,%f' % (segval, currrate, upperbound))
        logging.debug('Set AMI_430 current ramp rate of segment %i to %f A/%s .' % (segval, currrate, self._ramprateunit))

    def get_ramprate_field(self, segval=1):
        temprrfield = float(self._visainstrument.ask('RAMP:RATE:FIELD:%i?' % segval).split(',')[0])
        logging.debug('Read AMI_430 field ramp rate of segment %i as %f %s/%s .' % (segval, temprrfield, self._fieldunit, self._ramprateunit))
        return temprrfield

    def set_ramprate_field(self, segval=1, fieldrate=0.0132, upperbound = 0.2):
        self._visainstrument.write('CONFigure:RAMP:RATE:FIELD %i,%f,%f' % (segval, fieldrate, upperbound))
        logging.debug('Set AMI_430 field ramp rate of segment %i to %f %s/%s .' % (segval, fieldrate, self._fieldunit, self._ramprateunit))

    def set_ramp_auto(self):
        self._visainstrument.write('RAMP')
        logging.debug('Set AMI_430 ramp mode to auto ramp.')
        
    def set_ramp_pause(self):
        self._visainstrument.write('PAUSE')
        logging.debug('Set AMI_430 ramp mode to pause.')
        
    def set_ramp_manualup(self):
        self._visainstrument.write('INCR')
        logging.debug('Set AMI_430 ramp mode to manual up.')
        
    def set_ramp_manualdown(self):
        self._visainstrument.write('DECR')
        logging.debug('Set AMI_430 ramp mode to manual down.')
        
    def set_ramp_zero(self):
        self._visainstrument.write('ZERO')
        logging.debug('Set AMI_430 ramp mode to zero.')
        
    def get_ramp_state(self):
        temprampstate = int(self._visainstrument.ask('STATE?'))
        self._rampstate = self._rampstates[temprampstate-1]
        logging.debug('Read AMI_430 ramp state as %s' % self._rampstate)
        return self._rampstate
                    
    def get_stability(self):
        tempstab = float(self._visainstrument.ask('STABility?'))
        logging.debug('Read AMI_430 stability as %f percent.' % (tempstab))
        return temprrcurr

    def set_stability(self, stabset = 0):
        self._visainstrument.write('CONFigure:STABility %f' % (stabset))
        logging.debug('Set AMI_430 stability to %f percent.' % (stabset))
# --------------------------------------
#           internal functions
# --------------------------------------

# --------------------------------------
#           parameters
# --------------------------------------

# --------------------------------------
#           Internal Routines
# --------------------------------------   