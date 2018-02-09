#!/usr/bin/python
# -*- coding: utf-8 -*-

import re


class BPCSReservationDetails(object):
    PORT_FAMILY = ['Port', 'Virtual Port']
    CHASSIS_FAMILY = ['Traffic Generator Chassis', 'Virtual Traffic Generator Chassis', 'CS_TrafficGeneratorChassis']
    PORT_ATTRIBUTE = 'Logical Name'
    USERNAME_ATTRIBUTE = 'User'
    PASSWORD_ATTRIBUTE = 'Password'

    def __init__(self, context, logger, api):
        self._context = context
        self._logger = logger
        self._api = api

        self.__chassis_resource = None
        self.__chassis_resource_details = None

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, value):
        self._context = value

    @property
    def api(self):
        return self._api

    @api.setter
    def api(self, value):
        self.__chassis_resource = None
        self.__chassis_resource_details = None
        self._api = value

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, value):
        self._logger = value

    @property
    def _chassis_resource(self):
        if not self.__chassis_resource:
            for resource in self._get_reservation_details().ReservationDescription.Resources:
                if resource.ResourceFamilyName in self.CHASSIS_FAMILY:
                    self.__chassis_resource = resource
                    break
        if self.__chassis_resource:
            return self.__chassis_resource
        raise Exception(self.__class__.__name__, 'Cannot find chassis resource in the reservation')

    @property
    def _chassis_resource_details(self):
        if not self.__chassis_resource_details:
            self.__chassis_resource_details = self.api.GetResourceDetails(self._chassis_resource_name)
        if self.__chassis_resource_details:
            return self.__chassis_resource_details
        raise Exception(self.__class__.__name__,
                        'Cannot find resource details for resource {}'.format(self._chassis_resource_name))

    @property
    def _chassis_resource_name(self):
        return self._chassis_resource.Name

    @property
    def _chassis_resource_model(self):
        return self._chassis_resource.ResourceModelName

    @property
    def _chassis_resource_family(self):
        return self._chassis_resource.ResourceFamilyName

    def get_chassis_address(self):
        return self._chassis_resource.FullAddress

    def _get_reservation_details(self):
        self.logger.debug('API instance: {}'.format(self.api))
        reservation_id = self.context.reservation.reservation_id
        return self.api.GetReservationDetails(reservationId=reservation_id)

    def get_chassis_ports(self):
        self.logger.debug('Api: {}'.format(self.api))
        reserved_ports = {}
        port_pattern = r'{}/M(?P<module>\d+)/P(?P<port>\d+)'.format(self.get_chassis_address())
        for resource in self._get_reservation_details().ReservationDescription.Resources:
            if resource.ResourceFamilyName in self.PORT_FAMILY:
                result = re.search(port_pattern, resource.FullAddress)
                if result:
                    logical_name = self.api.GetAttributeValue(resourceFullPath=resource.Name,
                                                              attributeName=self.PORT_ATTRIBUTE).Value
                    if logical_name:
                        reserved_ports[logical_name.lower()] = (result.group('module'), result.group('port'))
        self.logger.debug('Chassis ports {}'.format(reserved_ports))
        return reserved_ports

    def _get_attribute(self, attribute_name):
        new_gen_attr_name = '{resource_model}.{attribute_name}'.format(resource_model=self._chassis_resource_model,
                                                                       attribute_name=attribute_name)
        for attribute in self._chassis_resource_details.ResourceAttributes:
            if attribute.Name == attribute_name or attribute.Name == new_gen_attr_name:
                return attribute.Value

    def get_chassis_user(self):
        return self._get_attribute(self.USERNAME_ATTRIBUTE)

    def get_chassis_password(self):

        encrypted_password = self._get_attribute(self.PASSWORD_ATTRIBUTE)
        return self.api.DecryptPassword(encrypted_password).Value
