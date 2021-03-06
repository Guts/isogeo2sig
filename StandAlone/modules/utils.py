# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import (absolute_import, print_function, unicode_literals)
# ----------------------------------------------------------------------------
# Name:         isogeo2office useful methods
# Purpose:      externalize util methods from isogeo2office
#
# Author:       Julien Moura (@geojulien)
#
# Python:       2.7.x
# Created:      14/08/2016
# Updated:      28/11/2016
# ----------------------------------------------------------------------------

# ############################################################################
# ########## Libraries #############
# ##################################

# Standard library
from ConfigParser import SafeConfigParser
from itertools import izip_longest
import logging
from os import access, path, R_OK
import re
import subprocess
from sys import platform as opersys
from webbrowser import open_new_tab
from xml.sax.saxutils import escape  # '<' -> '&lt;'

# Depending on operating system
if opersys == 'win32':
    u""" windows """
    from os import startfile        # to open a folder/file
else:
    pass

# ############################################################################
# ########## Classes ###############
# ##################################


class IsogeoToGIS_Utils(object):
    """isogeo2office utils methods class."""

    def __init__(self):
        """instanciating method
        """
        super(IsogeoToGIS_Utils, self).__init__()

        # ------------ VARIABLES ---------------------


    # MISCELLANOUS -----------------------------------------------------------

    def open_urls(self, li_url):
        """Open URLs in new tabs in the default brower.

        It waits a few seconds between the first and the next URLs
        to handle case when the webbrowser is not yet opened.
        """
        x = 1
        for url in li_url:
            if x > 1:
                sleep(3)
            else:
                pass
            open_new_tab(url)
            x += 1

        # end of method
        return

    def open_dir_file(self, target):
        """Open a file or a directory in the explorer of the operating system."""
        # check if the file or the directory exists
        if not path.exists(target):
            raise IOError('No such file: {0}'.format(target))

        # check the read permission
        if not access(target, R_OK):
            raise IOError('Cannot access file: {0}'.format(target))

        # open the directory or the file according to the os
        if opersys == 'win32':  # Windows
            proc = startfile(path.realpath(target))

        elif opersys.startswith('linux'):  # Linux:
            proc = subprocess.Popen(['xdg-open', target],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

        elif opersys == 'darwin':  # Mac:
            proc = subprocess.Popen(['open', '--', target],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

        else:
            raise NotImplementedError(
                "Your `%s` isn't a supported operating system`." % opersys)

        # end of function
        return proc

    # SETTINGS ---------------------------------------------------------------

    def settings_load(self, config_file=r"../settings.ini"):
        """Load settings from the ini file."""
        config = SafeConfigParser()
        config.read(r"settings.ini")
        settings_dict = {s: dict(config.items(s)) for s in config.sections()}

        logging.info("Settings loaded from: {}".format(config_file))

        # end of method
        return settings_dict

    def settings_save(self, config_file=r"../settings.ini"):
        """Save settings into the ini file."""
        config = SafeConfigParser()
        config.read(path.realpath(config_file))
        # new values
        config.set('auth', 'app_id', self.app_id)
        config.set('auth', 'app_secret', self.app_secret)
        config.set('basics', 'out_folder', path.realpath(self.out_fold_path.get()))
        config.set('basics', 'excel_out', self.output_xl.get())
        config.set('basics', 'excel_opt', str(self.opt_excel.get()))
        config.set('basics', 'word_opt', str(self.opt_word.get()))
        config.set('basics', 'word_tpl', self.tpl_input.get())
        config.set('basics', 'word_out_prefix', str(self.out_word_prefix.get()))
        config.set('basics', 'word_opt_id', str(self.word_opt_id.get()))
        config.set('basics', 'word_opt_date', str(self.word_opt_date.get()))
        config.set('basics', 'xml_opt', str(self.opt_xml.get()))
        config.set('basics', 'xml_out_prefix', str(self.out_xml_prefix.get()))
        config.set('basics', 'xml_opt_id', str(self.xml_opt_id.get()))
        config.set('basics', 'xml_opt_date', str(self.xml_opt_date.get()))
        # writing
        with open(path.realpath(config_file), 'wb') as configfile:
            config.write(configfile)

        logging.info("Settings saved into: {}".format(config_file))
        # end of method
        return

    # ------------------------------------------------------------------------

    def remove_accents(self, input_str, substitute=u""):
        """Clean string from special characters.

        source: http://stackoverflow.com/a/5843560
        """
        return unicode(substitute).join(char for char in input_str if char.isalnum())

    def clean_xml(self, invalid_xml, mode="soft", substitute=u"_"):
        """Clean string of XML invalid characters.

        source: http://stackoverflow.com/a/13322581/2556577
        """
        # assumptions:
        #   doc = *( start_tag / end_tag / text )
        #   start_tag = '<' name *attr [ '/' ] '>'
        #   end_tag = '<' '/' name '>'
        ws = r'[ \t\r\n]*'  # allow ws between any token
        name = '[a-zA-Z]+'  # note: expand if necessary but the stricter the better
        attr = '{name} {ws} = {ws} "[^"]*"'  # note: fragile against missing '"'; no "'"
        start_tag = '< {ws} {name} {ws} (?:{attr} {ws})* /? {ws} >'
        end_tag = '{ws}'.join(['<', '/', '{name}', '>'])
        tag = '{start_tag} | {end_tag}'

        assert '{{' not in tag
        while '{' in tag:   # unwrap definitions
            tag = tag.format(**vars())

        tag_regex = re.compile('(%s)' % tag, flags=re.VERBOSE)

        # escape &, <, > in the text
        iters = [iter(tag_regex.split(invalid_xml))] * 2
        pairs = izip_longest(*iters, fillvalue='')  # iterate 2 items at a time

        # get the clean version
        clean_version = ''.join(escape(text) + tag for text, tag in pairs)
        if mode == "strict":
            clean_version = re.sub(r"<.*?>", substitute, clean_version)
        else:
            pass
        return clean_version

    def clean_filename(self, filename, mode="soft", substitute=u"_"):
        """Removes invalid characters from filename."""
        if mode == "soft":
            return re.sub(r'[\\/*?:"<>|]', substitute, filename)
        elif mode == "strict":
            return re.sub("[^\w\-_\. ]", substitute, filename)
        else:
            pass

# ############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == '__main__':
    """Standalone execution and tests"""
    utils = IsogeoToGIS_Utils()

    # assert