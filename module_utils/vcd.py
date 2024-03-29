# Copyright © 2018 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause

import os
from lxml import etree
from pyvcloud.vcd.client import Client
from pyvcloud.vcd.client import TaskStatus
from ansible.module_utils.basic import AnsibleModule
from pyvcloud.vcd.client import BasicLoginCredentials
# from module_utils.vcd_errors import VCDLoginError


class VCDVappCreationError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VCDLoginError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VDCNotFoundError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, " VDCNotFoundError [" + msg + "]")


class ItemFoundError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, " ItemFoundError [" + msg + "]")


class VCDDiskCreationError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VCDDiskDeletionError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VCDOrgCreationError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VCDOrgDeleteError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class APINotImplement(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VCDVdcDeleteError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VCDVdcCreateError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappVmCreateError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappVmDeleteError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappVmReloadError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappVmModifyCPUError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappVmModifyMemoryError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappVmUnDeployError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappVmPowerOnError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappVmPowerOffError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappNetworkCreateError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


class VappUpdateError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


def vcd_argument_spec():
    return dict(
        user=dict(type='str', required=False, default=os.environ.get('env_user')),
        password=dict(type='str', required=False, no_log=True, default=os.environ.get('env_password')),
        org=dict(type='str', required=False, default=os.environ.get('env_org')),
        host=dict(type='str', required=False, default=os.environ.get('env_host')),
        api_version=dict(type='str', default=os.environ.get('env_api_version', '30.0')),
        verify_ssl_certs=dict(type='bool', default=os.environ.get('env_verify_ssl_certs', False))
    )


class VcdAnsibleModule(AnsibleModule):
    def __init__(self, *args, **kwargs):
        argument_spec = vcd_argument_spec()
        argument_spec.update(kwargs.get('argument_spec', dict()))
        kwargs['argument_spec'] = argument_spec

        super(VcdAnsibleModule, self).__init__(*args, **kwargs)
        self.login()

    def login(self):
        try:
            user = self.params.get('user')
            password = self.params.get('password')
            org = self.params.get('org')
            host = self.params.get('host')
            api_version = self.params.get('api_version')
            verify_ssl_certs = self.params.get('verify_ssl_certs')
            self.client = Client(host,
                                 api_version=api_version,
                                 verify_ssl_certs=verify_ssl_certs)

            self.client.set_credentials(BasicLoginCredentials(user, org, password))

        except Exception as error:
            error = 'Login failed for user {} to org {}'
            raise VCDLoginError(error.format(user, org))

    def execute_task(self, task):
        task_monitor = self.client.get_task_monitor()
        task_state = task_monitor.wait_for_status(
            task=task,
            timeout=60,
            poll_frequency=2,
            fail_on_statuses=None,
            expected_target_statuses=[
                TaskStatus.SUCCESS, TaskStatus.ABORTED, TaskStatus.ERROR,
                TaskStatus.CANCELED
            ],
            callback=None)

        task_status = task_state.get('status')
        if task_status != TaskStatus.SUCCESS.value:
            raise Exception(etree.tostring(task_state, pretty_print=True))

        return 1
