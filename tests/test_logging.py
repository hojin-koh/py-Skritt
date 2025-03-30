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

# Tests related to Logging-related resources

import re
import tempfile

from Skritt.logging import ResourceLogger

import pytest

def test_logger_initialization() -> None:
    from loguru import logger
    resLogging = ResourceLogger()
    assert hasattr(resLogging, 'logger')
    assert resLogging.logger == logger

def test_default_stderr_logging(capfd: pytest.CaptureFixture[str]) -> None:
    resLogging = ResourceLogger()
    resLogging.logger.info("Test stderr message")

    captured = capfd.readouterr()
    assert "Test stderr message" in captured.err
    assert re.search(r"\d{8} \d{6} \[I\]", captured.err) # Test the message format

def test_file_logging() -> None:
    resLogging = ResourceLogger()

    with tempfile.NamedTemporaryFile() as tmp:
        handler_id = resLogging.setFile(tmp.name)

        test_message = "Test file logging message"
        resLogging.logger.debug(test_message)

        with open(tmp.name) as f:
            content = f.read()
            assert test_message in content
            assert re.search(r"\d{8} \d{6} \[D\]", content)

        # Test sink removal
        resLogging.removeSink(handler_id)
        resLogging.logger.debug("This should not be logged")

        with open(tmp.name) as f:
            new_content = f.read()
            assert new_content == content  # Content shouldn't change

def test_multiple_sinks() -> None:
    # Test multiple file sinks
    resLogging = ResourceLogger()

    with tempfile.NamedTemporaryFile() as tmp1, tempfile.NamedTemporaryFile() as tmp2:

        h1 = resLogging.setFile(tmp1.name)
        h2 = resLogging.setFile(tmp2.name)

        resLogging.logger.debug("Test multiple sinks")

        # Verify all files received the message
        for file in (tmp1.name, tmp2.name):
            with open(file) as fp:
                assert "Test multiple sinks" in fp.read()

        # Remove one sink and test
        resLogging.removeSink(h1)
        resLogging.logger.debug("After removing first sink")

        with open(tmp1.name) as f:
            content1 = f.read()
        with open(tmp2.name) as f:
            content2 = f.read()

        assert "After removing first sink" not in content1
        assert "After removing first sink" in content2

        resLogging.removeSink(h2)

def test_remove_nonexistent_handler() -> None:
    resLogging = ResourceLogger()

    with pytest.raises(ValueError):
        resLogging.removeSink(999999)
