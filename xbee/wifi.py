"""
wifi.py

Christopher Lee, Ashima Research, 2013
lee@ashimaresearch.COM
This module provides and XBee WiFi (802.11) API library
"""
import struct
from xbee.base import XBeeBase

class XBeeWifi(XBeeBase):
    """
    Implements the XBee-WiFi API.
    
    Commands may be sent to a device by instansiating this class with
    a serial port object (see PySerial) and then calling the send
    method with the proper information specified by the API. Data may
    be read from a device syncronously by calling wait_read_frame. For
    asynchronous reads, see the definition of XBeeBase.
    """
    # Packets which can be sent to an XBee
    
    # Format: 
    #        {name of command:
    #           [{name:field name, len:field length, default: default value sent}
    #            ...
    #            ]
    #         ...
    #         }
    api_commands = {"at":
                        [{'name':'id',        'len':1,      'default':b'\x08'},
                         {'name':'frame_id',  'len':1,      'default':b'\x00'},
                         {'name':'command',   'len':2,      'default':None},
                         {'name':'parameter', 'len':None,   'default':None}],
                    "queued_at":
                        [{'name':'id',        'len':1,      'default':b'\x09'},
                         {'name':'frame_id',  'len':1,      'default':b'\x00'},
                         {'name':'command',   'len':2,      'default':None},
                         {'name':'parameter', 'len':None,   'default':None}],
                    "remote_at":
                        [{'name':'id',              'len':1,        'default':b'\x07'},
                         {'name':'frame_id',        'len':1,        'default':b'\x00'},
                         # dest_addr_long is 8 bytes (64 bits), so use an unsigned long long
                         #align IP address to low 32-bits, other bytes are 0
                         #eq. 192.168.0.100 = 0x00 0x00 0x00 0x00 0xc0 0xa8 0x00 0x64
                         {'name':'dest_addr',       'len':8,        'default':None},
                         {'name':'options',         'len':1,        'default':b'\x02'},
                         {'name':'command',         'len':2,        'default':None},
                         {'name':'parameter',       'len':None,     'default':None}],
                    "tx":
                        [{'name':'id',              'len':1,        'default':b'\x20'},
                         {'name':'frame_id',        'len':1,        'default':b'\x01'},
                         {'name':'dest_addr',       'len':4,        'default':None},
                         {'name':'dest_port',       'len':2,        'default':None},
                         {'name':'source_port',     'len':2,        'default':None},
                         {'name':'protocol',        'len':1,        'default':b'\x00'},
                         {'name':'options',         'len':1,        'default':b'\x00'},
                         {'name':'data',            'len':None,     'default':None}],
                     "tx_long_addr":
                        [{'name':'id',              'len':1,        'default':b'\x00'},
                         {'name':'frame_id',        'len':1,        'default':b'\x00'},
                         {'name':'dest_addr',       'len':8,        'default':None}, #low 32 bits is IP
                         {'name':'options',         'len':1,        'default':b'\x00'},
                         {'name':'data',            'len':None,     'default':None}]
                    }
           # Packets which can be received from an XBee
    
    # Format: 
    #        {id byte received from XBee:
    #           {name: name of response
    #            structure:
    #                [ {'name': name of field, 'len':length of field}
    #                  ...
    #                  ]
    #            parsing: [(name of field to parse,
    #                        function which accepts an xbee object and the
    #                            partially-parsed dictionary of data received
    #                            and returns bytes to replace the
    #                            field to parse's data with
    #                        )]},
    #           }
    #           ...
    #        }
    #           
    api_responses = {"\x80":
                           {'name':'rx',
                            'structure':
                               [{'name':'frame_id',    'len':1},
                                {'name':'source_addr', 'len':8}, # align IP in low 32 bits
                                {'name':'RSSI',        'len':2},
                                {'name':'options',     'len':1},
                                {'name':'rf_data',     'len':None}]},
                         "\x88":
                           {'name':'at_response',
                            'structure':
                               [{'name':'frame_id',    'len':1},
                                {'name':'command',     'len':2},
                                {'name':'status',      'len':1},
                                {'name':'parameter',   'len':None}]},
                         "\x8A":
                            {'name':'status',
                             'structure':
                                 [{'name':'status',      'len':1}]},
                         "\x89":
                            {'name':'tx_status',
                             'structure':
                                [{'name':'frame_id',    'len':1},
                                 {'name':'status',      'len':1}]},
                         "\x8F":
                            {'name':'rx_io', 
                             'structure':
                                [{'name':'source_addr', 'len':8},
                                 {'name':'RSSI',        'len':1},
                                 {'name':'options',     'len':1},
                                 {'name':'num_samples', 'len':1},
                                 {'name':'digital_mask','len':2},
                                 {'name':'analog_mask', 'len':1},
                                 {'name':'digital_samples', 'len':2},
                                 {'name':'analog_sample', 'len':2}]},
                        "\x87":
                           {'name':'remote_at_response',
                             'structure':
                               [{'name':'frame_id',        'len':1},
                                {'name':'source_addr',     'len':8}, #low 32 bit is IP
                                {'name':'command',         'len':2},
                                {'name':'status',          'len':1},
                                {'name':'parameter',       'len':None}]},
                        "\xB0":
                           {'name':'rx',
                             'structure':
                               [{'name':'source_addr',      'len':4}, 
                                {'name':'dest_port',        'len':2},
                                {'name':'source_port',      'len':2},
                                {'name':'protocol',         'len':1},
                                {'name':'status',           'len':1},
                                {'name':'rf_data',          'len':None}]}
                                }

    def __init__(self, *args, **kwargs):
        # Call the super class constructor to save the serial port
        super(XBeeWifi, self).__init__(*args, **kwargs)
                        