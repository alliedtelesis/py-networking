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


    def update(self, datetime=None, timezone=None):
        self._d.log_info("update")
        self._update_clock()

        if (datetime == None and timezone == None):
            raise KeyError('either datetime or timezone argument must be given')

        if (datetime != None):
            # set date and time
            hh = datetime.strftime('%H')
            mm = datetime.strftime('%M')
            ss = datetime.strftime('%S')
            day = datetime.strftime('%d')
            month = datetime.strftime('%b')
            year = datetime.strftime('%Y')

            #clock set 14:00:00 25 Jan 2008
            set_cmd = "clock set {0}:{1}:{2} {3} {4} {5}".format(hh, mm, ss, day, month, year)
            cmds = {'cmds':[{'cmd': set_cmd , 'prompt':'\#'}]}

            self._device.cmd(cmds, cache=False, flush_cache=True)

        if (timezone != None):
            # set the timezone
            loc_now = self._now()
            loc_dt = timezone.localize(loc_now)
            tz_name = loc_dt.strftime('%Z')
            offset = loc_dt.strftime('%z')

            sign = offset[0:1]
            if (offset[1] == '0'):
                off_h = offset[2:3]
            else:
                off_h = offset[1:3]
            off_m = offset[3:5]

            # clock timezone hours-offset [minutes minutes-offset] [zone acronym]
            if sign == '+':
                sign = ''
            tz_cmd = "clock timezone {0}{1} zone {2}".format(sign, off_h, tz_name)
            cmds = {'cmds':[{'cmd': 'conf' , 'prompt':'\(config\)\#'},
                            {'cmd': tz_cmd , 'prompt':'\(config\)\#'}
                           ]}

            # set the DST rules
            begin_dst = self._get_begin_dst(timezone, loc_dt)
            end_dst = self._get_end_dst(timezone, loc_dt)
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

                # clock summer-time recurring week day month hh:mm week day month hh:mm [offset offset] [zone acronym]
                st_cmd = "clock su r {0} {1} {2} {3} {4} {5} {6} {7} o {8} z {9}".format(bw, bd, bm, bt, ew, ed, em, et, om, tz_name)
                cmds['cmds'].append({'cmd': st_cmd , 'prompt':'\(config\)\#'})
            else:
                st_cmd = "no clock summer-time r"
                cmds['cmds'].append({'cmd': st_cmd , 'prompt':'\(config\)\#'})

            cmds['cmds'].append({'cmd': chr(26), 'prompt':'\#'})
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


    def _now(self):
        return datetime.now()


    def _update_clock(self):
        self._d.log_info("_update_clock")
        self._clock = OrderedDict()

        local_time = ''
        utc_time = ''
        timezone_name = 'UTC'
        timezone_offset = ''
        summertime_start = ''
        summertime_end = ''
        summertime_offset = ''
        tz_hours = 0
        the_year = self._now().year

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

        ifre1 = re.compile('(\r|'')\*(?P<local_time>[^\s]+)\s+'
                            '(?P<time_stuff>[^\s]+)\s+'
                            '\s+(?P<local_month>\w+)\s+'
                            '(?P<local_day>\d+)\s+'
                            '(?P<local_year>\d+)')

        ifre2 = re.compile('Offset\s+is\s+UTC(?P<offset_data>[^\s]+)\s+')

        ifre3 = re.compile('Acronym\s+is\s+(?P<timezone_name>\w+)')

        ifre4 = re.compile('Begins\s+at\s+(?P<bweek>\d+)\s+(?P<bday>\d+)\s+(?P<bmonth>\d+)\s+(?P<bhour>\d+):(?P<bmin>\d+).')

        ifre5 = re.compile('Ends\s+at\s+(?P<eweek>\d+)\s+(?P<eday>\d+)\s+(?P<emonth>\d+)\s+(?P<ehour>\d+):(?P<emin>\d+).')

        ifre6 = re.compile('Offset\s+is\s+(?P<summertime_offset>\d+)\s+minutes.')

        for line in self._device.cmd("show clock detail").split('\n'):
            self._d.log_debug("line parsed is: {0}".format(line))
            m = ifre1.match(line)
            if m:
                local_time = m.group('local_day') + '-' + m.group('local_month') + '-' + m.group('local_year') + ' ' + m.group('local_time')
                the_year = m.group('local_year')

            m = ifre2.match(line)
            if m:
                timezone_d = m.group('offset_data')
                timezone_s = timezone_d[0]
                timezone_h = timezone_d[1:3]
                if (len(timezone_h) == 1):
                    timezone_h = '0' + timezone_h
                timezone_offset = timezone_s + timezone_h + ':00'
                tz_hours = -int(timezone_d[0:3])

            m = ifre3.match(line)
            if m:
                timezone_name = m.group('timezone_name')

            m = ifre4.match(line)
            if m:
                summertime_start = self._get_summertime_str(m.group('bweek'),m.group('bday'),m.group('bmonth'),the_year) + m.group('bhour') + ':' + m.group('bmin') + ':00'

            m = ifre5.match(line)
            if m:
                summertime_end = self._get_summertime_str(m.group('eweek'),m.group('eday'),m.group('emonth'),the_year) + m.group('ehour') + ':' + m.group('emin') + ':00'

            m = ifre6.match(line)
            if m:
                summertime_offset = m.group('summertime_offset')

        loc_time_obj = datetime.strptime(local_time, "%d-%b-%Y %H:%M:%S")
        loc_time_delta = timedelta(hours=tz_hours)
        utc_time_obj = loc_time_obj + loc_time_delta
        utc_time = utc_time_obj.strftime("%d-%b-%Y %H:%M:%S")

        self._clock = {'local_time': local_time,
                       'utc_time': utc_time,
                       'timezone_name': timezone_name,
                       'timezone_offset': timezone_offset,
                       'summertime_start': summertime_start,
                       'summertime_end': summertime_end,
                       'summertime_offset': summertime_offset
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


    def _get_summertime_str(self, beweek, beday, bemonth, the_year):
        a_week = ['First ', 'Second ', 'Third ', 'Fourth ', 'Last ']
        a_day = ['Sunday ', 'Monday ', 'Tuesday ', 'Wednesday ', 'Thursday ', 'Friday ', 'Saturday ']
        strweek = a_week[int(beweek)-1]
        strday = a_day[int(beday)-1]
        ddd = datetime(int(the_year), int(bemonth), 1)
        str = strweek + strday + 'in ' + ddd.strftime("%B") + ' at '
        return str
