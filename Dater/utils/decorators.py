#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Thread


def async(f):
    """ Decorator to make asynchronous functions """
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

