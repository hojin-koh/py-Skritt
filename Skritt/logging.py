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

import os
import sys

def setupFdForDisplay(num: int = 6) -> bool:
    """
    Open a fd to write to stderr without logging as in the legacy framework.
    Mainly for subprocesses to inherit this file descriptor to display
    things like progress bars that don't need to go into the log file.

    Return False and no-op if that fd is already open, otherwise open it and
    return True.
    """
    try:
        os.fstat(num) # Check if already open
        return False
    except OSError:
        os.dup2(sys.stderr.fileno(), num, inheritable=True)
        return True
