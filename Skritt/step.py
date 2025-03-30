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

from .base import StepBase
from .logging import ResourceLogger

class Step(StepBase):
    """
    A Step. The basic building block of Skritt library.
    """

    def __init__(self, *args: str) -> None:
        super().__init__(*args)
        self.resLogging = ResourceLogger()
        self.logger = self.resLogging.logger

        parser = self.getParser()
        parser.add_argument("--logfile", help="File to write log in")
        parser.add_argument("--force", action='store_true', help="Run the step even if not necessary")
        parser.add_argument("--check", action='store_true', help="Check if need to run or not and return 0 if need to run")
        parser.add_argument("--debug", action='store_true', help="Show debug message on screen")

    # Standard lifecycle hooks
    def parseArgs(self) -> None:
        """
        Same as StepBase's parseArgs, but add preparse and postparse lifecycle
        """
        self.invokeLifecycle("pre-parse")
        super().parseArgs()

        # Configure logging based on arguments
        if self.args.debug:
            self.resLogging.setStderr('DEBUG')

        if self.args.logfile:
            self.hLogfile: int = self.resLogging.setFile(self.args.logfile)

        self.invokeLifecycle("post-parse")

    def invoke(self) -> int:
        try:
            if not hasattr(self, 'args'):
                self.parseArgs()

            # If --check is specified, just report if needed and exit
            if self.args.check:
                isNeeded = self.needed()
                return 0 if isNeeded else 1

            # If --force is specified, ignore the results of needed()
            if self.args.force or self.needed():
                rtn = self.execute()
            else:
                rtn = 0
            return rtn
        finally:
            self.cleanup()
            self.invokeLifecycle("cleanup")
            if hasattr(self, 'hLogfile'):
                self.resLogging.removeSink(self.hLogfile)

    def execute(self) -> int:
        try:
            self.invokeLifecycle("pre-run")
            return self.main()
        finally:
            self.invokeLifecycle("post-run")
