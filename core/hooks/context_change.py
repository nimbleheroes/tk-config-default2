# Copyright (c) 2018 Shotgun Software Inc.
#
# CONFIDENTIAL AND PROPRIETARY
#
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
This hook gets executed before and after the context changes in Toolkit.
"""

import os
from tank import get_hook_baseclass


class ContextChange(get_hook_baseclass()):
    """
    - If an engine **starts up**, the ``current_context`` passed to the hook
      methods will be ``None`` and the ``next_context`` parameter will be set
      to the context that the engine is starting in.

    - If an engine is being **reloaded**, in the context of an engine restart
      for example, the ``current_context`` and ``next_context`` will usually be
      the same.

    - If a **context switch** is requested, for example when a user switches
      from project to shot mode in Nuke Studio, ``current_context`` and ``next_context``
      will contain two different context.

    .. note::

       These hooks are called whenever the context is being set in Toolkit. It is
       possible that the new context will be the same as the old context. If
       you want to trigger some behavior only when the new one is different
       from the old one, you'll need to compare the two arguments using the
       ``!=`` operator.
    """

    def pre_context_change(self, current_context, next_context):
        """
        Executed before the context has changed.

        The default implementation does nothing.

        :param current_context: The context of the engine.
        :type current_context: :class:`~sgtk.Context`
        :param next_context: The context the engine is switching to.
        :type next_context: :class:`~sgtk.Context`
        """
        pass

    def post_context_change(self, previous_context, current_context):
        """
        Executed after the context has changed.

        The default implementation does nothing.

        :param previous_context: The previous context of the engine.
        :type previous_context: :class:`~sgtk.Context`
        :param current_context: The current context of the engine.
        :type current_context: :class:`~sgtk.Context`
        """
        if current_context != previous_context:

            try:
                os.environ.pop('SG_SHELL')
            except KeyError:
                pass

            if current_context is not None:

                shell_ctx = None

                if current_context.project:
                    project = self.parent.shotgun.find_one("Project",
                                                           [["id", "is", current_context.project['id']]],
                                                           ["code"])
                    shell_ctx = project['code']

                if current_context.entity:
                    if current_context.entity["type"] == "Shot":
                        entity = self.parent.shotgun.find_one("Shot",
                                                              [["id", "is", current_context.entity['id']]],
                                                              ["code"])

                    if current_context.entity["type"] == "Asset":
                        entity = self.parent.shotgun.find_one("Asset",
                                                              [["id", "is", current_context.entity['id']]],
                                                              ["code"])

                    if current_context.entity["type"] == "Sequence":
                        entity = self.parent.shotgun.find_one("Sequence",
                                                              [["id", "is", current_context.entity['id']]],
                                                              ["code"])

                    shell_ctx = "{}/{}".format(shell_ctx, entity)

                if current_context.entity and current_context.step:
                    step = self.parent.shotgun.find_one("Sequence",
                                                        [["id", "is", current_context.step['id']]],
                                                        ["code"])

                    shell_ctx = "{}/{}".format(shell_ctx, step)

                os.environ['SG_SHELL'] = shell_ctx
                self.logger.debug("Setting shell context to: {}".format(shell_ctx))
