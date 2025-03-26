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

import sys

from .res import Resource
from loguru import logger

class ResourceLogger(Resource):
    """
    Configure the global logger for this process and expose the logger instance
    as public member.
    """
    def initialize(self) -> None:
        logger.remove(0)
        logger.add(sys.stderr, level="INFO", format="<level>{time:YYYYMMDD HHmmss} [{level.name[0]}]</level> {file}:{line} <level>{message}</level>")
        self.logger = logger

    def setFile(self, filename: str) -> int:
        """
        Setup a file as the logging sink, and return an integer handler to later
        be used to remove the sink through removeSink()
        """
        return self.logger.add(filename, level="DEBUG", enqueue=True, format="{time:YYYYMMDD HHmmss} [{level.name[0]}] {file}:{line} {message}")

    def removeSink(self, handler: int) -> None:
        self.logger.remove(handler)
