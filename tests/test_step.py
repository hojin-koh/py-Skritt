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

# Tests related to Step running flow, mainly the additional lifecycle

from typing import Self
from Skritt.base import TypeHookFunc

from Skritt import Step

class NormalStep(Step):
    """Mock class to test `Step` hook calling functionality"""
    def __init__(self, *args: str, should_check: bool) -> None:
        super().__init__(*args)
        self.should_check = should_check
        self.main_called = False
        self.cleanup_called = False
        self.lifecycle_calls: list[str] = []

    def needed(self) -> bool:
        return self.should_check

    def cleanup(self) -> None:
        self.cleanup_called = True

    def main(self) -> int:
        self.main_called = True
        return 42

    def invokeHookFunc(self, name: str, func: TypeHookFunc[Self]) -> None:
        """
        Overriden invokeHookFunc adding instrumentation for testing
        """
        self.lifecycle_calls.append(f"{name}")
        super().invokeHookFunc(name, func)


# Test cases
def test_lifecycle_hooks_execute() -> None:
    """Test that lifecycle hooks are called in the correct order during execute()"""
    step = NormalStep(should_check=True)

    step.addHook('pre-run', 'pre-run-test', lambda s: None)
    step.addHook('post-run', 'post-run-test', lambda s: None)

    step.parseArgs()
    step.execute()

    assert "pre-run-test" in step.lifecycle_calls
    assert "post-run-test" in step.lifecycle_calls
    assert step.lifecycle_calls.index("pre-run-test") < step.lifecycle_calls.index("post-run-test")


def test_lifecycle_hooks_parse_args() -> None:
    """Test that pre-parse and post-parse hooks are called in the correct order"""
    step = NormalStep(should_check=True)

    step.addHook('pre-parse', 'pre-parse-test', lambda s: None)
    step.addHook('post-parse', 'post-parse-test', lambda s: None)

    step.parseArgs()

    assert "pre-parse-test" in step.lifecycle_calls
    assert "post-parse-test" in step.lifecycle_calls
    assert step.lifecycle_calls.index("pre-parse-test") < step.lifecycle_calls.index("post-parse-test")


def test_lifecycle_hooks_invoke() -> None:
    """Test that cleanup hook is called during invoke()"""
    step = NormalStep(should_check=True)

    step.addHook('pre-parse', 'pre-parse-test', lambda s: None)
    step.addHook('post-parse', 'post-parse-test', lambda s: None)
    step.addHook('pre-run', 'pre-run-test', lambda s: None)
    step.addHook('post-run', 'post-run-test', lambda s: None)
    step.addHook('cleanup', 'cleanup-test', lambda s: None)

    step.invoke()

    assert "cleanup-test" in step.lifecycle_calls
    assert "pre-parse-test" in step.lifecycle_calls
    assert "post-parse-test" in step.lifecycle_calls
    assert "pre-run-test" in step.lifecycle_calls
    assert "post-run-test" in step.lifecycle_calls
    assert step.lifecycle_calls.index("pre-parse-test") < step.lifecycle_calls.index("post-parse-test")
    assert step.lifecycle_calls.index("post-parse-test") < step.lifecycle_calls.index("pre-run-test")
    assert step.lifecycle_calls.index("pre-run-test") < step.lifecycle_calls.index("post-run-test")
    assert step.lifecycle_calls.index("post-run-test") < step.lifecycle_calls.index("cleanup-test")
    assert step.cleanup_called is True


def test_force_flag() -> None:
    """Test that --force flag makes the step run even when needed() returns False"""
    step = NormalStep("--force", should_check=False)
    result = step.invoke()

    assert result == 42
    assert step.main_called is True
    assert step.cleanup_called is True


def test_check_flag_needed() -> None:
    """Test that --check flag returns 0 when needed() returns True"""
    step = NormalStep("--check", should_check=True)
    result = step.invoke()

    assert result == 0
    assert step.main_called is False
    assert step.cleanup_called is True


def test_check_flag_not_needed() -> None:
    """Test that --check flag returns 1 when needed() returns False"""
    step = NormalStep("--check", should_check=False)
    result = step.invoke()

    assert result == 1
    assert step.main_called is False
    assert step.cleanup_called is True
