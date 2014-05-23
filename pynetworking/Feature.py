# -*- coding: utf-8 -*-
#


class Feature(object):
    def __init__(self, device, **kvargs):
        self._device = device
        self._opts = kvargs

    def load_config(self, config):  #pragma: no cover
        pass


