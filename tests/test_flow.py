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

# Tests related to basic running flow

import typing

import pytest

from Skritt import Step

# Mock class to test `Step` functionality
class NormalStep(Step):
    def __init__(self, should_check: bool, *args: str):
        super().__init__(*args)
        self.should_check = should_check
        self.main_called = False

    def check(self: typing.Self) -> bool:
        return self.should_check

    def main(self: typing.Self) -> int:
        self.main_called = True
        return 42

# Test cases
def test_abstract_main():
    """Test that invoking an undefined 'main' raises an exception."""
    class IncompleteStep(Step):
        pass

    with pytest.raises(TypeError):
        IncompleteStep()  # Should raise because `main` is not implemented

def test_execute_return_main_return():
    """Test invoke() returns the result of main() when check() is True."""
    step = NormalStep(should_check=True)
    result = step.execute()
    assert result == 42
    assert step.main_called is True

def test_invoke_return_main_called():
    """Test invoke() returns the result of main() when check() is True."""
    step = NormalStep(should_check=True)
    result = step.invoke()
    assert result == 42
    assert step.main_called is True

def test_invoke_return_no_main_called():
    """Test invoke() returns 0 when check() is False and main() is not called."""
    step = NormalStep(should_check=False)
    result = step.invoke()
    assert result == 0
    assert step.main_called is False
