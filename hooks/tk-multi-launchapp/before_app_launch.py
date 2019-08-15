# Copyright (c) 2013 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Before App Launch Hook

This hook is executed prior to application launch and is useful if you need
to set environment variables or run scripts as part of the app initialization.
"""

import os
import sgtk


class BeforeAppLaunch(sgtk.Hook):
    """
    Hook to set up the system prior to app launch.
    """

    def execute(self, app_path, app_args, version, engine_name, **kwargs):
        """
        The execute functon of the hook will be called prior to starting the required application

        :param app_path: (str) The path of the application executable
        :param app_args: (str) Any arguments the application may require
        :param version: (str) version of the application being run if set in the
            "versions" settings of the Launcher instance, otherwise None
        :param engine_name (str) The name of the engine associated with the
            software about to be launched.

        """

        # accessing the current context (current shot, etc)
        # can be done via the parent object
        #
        # > multi_launchapp = self.parent
        # > current_entity = multi_launchapp.context.entity

        # you can set environment variables like this:
        # os.environ["MY_SETTING"] = "foo bar"

        self.logger.debug('[niho] engine name: {0}'.format(engine_name))

        # import the niho framework
        niho_fw = self.load_framework("tk-framework-niho_v0.0.x")
        niho_utils = niho_fw.import_module("utils")

        # gets the 'pipeline' path from shotgun LocalStorage entity
        pipe_path_dict = self.parent.shotgun.find_one("LocalStorage", [['code', 'is', 'pipeline']], ["code", "linux_path", "windows_path", "mac_path"])
        pipe_path = sgtk.util.ShotgunPath.from_shotgun_dict(pipe_path_dict)

        # create a dict to store some env variables
        env_vars = {}

        # set the PIPE_PATH env variable
        env_vars['PIPE_PATH'] = os.path.join(pipe_path.current_os)

        # set env variables for nuke
        if engine_name in ['tk-nuke', 'tk-nuke-render']:
            global_nuke_path = os.path.join(pipe_path.current_os, 'nuke')
            global_plugins_path = os.path.join(global_nuke_path, 'plugins')
            project_plugins_path = os.path.join(niho_utils.resolve_template(self.sgtk.templates["nuke_tools_path"], self.parent.context), 'plugins')
            env_vars['NUKE_PATH'] = "{0}:{1}:{2}".format(global_nuke_path, global_plugins_path, project_plugins_path)

        # set env variables for hiero/nukestudio
        if engine_name in ['tk-hiero', 'tk-nukestudio']:
            env_vars['HIERO_PLUGIN_PATH'] = os.path.join(pipe_path.current_os, 'hiero')

        # append env_vars to existing environment
        for k, v in env_vars.iteritems():
            self.logger.debug('[niho] appending env {0}={1}'.format(k, v))
            sgtk.util.append_path_to_env_var(k, v)
