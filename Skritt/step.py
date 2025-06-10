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

from collections.abc import Sequence
from typing import Self
from Skritt.base import TypeHookFunc

import asyncio
from datetime import datetime, timedelta

from .base import StepBase
from .logging import ResourceLogger
from .subprocess import shellrun, ThreadForSubprocess

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
        parser.add_argument("--debug", action='store_true', help="Show debug message on screen")
        parser.add_argument("--notitle", action='store_true', help="Disable showing fancy begin/end banners")
        parser.add_argument("--force", action='store_true', help="Run the step even if not necessary")
        parser.add_argument("--check", action='store_true', help="Check if need to run or not and return 0 if need to run")

    # Additional logging
    def invokeHookFunc(self, name: str, func: TypeHookFunc[Self]) -> None:
        self.logger.debug(F"Hook {name}: {func.__qualname__}()")
        super().invokeHookFunc(name, func)

    def invokeLifecycle(self, nameLifecycle: str) -> None:
        """
        Call all functions in a certain lifecycle in order, passing `self`.
        """
        self.logger.debug(F"Lifecycle {self.__class__.__qualname__}::{nameLifecycle}")
        if nameLifecycle not in self.mLifecycle:
            return

        for name, func in self.listHooks(nameLifecycle):
            self.invokeHookFunc(name, func)

    # Fancy logging
    def showHeader(self) -> None:
        titleScript = F"{self.__class__.__qualname__} {' '.join(self.aCmdline)}"
        if len(titleScript) > 160:
            titleScript = titleScript[:160] + " ..."
        self.logger.success(titleScript)
        self.timeBegin: datetime = datetime.now()

    def showFooter(self, rtn: int) -> None:
        elapsed: timedelta = datetime.now() - self.timeBegin
        if rtn == 0:
            self.logger.success(F"Retrun 0 in {elapsed}\n")
        else:
            self.logger.error(F"Retrun {rtn} in {elapsed}\n")

    # Standard lifecycle hooks, with logging added
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

        if not self.args.notitle:
            self.showHeader()
        self.invokeLifecycle("post-parse")

    def invoke(self) -> int:
        rtn = -1
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
            # Guard against the "--help" scenario to avoid generating unnecessary exceptions
            if hasattr(self, 'args'):
                self.cleanup()
                self.invokeLifecycle("cleanup")
                if not self.args.notitle:
                    self.showFooter(rtn)
            if hasattr(self, 'hLogfile'):
                self.resLogging.removeSink(self.hLogfile)

    def execute(self) -> int:
        try:
            self.invokeLifecycle("pre-run")
            return self.main()
        finally:
            self.invokeLifecycle("post-run")

    def shellout(self, *args: Sequence[str]) -> int:
        return asyncio.run(shellrun(self.logger, args))

    def shellbg(self, *args: Sequence[str]) -> ThreadForSubprocess:
        t = ThreadForSubprocess(target=self.shellout, args=args)
        t.start()
        return t
