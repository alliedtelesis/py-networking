from urlparse import urlparse


class Device(object):
    def __init__(self, uri, type='auto'):
        o = urlparse(uri)
        if o.scheme not in ('telnet','scp'):
            raise ValueError("Unsupported protocol "+o.scheme)


    def cmd(self, cmd):
        return ""

    def config(self):
        return ""
