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
from typing import cast, Self, Any

from abc import ABC, abstractmethod
from threading import Lock

class Resource(ABC):
    """
    Base class for all Resources. Implements a singleton pattern to ensure
    only one instance of each Resource subclass exists globally.

    If in need of cleaning up at garbage collection, use `weakref.finalize`.
    """
    _instances: dict[type[Self], Self] = {}
    _lock = Lock()

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__new__(cls)
                cls._instances[cls] = instance
        return cast(Self, cls._instances[cls])

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        if not getattr(self, '_initialized', False):
            self.initialize(*args, **kwargs)
            self._initialized: bool = True

    @abstractmethod
    def initialize(self) -> None:
        """
        Subclasses must implement this method for any initialization logic.
        """
        pass

