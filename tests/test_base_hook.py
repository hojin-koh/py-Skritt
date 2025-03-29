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

# Tests related to the hook system in StepBase

import pytest

from Skritt.base import StepBase, TypeHookFunc

class MockStep(StepBase):
    """Mock subclass for testing the hook system in StepBase."""
    def __init__(self, *args: str) -> None:
        super().__init__(*args)
        self.stateTest: list[str] = []
    def main(self) -> int:
        return 42

@pytest.fixture
def step() -> MockStep:
    """Fixture to provide a fresh StepBase instance for each test."""
    return MockStep()

def getMockHook(name: str) -> TypeHookFunc[MockStep]:
    def funcHook(step: MockStep) -> None:
        step.stateTest.append(name)
    return funcHook

def test_add_hook_to_lifecycle(step: MockStep) -> None:
    """
    Test that hooks can be added to a lifecycle and later inspected.
    """
    nameHook = "test_hook"
    nameLifecycle = "preparse"

    step.addHook(nameLifecycle, nameHook, getMockHook(nameHook))

    hooks = list(step.listHooks(nameLifecycle))
    assert len(hooks) == 1
    assert hooks[0][0] == nameHook  # Check hook name
    assert callable(hooks[0][1])  # Check hook function

def test_empty_lifecycle(step: MockStep) -> None:
    """
    Test that empty lifecycles are indeed empty.
    """
    hooks = list(step.listHooks("nonexistent"))
    assert hooks == []

def test_empty_lifecycle_invoke(step: MockStep) -> None:
    """
    Test that invoking an empty lifecycle has no effect.
    """
    step.invokeLifecycle("nonexistent")
    assert step.stateTest == []

def test_list_lifecycles(step: MockStep) -> None:
    """
    Test the ability to list all registered lifecycles.
    """
    step.addHook("preparse", "hook1", getMockHook("hook1"))
    step.addHook("prerun", "hook2", getMockHook("hook2"))

    lifecycles = list(step.listLifecycles())
    assert len(lifecycles) == 2
    assert "preparse" in lifecycles
    assert "prerun" in lifecycles

def test_empty_lifecycle_not_added(step: MockStep) -> None:
    """
    Test that invoking an empty lifecycle doesn't get it added by accident.
    """
    step.invokeLifecycle("nonexistent")

    lifecycles = list(step.listLifecycles())
    assert "nonexistent" not in lifecycles

def test_invoke_hook_executes_functions(step: MockStep) -> None:
    """
    Test that invoking hooks calls the associated functions in order.
    """
    nameHook1 = "hook1"
    nameHook2 = "hook2"
    nameLifecycle = "prerun"

    step.addHook(nameLifecycle, nameHook1, getMockHook(nameHook1))
    step.addHook(nameLifecycle, nameHook2, getMockHook(nameHook2))

    step.invokeLifecycle(nameLifecycle)
    assert step.stateTest == [nameHook1, nameHook2]

def test_hooks_at_beginning(step: MockStep) -> None:
    """
    Test adding hooks with the 'atBegin' option ensures correct order.
    """
    nameHook1 = "first_hook"
    nameHook2 = "second_hook"
    nameLifecycle = "preparse"

    step.addHook(nameLifecycle, nameHook2, getMockHook(nameHook2))
    step.addHook(nameLifecycle, nameHook1, getMockHook(nameHook1), atBegin=True)

    step.invokeLifecycle(nameLifecycle)
    assert step.stateTest == [nameHook1, nameHook2]
