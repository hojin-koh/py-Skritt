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

# Tests related to argparse functionality in StepBase

from argparse import Namespace

from Skritt.base import StepBase

class MockStep(StepBase):
    """Mock subclass for testing the argparse wrapper in StepBase."""
    def main(self) -> int:
        return 42

def test_parse_args() -> None:
    """
    Test the parseArgs method to ensure command-line arguments are correctly parsed.
    """
    step = MockStep("--option1", "value1", "--option2", "value2")
    parser = step.getParser()
    parser.add_argument("--option1")
    parser.add_argument("--option2")

    step.parseArgs()

    assert step.args.option1 == "value1"
    assert step.args.option2 == "value2"

def test_get_parser_default_group() -> None:
    """
    Test getParser() is equivelent to getParser('Skritt')
    """
    step = MockStep()
    parser = step.getParser()
    parser2 = step.getParser('Skritt')

    assert parser is parser2

def test_get_parser_creates_group() -> None:
    """
    Test getParser to ensure a new argument group is created when requested.
    """
    step = MockStep()
    parser = step.getParser()
    parser2 = step.getParser('NewGroup')

    assert parser is not parser2

def test_get_parser_reuses_existing_group() -> None:
    """
    Test getParser to ensure an existing argument group is reused.
    """
    step = MockStep()
    parser1 = step.getParser("TestGroup")
    parser2 = step.getParser("TestGroup")
    assert parser1 is parser2

def test_no_arguments_handled_correctly() -> None:
    """
    Ensure having no arguments doesn't cause unexpected behaviors.
    """
    step = MockStep()
    step.parseArgs()
    assert isinstance(step.args, Namespace)
    assert vars(step.args) == {}
