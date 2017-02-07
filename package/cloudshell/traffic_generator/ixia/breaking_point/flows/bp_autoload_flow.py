from cloudshell.traffic_generator.ixia.breaking_point.autoload.info.bp_chassis_info import BPChassisInfo
from cloudshell.traffic_generator.ixia.breaking_point.autoload.info.bp_modules_info import BPModulesInfo
from cloudshell.traffic_generator.ixia.breaking_point.autoload.info.bp_ports_info import BPPortsInfo
from cloudshell.traffic_generator.ixia.breaking_point.rest_actions.autoload_actions import AutoloadActions
from cloudshell.traffic_generator.ixia.breaking_point.rest_api.rest_session_manager import RestSessionManager


class BPAutoloadFlow(object):
    def __init__(self, session_manager, logger):
        """
        :param session_manager:
        :type session_manager: RestSessionManager
        :param logger:
        :return:
        """
        self._session_manager = session_manager
        self._logger = logger
        self._elements = {}

    def autoload_details(self):
        with self._session_manager.new_session() as session:
            autoload_actions = AutoloadActions(session, self._logger)

            chassis_info = BPChassisInfo(autoload_actions, self._logger)
            self._elements.update(chassis_info.collect())

            modules_info = BPModulesInfo(autoload_actions, self._logger)
            self._elements.update(modules_info.collect())

            ports_info = BPPortsInfo(autoload_actions, self._logger)
            self._elements.update(ports_info.collect())