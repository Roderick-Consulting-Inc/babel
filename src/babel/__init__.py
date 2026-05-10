# Copyright 2026 Roderick Consulting Inc.
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
"""Babel — a parameter-driven generator for esoteric programming languages.

The package exposes the parameter schema (Pydantic models), a YAML loader,
and three output emitters: an interpreter, a transpiler, and a markdown
specification page.

The current vertical slice covers the Brainfuck-tape base machine
end-to-end. The schema is open to other base machines (stack, OISC,
fungeoid, etc.) but the implementation only covers the tape family.
"""

__version__ = "0.1.0"

from babel.schema import (
    BaseMachine,
    CellWidth,
    Encoding,
    InstructionOp,
    IOModel,
    LanguageSpec,
    MemoryShape,
    MetaParameters,
)

__all__ = [
    "BaseMachine",
    "CellWidth",
    "Encoding",
    "InstructionOp",
    "IOModel",
    "LanguageSpec",
    "MemoryShape",
    "MetaParameters",
    "__version__",
]
