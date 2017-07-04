import os
from xml.etree import ElementTree

from cloudshell.tg.breaking_point.runners.exceptions import BPRunnerException


class TestFileHelper(object):
    def __init__(self, test_name, test_content, context):
        self._context = context
        self._test_name = self.gen_name(test_name)
        self._test_content = test_content

    def gen_name(self, test_name):
        """
        Nenerate new name
        :param test_name: 
        :return: 
        """
        return "{0}_{1}".format(test_name, self._context.reservation.reservation_id)

    def modify_test_content(self):
        """
        Modify content with new name
        :return: 
        """
        root_node = ElementTree.fromstring(self._test_content)
        test_model = root_node.find('testmodel')
        test_model.set('network', self._test_name)
        network = root_node.find('network')
        network.set('name', self._test_name)
        self._test_content = ElementTree.tostring(root_node)

    def save_test_content_to_the_file(self):
        """
        Save test configuration to the file
        :return: 
        """
        test_files_location = self._context.resource.attributes.get('Test Files Location')
        if not test_files_location:
            raise BPRunnerException(self.__class__.__name__, "Test Files Location attribute is not defined")
        if not os.path.exists(test_files_location) or os.access(test_files_location, os.W_OK) is not True:
            raise BPRunnerException(self.__class__.__name__,
                                    'The location of the test files "{}" does not exist or is not writable'.format(
                                        test_files_location))
        reservation_files = os.path.join(test_files_location, self._context.reservation.reservation_id)
        if not os.path.exists(reservation_files):
            os.makedirs(reservation_files)
        test_file_path = os.path.join(reservation_files, self._test_name + '.bpt')
        with open(test_file_path, 'w') as f:
            f.write(self._test_content)
        return test_file_path
