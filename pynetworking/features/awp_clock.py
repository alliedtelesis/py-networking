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
            raise KeyError('either dt or timezone argument must be given')

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

                # # DST begin rules
                # go_in_the_day_before = False
                # go_in_the_day_after = False
                #
                # mm = begin_dst.strftime('%M')
                # hh = int(begin_dst.strftime('%H'))
                #
                # if sign == '-':
                #     if (hh - int(off_h) < 0):
                #         go_in_the_day_before = True
                # else:
                #     if (hh + int(off_h) >= 24):
                #         go_in_the_day_after = True
                #
                # if sign == '-':
                #     if (go_in_the_day_before == False):
                #          hh = hh - int(off_h)
                #     else:
                #          hh = hh + 24 - int(off_h)
                # else:
                #     if (go_in_the_day_after == False):
                #         hh = hh + int(off_h)
                #     else:
                #         hh = hh + int(off_h) - 24
                # bt = "{0}:{1}".format(hh,mm)
                #
                # dd = int(begin_dst.strftime('%w'))
                # ww = int(begin_dst.strftime('%d'))
                # if sign == '-':
                #     if (go_in_the_day_before == True):
                #          if (dd - 1 < 0):
                #              dd = 6
                #              ww = ww - 1
                #          else:
                #              dd = dd - 1
                # else:
                #     if (go_in_the_day_after == True):
                #          if (dd + 1 > 6):
                #              dd = 0
                #              ww = ww + 1
                #          else:
                #              dd = dd + 1
                # bd = str(dd)
                # bw = str(ww)
                #
                # bm = begin_dst.strftime('%b')
                #
                # # DST end rules
                # go_in_the_day_before = False
                # go_in_the_day_after = False
                #
                # mm = end_dst.strftime('%M')
                # hh = int(end_dst.strftime('%H'))
                #
                # if sign == '-':
                #     if (hh - int(off_h) < 0):
                #         go_in_the_day_before = True
                # else:
                #     if (hh + int(off_h) >= 24):
                #         go_in_the_day_after = True
                #
                # if sign == '-':
                #     if (go_in_the_day_before == False):
                #          hh = hh - int(off_h)
                #     else:
                #          hh = hh + 24 - int(off_h)
                # else:
                #     if (go_in_the_day_after == False):
                #         hh = hh + int(off_h)
                #     else:
                #         hh = hh + int(off_h) - 24
                # et = "{0}:{1}".format(hh,mm)
                #
                # em = end_dst.strftime('%b')
                #
                # dd = int(end_dst.strftime('%a'))
                # ww = int(end_dst.strftime('%d'))
                # if sign == '-':
                #     if (go_in_the_day_before == True):
                #          if (dd - 1 < 0):
                #              dd = 6
                #              ww = ww - 1
                #          else:
                #              dd = dd - 1
                # else:
                #     if (go_in_the_day_after == True):
                #          if (dd + 1 > 6):
                #              dd = 0
                #              ww = ww + 1
                #          else:
                #              dd = dd + 1
                # ed = str(dd)
                # ew = str(ww)

                # bw = str((int(begin_dst.strftime('%d')) - 1)/7 + 1)
                # bd = begin_dst.strftime('%a')
                # bm = begin_dst.strftime('%b')
                # hh = int(begin_dst.strftime('%H'))
                # mm = begin_dst.strftime('%M')
                # if sign == '-':
                #     if (hh + int(off_h) >= 0):
                #         hh -= int(off_h)
                #     else:
                #         hh = hh + 24 - int(off_h)
                # else:
                #     if (hh + int(off_h) < 24):
                #         hh += int(off_h)
                #     else:
                #         hh = hh + int(off_h) - 24
                #         if (int(begin_dst.strftime('%d')) - 1)/7 < 0:
                #             bw = '6'
                #             bd = str(int(bd)-1)
                #         else:
                #             bw = str((int(begin_dst.strftime('%d')) - 1)/7)
                # bt = "{0}:{1}".format(hh,mm)
                #
                # ew = str((int(end_dst.strftime('%d')) - 1)/7 + 1)
                # ed = end_dst.strftime('%a')
                # em = end_dst.strftime('%b')
                # hh = int(end_dst.strftime('%H'))
                # mm = end_dst.strftime('%M')
                # if sign == '-':
                #     hh -= int(off_h) + 1
                # else:
                #     if (hh + int(off_h) + 1 < 24):
                #         hh += int(off_h) + 1
                #     else:
                #         hh = hh + int(off_h) + 1 - 24
                #         if (int(begin_dst.strftime('%d')) - 1)/7 + 1 < 6:
                #             bw = str((int(begin_dst.strftime('%d')) - 1)/7 + 2)
                #         else:
                #             bw = '0'
                #             bd = str(int(bd)+1)
                #
                # et = "{0}:{1}".format(hh,mm)
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
        self._d.log_info("offset {0} year {1}".format(offset, year))

        for index in range(len(tt)):
            if tt[index].year == year:
                # self._d.log_info("index is {0}".format(index))
                # self._d.log_info("begin with {0}".format(tt[index]))
                utc = pytz.utc
                utc_dt = datetime(tt[index].year, tt[index].month, tt[index].day, tt[index].hour + 1, tt[index].minute + 1, tzinfo = utc)
                temp_dt = utc_dt.astimezone(tz)
                if temp_dt.dst() == timedelta(0):
                    continue
                self._d.log_info("index is {0}".format(index))
                self._d.log_info("begin with {0}".format(tt[index]))
                a_tt = datetime(tt[index].year, tt[index].month, tt[index].day, tt[index].hour, tt[index].minute, tzinfo = utc)
                ret_tt = a_tt.astimezone(tz)
                return ret_tt

        return None


    def _get_end_dst(self, tz, dt):
        tt = tz._utc_transition_times
        offset = dt.hour
        year = dt.year
        self._d.log_info("offset {0} year {1} {2}".format(offset, year, len(tt)))

        for index in range(len(tt)):
            if tt[index].year == year:
                # self._d.log_info("index is {0}".format(index))
                # self._d.log_info("end with {0}".format(tt[index]))
                utc = pytz.utc
                utc_dt = datetime(tt[index].year, tt[index].month, tt[index].day, tt[index].hour + 1, tt[index].minute + 1, tzinfo = utc)
                temp_dt = utc_dt.astimezone(tz)
                if temp_dt.dst() != timedelta(0):
                    continue
                self._d.log_info("index is {0}".format(index))
                self._d.log_info("end with {0}".format(tt[index]))
                a_tt = datetime(tt[index].year, tt[index].month, tt[index].day, tt[index].hour + 1, tt[index].minute, tzinfo = utc)
                ret_tt = a_tt.astimezone(tz)
                return ret_tt

        return None


