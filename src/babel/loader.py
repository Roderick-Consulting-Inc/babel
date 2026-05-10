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
"""Load a Babel parameter sheet from YAML on disk.

The loader is deliberately thin: it reads the file, yamls it, and hands
the resulting dict to Pydantic. All validation happens in
`babel.schema`. A YAML file that violates the schema will surface a
``pydantic.ValidationError`` with the specific field path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from babel.schema import LanguageSpec


def load_spec(path: str | Path) -> LanguageSpec:
    """Read a YAML file and validate it as a `LanguageSpec`.

    Raises:
        FileNotFoundError: if the path does not exist.
        yaml.YAMLError: if the file is not parseable as YAML.
        pydantic.ValidationError: if the resulting dict does not match
            the schema (this is the common case for a malformed sheet).
    """
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"parameter sheet not found: {path}")
    with p.open("r", encoding="utf-8") as fh:
        data: Any = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(
            f"parameter sheet at {path} must be a YAML mapping at the top level, "
            f"got {type(data).__name__}"
        )
    return LanguageSpec.model_validate(data)


def load_spec_from_string(content: str) -> LanguageSpec:
    """Validate a YAML string as a `LanguageSpec`.

    Convenience for tests and for callers that already hold the YAML in
    memory.
    """
    data: Any = yaml.safe_load(content)
    if not isinstance(data, dict):
        raise ValueError("parameter sheet must be a YAML mapping at the top level")
    return LanguageSpec.model_validate(data)
