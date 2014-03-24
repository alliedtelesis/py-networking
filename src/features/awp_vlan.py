# -*- coding: utf-8 -*-
from pynetworking import Feature

class awp_vlan(Feature):
    """
    Vlan feature implementation for AWP
    """
    def __init__(self, device, **kvargs):
        Feature.__init__(self, device, **kvargs)
        pass

    def create(self, id, name=''):
        print "create vlan {0} on awp".format(id)

    def delete(self, id):
        pass


