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

from __future__ import annotations # Shouldn't be needed after python 3.14
from collections.abc import Generator
from typing import Protocol, Self

from abc import ABC, abstractmethod
from argparse import ArgumentParser, Namespace, _ArgumentGroup

from collections import defaultdict

class TypeHookFunc[C: StepBase](Protocol):
    """
    What the hook functions should look like: func(step)
    """
    def __call__(self, step: C) -> None:
        pass

class StepBase(ABC):
    """
    Base class defining the lifecycle of a Step.

    A Step is a bundle containing a script to run, a set of argument definitions,
    and optionally a check function determining whether the script need to run or
    not.

    This base class include things that don't interact with outside world (logging etc.).
    """

    def __init__(self, *args: str) -> None:
        self.mLifecycle: defaultdict[str, list[tuple[str, TypeHookFunc[Self]]]] = defaultdict(list)
        self.aCmdline: list[str] = list(args)
        self.parser = ArgumentParser(allow_abbrev=False, exit_on_error=False)
        self.mParserGroups: dict[str, _ArgumentGroup] = {}

    # The main lifecycle

    def needed(self) -> bool:
        return True

    @abstractmethod
    def main(self) -> int:
        return 0

    # Invoke: include need-to-run check
    def invoke(self) -> int:
        if not hasattr(self, 'args'):
            self.parseArgs()
        if self.needed():
            rtn = self.execute()
        else:
            rtn = 0
        return rtn

    # Execute: main life cycle
    def execute(self) -> int:
        rtn = self.main()
        return rtn

    def addHook(self, nameLifecycle: str, nameFunc: str, func: TypeHookFunc[Self], atBegin: bool = False) -> None:
        """
        Add a function to a hook list by lifecycle name and a function name.

        Optionally, the hook function can be prepended at the beginning of the list instead of at the end.
        """
        if atBegin:
            self.mLifecycle[nameLifecycle].insert(0, (nameFunc, func))
        else:
            self.mLifecycle[nameLifecycle].append((nameFunc, func))

    def listLifecycles(self) -> Generator[str]:
        """
        Yield the names of all defined lifecycles in the current step.
        """
        yield from self.mLifecycle.keys()
        
    def listHooks(self, nameLifecycle: str) -> Generator[tuple[str, TypeHookFunc[Self]]]:
        """
        Yield all hooks (name and callable) associated with the given lifecycle.
        """
        if nameLifecycle in self.mLifecycle:
            yield from self.mLifecycle[nameLifecycle]

    def invokeHookFunc(self, name: str, func: TypeHookFunc[Self]) -> None:
        func(self)

    def invokeHook(self, nameLifecycle: str) -> None:
        """
        Call all functions in a certain lifecycle in order, passing `self`.
        """
        if nameLifecycle not in self.mLifecycle:
            return
        
        for name, func in self.listHooks(nameLifecycle):
            self.invokeHookFunc(name, func)

    # argparse-related things

    def parseArgs(self) -> None:
        """
        Actually parse the commandline arguments stored in this object, and store the
        results as self.args
        """
        self.args: Namespace = self.parser.parse_intermixed_args(self.aCmdline)

    def getParser(self, nameGroup: str = "Skritt") -> _ArgumentGroup:
        """
        Get the argparse group to add argument definitions
        """
        if nameGroup not in self.mParserGroups:
            self.mParserGroups[nameGroup] = self.parser.add_argument_group(nameGroup)
        return self.mParserGroups[nameGroup]
