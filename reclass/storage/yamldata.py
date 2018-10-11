#
# -*- coding: utf-8 -*-
#
# This file is part of reclass (http://github.com/madduck/reclass)
#
# Copyright © 2007–14 martin f. krafft <madduck@madduck.net>
# Released under the terms of the Artistic Licence 2.0
#
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from reclass import datatypes
import yaml
import os
from reclass.errors import NotFoundError

_SafeLoader = yaml.CSafeLoader if yaml.__with_libyaml__ else yaml.SafeLoader

class YamlData(object):

    @classmethod
    def from_file(cls, path):
        ''' Initialise yaml data from a local file '''
        abs_path = os.path.abspath(path)
        if not os.path.isfile(abs_path):
            raise NotFoundError('No such file: %s' % abs_path)
        if not os.access(abs_path, os.R_OK):
            raise NotFoundError('Cannot open: %s' % abs_path)
        y = cls('yaml_fs://{0}'.format(abs_path))
        with open(abs_path) as fp:
            data = yaml.load(fp, Loader=_SafeLoader)
            if data is not None:
                y._data = data
        return y

    @classmethod
    def from_string(cls, string, uri):
        ''' Initialise yaml data from a string '''
        y = cls(uri)
        data = yaml.load(string, Loader=_SafeLoader)
        if data is not None:
            y._data = data
        return y

    def __init__(self, uri):
        self._uri = uri
        self._data = dict()

    uri = property(lambda self: self._uri)

    def get_data(self):
        return self._data

    def set_absolute_names(self, name, names):
        structure = name.split('.')
        parent = '.'.join(structure[0:-1])
        new_names = []
        for n in names:
            if n[0] == '.' and len(n) > 1 and n[1] == '.':
                grandparent = '.'.join(structure[0:-2])
                n = self.get_grandparent_directory(n, parent, grandparent)
            else:
                n = self.get_parent_directory(n, parent)
            new_names.append(n)
        return new_names

    def get_parent_directory(self, name, parent):
        if parent == '':
            name = name[1:]
        elif len(name) == 1:
            name = parent
        else:
            name = parent + name
        return name

    def get_grandparent_directory(self, name, parent, grandparent):
        if len(name) == 2:
            name = grandparent
        elif parent == '' or grandparent == '':
            name = name[2:]
        else:
            name = grandparent + name[1:]
        return name

    def get_entity(self, name, settings):
        #if name is None:
        #    name = self._uri

        classes = self._data.get('classes')
        if classes is None:
            classes = []
        classes = self.set_absolute_names(name, classes)
        classes = datatypes.Classes(classes)

        applications = self._data.get('applications')
        if applications is None:
            applications = []
        applications = datatypes.Applications(applications)

        parameters = self._data.get('parameters')
        if parameters is None:
            parameters = {}
        parameters = datatypes.Parameters(parameters, settings, self._uri)

        exports = self._data.get('exports')
        if exports is None:
            exports = {}
        exports = datatypes.Exports(exports, settings, self._uri)

        env = self._data.get('environment', None)

        return datatypes.Entity(settings, classes=classes, applications=applications, parameters=parameters,
                                exports=exports, name=name, environment=env, uri=self.uri)

    def __str__(self):
        return '<{0} {1}, {2}>'.format(self.__class__.__name__, self._uri,
                                       self._data)

    def __repr__(self):
        return '<{0} {1}, {2}>'.format(self.__class__.__name__, self._uri,
                                       self._data.keys())
