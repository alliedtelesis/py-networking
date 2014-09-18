# -*- coding: utf-8 -*-
from pynetworking import Feature
from pprint import pformat
import re
import json
import os
import pytz
from datetime import datetime, timedelta
from pytz import timezone

class awp_clock(Feature):
    """
    Clock feature implementation for AWP
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        self._d = device
        self._d.log_debug("loading feature")


    def load_config(self, config):
        self._d.log_info("loading config")


    def create(self, name, protocol='http', text='', filename=''):
        self._d.log_info("create file {0}".format(name))


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

            self._d.log_info("Setting time={0}:{1}:{2}, date={3}/{4}/{5}".format(hh, mm, ss, day, month, year))

            #clock set 14:00:00 25 Jan 2008
            cmd = "clock set {0}:{1}:{2} {3} {4} {5}".format(hh, mm, ss, day, month, year)
            self._d.log_info("Command is {0}".format(cmd))

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

            if sign == '-':
                sign_key = 'minus'
            else:
                sign_key = 'plus'

            # clock timezone <timezone-name> {plus|minus} <0-12>
            cmd = "clock timezone {0} {1} {2}:{3}".format(tz_name, sign_key, off_h, off_m)
            self._d.log_info("Command is {0}".format(cmd))

            # set the DST rules
            begin_dst = self._get_begin_dst(tz, loc_dt)
            end_dst = self._get_end_dst(tz, loc_dt)
            if (begin_dst != None and end_dst != None):
                hh = int(begin_dst.strftime('%H')) - 1
                mm = begin_dst.strftime('%M')
                bt = "{0}:{1}".format(hh,mm)
                bd = begin_dst.strftime('%a')
                bw = str((int(begin_dst.strftime('%d')) - 1)/7 + 1)
                bm = begin_dst.strftime('%b')

                hh = int(end_dst.strftime('%H'))
                mm = end_dst.strftime('%M')
                et = "{0}:{1}".format(hh,mm)
                ed = end_dst.strftime('%a')
                ew = str((int(end_dst.strftime('%d')) - 1)/7 + 1)
                em = end_dst.strftime('%b')

                om = '60'

                self._d.log_info("Setting timezone {0} with {1} {2} {3} {4} {5} {6} {7} {8} {9}".format(tz_name, bw, bd, bm, bt, ew, ed, em, et, om))

                # clock summer-time <zone-name> recurring <start-week> <start-day> <start-month> <start-time> <end-week> <end-day> <end-month> <end-time> <1-180>
                cmd = "clock summer-time {0} recurring {1} {2} {3} {4} {5} {6} {7} {8} {9}".format(tz_name, bw, bd, bm, bt, ew, ed, em, et, om)
                self._d.log_info("Command is {0}".format(cmd))


    def delete(self, file_name):
        self._d.log_info("remove {0}".format(file_name))


    def items(self):
        self._update_file()
        return self._file.items()


    def keys(self):
        self._update_file()
        return self._file.keys()


    def _get_begin_dst(self, tz, dt):
        tt = tz._utc_transition_times
        offset = dt.hour
        year = dt.year

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
                return ret_tt

        return None


    def _get_end_dst(self, tz, dt):
        tt = tz._utc_transition_times
        offset = dt.hour
        year = dt.year

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
                return ret_tt

        return None


