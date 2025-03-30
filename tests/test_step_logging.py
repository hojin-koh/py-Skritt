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

# Tests related to Step logging functionality

import re
import tempfile

import pytest
from Skritt import Step

class NormalStep(Step):
    """Test implementation of Step"""
    def main(self) -> int:
        self.logger.info("Running main")
        self.logger.debug("Debug message from main")
        return 0

def test_debug_flag(capfd: pytest.CaptureFixture[str]) -> None:
    """Test that --debug enables debug messages to stderr"""
    # Without debug flag
    step = NormalStep()
    step.invoke()
    captured = capfd.readouterr()
    assert "Debug message" not in captured.err

    # With debug flag
    step = NormalStep("--debug")
    step.invoke()
    captured = capfd.readouterr()
    assert "Debug message" in captured.err

def test_step_logfile_handling() -> None:
    with tempfile.NamedTemporaryFile() as tmp:
        step = NormalStep("--logfile", tmp.name)
        step.invoke()

        step.logger.info("After logfile detached")

        with open(tmp.name) as f:
            content = f.read()
            assert re.search(r"\d{8} \d{6} \[D\]", content)
            assert "Running main" in content
            assert "Debug message from main" in content
            assert "After logfile detached" not in content

def test_nested_step_logfile_handling() -> None:
    with tempfile.NamedTemporaryFile() as tmp1, tempfile.NamedTemporaryFile() as tmp2:
        # Create a nested step with a different logfile
        class NestedStep(NormalStep):
            def main(self) -> int:
                self.logger.debug("Outer step running")
                # Create and run a child step
                child = NormalStep("--logfile", tmp2.name)
                child.invoke()
                return 0

        nested = NestedStep('--logfile', tmp1.name)
        nested.invoke()

        # Check the parent's logfile
        with open(tmp1.name) as f:
            content = f.read()
            assert re.search(r"\d{8} \d{6} \[D\]", content)
            assert "Outer step running" in content
            assert "Running main" in content
            assert "Debug message from main" in content

        # Check the child's logfile
        with open(tmp2.name) as f:
            content = f.read()
            assert re.search(r"\d{8} \d{6} \[D\]", content)
            assert "Outer step running" not in content
            assert "Running main" in content
            assert "Debug message from main" in content
