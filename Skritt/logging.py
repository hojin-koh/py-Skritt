#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2024-2025, Hojin Koh
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import sys

import loguru._logger
from loguru import logger

from .res import Resource

type TypeLogger = loguru.Logger | logging.Logger

class ResourceLogger(Resource):
    """
    Configure the global logger for this process and expose the logger instance
    as public member.
    """
    def initialize(self) -> None:
        self.logger = logger
        # For subprocess logging
        logger.level('PROC', no=22, color="<white>")
        logger.remove(0)
        self.setStderr()

    def getFormat(self) -> str:
        return '<level>{time:YYYYMMDD HHmmss} [{level.name[0]}] {message}</level>'

    def setStderr(self, level: str = 'INFO') -> int:
        if hasattr(self, 'hStderr'):
            self.logger.remove(self.hStderr)
        handle = self.logger.add(sys.stderr, level=level, format=self.getFormat())
        self.hStderr: int = handle
        return handle

    def setFile(self, filename: str) -> int:
        """
        Setup a file as the logging sink, and return an integer handler to later
        be used to remove the sink through removeSink()
        """
        return self.logger.add(filename, level="DEBUG", format=self.getFormat())

    def removeSink(self, handler: int) -> None:
        self.logger.remove(handler)
