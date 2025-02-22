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

import abc
import typing

class Step(abc.ABC):
    """
    Base class defining a Step.

    A Step is a bundle containing a script to run, a set of argument definitions,
    and optionally a check function determining whether the script need to run or
    not.
    """

    def __init__(self: typing.Self, *args: str):
        pass

    def check(self: typing.Self) -> bool:
        return True

    @abc.abstractmethod
    def main(self: typing.Self) -> int:
        return 0

    # Invoke: include check
    def invoke(self: typing.Self) -> int:
        if self.check():
            rtn = self.execute()
        else:
            rtn = 0
        return rtn

    # Execute: main life cycle
    def execute(self: typing.Self) -> int:
        rtn = self.main()
        return rtn

