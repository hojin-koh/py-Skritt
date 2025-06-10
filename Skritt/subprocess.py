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

from typing import no_type_check, Any
from collections.abc import Sequence

import asyncio
import os
from subprocess import PIPE
from threading import Thread

from .logging import TypeLogger

class ThreadForSubprocess(Thread):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._return: int = 0

    @no_type_check
    def run(self) -> None:
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    @no_type_check
    def join(self, *args: Any) -> int:
        super().join(*args)
        return self._return


async def logStream(logger: TypeLogger, stream: asyncio.StreamReader | None, pid: int) -> None:
    if stream is not None:
        while line := await stream.readline():
            logger.log(22, "({:d}) {}", pid, line.decode().strip())

async def shellrun(logger: TypeLogger, aEntries: Sequence[Sequence[str]]) -> int:
    aProcs: list[tuple[asyncio.subprocess.Process, str]] = []
    aPipes: list[tuple[int, int]] = []
    try:
        async with asyncio.TaskGroup() as tg:
            for i, entry in enumerate(aEntries):
                fdStdin = PIPE
                fdStdout = PIPE
                fdStderr = PIPE
                if i < len(aEntries)-1:
                    aPipes.append(os.pipe())
                    fdStdout = aPipes[i][1]
                if i > 0:
                    fdStdin = aPipes[i-1][0]

                proc = await asyncio.create_subprocess_exec(
                        entry[0], *(entry[1:]),
                        stdin=fdStdin,
                        stdout=fdStdout,
                        stderr=fdStderr,
                        )
                aProcs.append((proc, entry[0]))
                logger.debug("Spawn {:d} {}", proc.pid, " ".join(entry))

                tg.create_task(logStream(logger, proc.stderr, proc.pid))
                if i == len(aEntries)-1:
                    tg.create_task(logStream(logger, proc.stdout, proc.pid))

                if i < len(aEntries)-1:
                    os.close(aPipes[i][1])
                if i > 0:
                    os.close(aPipes[i-1][0])
            logger.info("Spawned {}", " ".join(F"{p.pid}({name})" for p,name in aProcs))
    finally:
        rtn = 0
        for p, name in aProcs:
            if p.returncode is None:
                p.terminate()
            await p.wait()
            if p.returncode is not None and p.returncode != 0:
                logger.error("Subprocess {:d} returned {:d}", p.pid, p.returncode)
                rtn = p.returncode
        return rtn

