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

# Tests related to Resource

from Skritt import Resource

class MyResource(Resource):
    def initialize(self, data: str='') -> None:
        self.data = data

class AnotherResource(Resource):
    def initialize(self, param: int=0) -> None:
        self.param = param

def test_singleton_behavior() -> None:
    """Test that the Resource class implements proper singleton behavior."""
    resource1 = MyResource(data="test_value")
    resource2 = MyResource(data="unused") # Subsequent instantiation should return the same instance
    assert resource1 is resource2
    assert resource2.data == "test_value"

def test_subclass_independence() -> None:
    """Test that different subclasses have independent singleton instances."""
    resource1 = MyResource(data="test_value")
    resource2 = AnotherResource(param=42)
    assert resource1 is not resource2
    assert resource1.data == "test_value"
    assert resource2.param == 42


class ThreadResource(Resource):
    def initialize(self, data: str='') -> None:
        self.data = data

def test_thread_safety() -> None:
    """Test that the singleton behavior is thread-safe."""
    from threading import Thread
    results = []

    def create_instance() -> None:
        resource = ThreadResource(data="thread_safe")
        results.append(resource)

    threads = [Thread(target=create_instance) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(r is results[0] for r in results)  # All threads should get the same instance
    assert results[0].data == "thread_safe"


class ParentResource(Resource):
    def initialize(self, data: str='') -> None:
        self.data = data + "+parent"

class SubResource(ParentResource):
    def initialize(self, data: str='') -> None:
        self.data = data + "+sub"

def test_inheritance() -> None:
    """Test that inheritance doesn't interfere with singleton behaviour."""
    resource1 = ParentResource(data="extra")
    resource2 = SubResource(data="inheritance")
    assert resource1 is not resource2
    assert resource1.data == "extra+parent"
    assert resource2.data == "inheritance+sub"
