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

from typing import Self

import pytest

from Skritt.base import StepBase

# Mock class to test `StepBase` functionality
class NormalStep(StepBase):
    def __init__(self, should_check: bool, *args: str) -> None:
        super().__init__(*args)
        self.should_check = should_check
        self.main_called = False

    def check(self: Self) -> bool:
        return self.should_check

    def main(self: Self) -> int:
        self.main_called = True
        return 42

# Test cases
def test_abstract_main() -> None:
    """Test that invoking an undefined 'main' raises an exception."""
    class IncompleteStep(StepBase):
        pass

    # Should raise because `main` is not implemented
    with pytest.raises(TypeError):
        IncompleteStep() # type: ignore[abstract]

def test_execute_return_main_return() -> None:
    """Test invoke() returns the result of main() when check() returns True."""
    step = NormalStep(should_check=True)
    result = step.execute()
    assert result == 42
    assert step.main_called is True

def test_invoke_return_main_called() -> None:
    """Test invoke() returns the result of main() when check() returns True."""
    step = NormalStep(should_check=True)
    result = step.invoke()
    assert result == 42
    assert step.main_called is True

def test_invoke_return_no_main_called() -> None:
    """Test invoke() returns 0 when check() returns False and main() is not called."""
    step = NormalStep(should_check=False)
    result = step.invoke()
    assert result == 0
    assert step.main_called is False
