# -*- coding: utf-8 -*-
from pynetworking import Feature
from pprint import pformat
import re
import json
import pytz
from datetime import datetime, timedelta
from pytz import timezone
try:
    from collections import OrderedDict
except ImportError: #pragma: no cover
    from ordereddict import OrderedDict


class ats_clock(Feature):
    """
    Clock feature implementation for ATS
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._d = device
        self._d._clock = {}
        self._d.log_debug("loading feature")


    def load_config(self, config):
        self._d.log_info("loading config")


    def update(self, dt=None, tz=None):
        self._d.log_info("update")

        if (dt == None and tz == None):
            raise KeyError('either datetime or timezone argument must be given')

        if (dt != None):
            # set date and time
            hh = dt.strftime('%H')
            mm = dt.strftime('%M')
            ss = dt.strftime('%S')
            day = dt.strftime('%d')
            month = dt.strftime('%b')
            year = dt.strftime('%Y')

            self._d.log_info("Setting time={0}:{1}:{2}, date={3}-{4}-{5}".format(hh, mm, ss, day, month, year))

            #clock set 14:00:00 25 Jan 2008
            set_cmd = "clock set {0}:{1}:{2} {3} {4} {5}".format(hh, mm, ss, day, month, year)
            self._d.log_info("Command is {0}".format(set_cmd))
            cmds = {'cmds':[{'cmd': 'conf'  , 'prompt':'\(config\)\#'},
                            {'cmd': set_cmd , 'prompt':'\(config\)\#'},
                            {'cmd': chr(26) , 'prompt':'\#'},
                           ]}

            self._device.cmd(cmds, cache=False, flush_cache=True)

        if (tz != None):
            # set the timezone
            loc_now = datetime.now()
            loc_dt = tz.localize(loc_now)
            tz_name = loc_dt.strftime('%Z')
            offset = loc_dt.strftime('%z')

            sign = offset[0:1]
            if (offset[1] == '0'):
                off_h = offset[2:3]
            else:
                off_h = offset[1:3]
            off_m = offset[3:5]

            self._d.log_info("Setting timezone {0} with offset {1}{2}:{3}".format(tz_name, sign, off_h, off_m))

            # clock timezone hours-offset [minutes minutes-offset] [zone acronym]
            if sign == '+':
                sign = ''
            tz_cmd = "clock timezone {0}{1} zone {2}".format(sign, off_h, tz_name)
            self._d.log_info("Command is {0}".format(tz_cmd))

            # set the DST rules
            begin_dst = self._get_begin_dst(tz, loc_dt)
            end_dst = self._get_end_dst(tz, loc_dt)
            if (begin_dst != None and end_dst != None):
                hh = int(begin_dst.strftime('%H')) - 1
                mm = begin_dst.strftime('%M')
                bt = "{0}:{1}".format(hh,mm)
                bd = begin_dst.strftime('%a')
                bd = bd.lower()
                bw = str((int(begin_dst.strftime('%d')) - 1)/7 + 1)
                bm = begin_dst.strftime('%b')
                bm = bm.lower()

                hh = int(end_dst.strftime('%H'))
                mm = end_dst.strftime('%M')
                et = "{0}:{1}".format(hh,mm)
                ed = end_dst.strftime('%a')
                ed = ed.lower()
                ew = str((int(end_dst.strftime('%d')) - 1)/7 + 1)
                em = end_dst.strftime('%b')
                em = em.lower()

                om = '60'

                self._d.log_info("Setting timezone {0} with {1} {2} {3} {4} {5} {6} {7} {8} {9}".format(tz_name, bw, bd, bm, bt, ew, ed, em, et, om))

                # clock summer-time recurring week day month hh:mm week day month hh:mm [offset offset] [zone acronym]
                st_cmd = "clock su r {0} {1} {2} {3} {4} {5} {6} {7} o {8} z {9}".format(bw, bd, bm, bt, ew, ed, em, et, om, tz_name)
                self._d.log_info("Command is {0}".format(st_cmd))
            else:
                st_cmd = "no clock summer-time r"

            cmds = {'cmds':[{'cmd': 'conf' , 'prompt':'\(config\)\#'},
                            {'cmd': tz_cmd , 'prompt':'\(config\)\#'},
                            {'cmd': st_cmd , 'prompt':'\(config\)\#'},
                            {'cmd': chr(26), 'prompt':'\#'},
                           ]}

            self._device.cmd(cmds, cache=False, flush_cache=True)

        self._update_clock()


    def items(self):
        self._update_clock()
        return self._clock.items()


    def keys(self):
        self._update_clock()
        return self._clock.keys()


    def __getitem__(self, id):
        self._update_clock()
        if id in self._clock.keys():
            return self._clock[id]
        raise KeyError('data {0} does not exist'.format(id))


    def _update_clock(self):
        self._d.log_info("_update_clock")
        self._clock = OrderedDict()

        # *11:11:59 AEST(UTC+10)  Oct 1 2006
        # No time source
        #
        # Time zone:
        # Acronym is AEST
        # Offset is UTC+10
        #
        # Summertime:
        # Acronym is AEST
        # Recurring every year.
        # Begins at 01 01 10 02:00.
        # Ends at 01 01 04 03:00.
        # Offset is 60 minutes.
        ifre1 = re.compile('')

        # *09:13:23 CST(UTC+8)  Oct 1 2006
        # No time source
        #
        # Time zone:
        # Acronym is CST
        # Offset is UTC+8
        ifre2 = re.compile('')

        output = self._device.cmd("show clock details")
        self._d.log_info("Output: {0}".format(output))
        m = ifre1.match(output)
        if m:
            self._d.log_info("three!")
            self._clock = {'local_time': m.group('local_time'),
                           'utc_time': '',
                           'timezone_name': m.group('tz_name'),
                           'timezone_offset': m.group('timezone_offset'),
                           'summertime_start': m.group('st_start'),
                           'summertime_end': m.group('st_stop'),
                           'summertime_offset': m.group('st_offset')
                          }
        else:
            m = ifre2.match(output)
            self._d.log_info("one")
            if m:
                self._d.log_info("two!")
                self._clock = {'local_time': m.group('local_time') + ' ' + m.group('date'),
                               'utc_time': m.group('local_time') + ' ' + m.group('date'),
                               'timezone_name': m.group('timezone_name'),
                               'timezone_offset': m.group('timezone_offset'),
                               'summertime_start': '',
                               'summertime_end': '',
                               'summertime_offset': ''
                              }
        self._d.log_debug("File {0}".format(pformat(json.dumps(self._clock))))


    def _get_begin_dst(self, tz, dt):
        tt = tz._utc_transition_times
        offset = dt.hour
        year = dt.year
        ret = None

        for index in range(len(tt)):
            if tt[index].year >= year:
                # search the maximum day value so to detect whether or not the day is in week 5
                utc = pytz.utc
                utc_dt = datetime(tt[index].year, tt[index].month, tt[index].day, tt[index].hour + 1, tt[index].minute + 1, tzinfo = utc)
                temp_dt = utc_dt.astimezone(tz)
                if temp_dt.dst() == timedelta(0) or tt[index+2].day > tt[index].day or tt[index-2].day > tt[index].day:
                    continue
                self._d.log_debug("DST start is {0} (index {1})".format(tt[index], index))
                a_tt = datetime(tt[index].year, tt[index].month, tt[index].day, tt[index].hour, tt[index].minute, tzinfo = utc)
                ret_tt = a_tt.astimezone(tz)
                ret = ret_tt
                break

        return ret


    def _get_end_dst(self, tz, dt):
        tt = tz._utc_transition_times
        offset = dt.hour
        year = dt.year
        ret = None

        for index in range(len(tt)):
            if tt[index].year >= year:
                # search the maximum day value so to detect whether or not the day is in week 5
                utc = pytz.utc
                utc_dt = datetime(tt[index].year, tt[index].month, tt[index].day, tt[index].hour + 1, tt[index].minute + 1, tzinfo = utc)
                temp_dt = utc_dt.astimezone(tz)
                if temp_dt.dst() != timedelta(0) or tt[index+2].day > tt[index].day or tt[index-2].day > tt[index].day:
                    continue
                self._d.log_debug("DST end is {0} (index {1})".format(tt[index], index))

                # adjustment due to DST time
                a_tt = datetime(tt[index].year, tt[index].month, tt[index].day, tt[index].hour + 1, tt[index].minute, tzinfo = utc)
                ret_tt = a_tt.astimezone(tz)
                ret = ret_tt
                break

        return ret


