#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template
from Dater import app


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/error.html', error=e), e.code
    # return render_template('errors/404.html'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/error.html', error=e), e.code
    # return render_template('errors/403.html'), 403


@app.errorhandler(410)
def gone(e):
    return render_template('errors/error.html', error=e), e.code
    # return render_template('errors/410.html'), 410


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('errors/error.html', error=e), e.code
    # return render_template('errors/500.html'), 500