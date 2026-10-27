"""Read pyproject.toml, write requirements.txt."""  # noqa: INP001

import tomllib
from pathlib import Path

p_in = Path(__file__).parent.parent / "pyproject.toml"
p_out = Path(__file__).parent.parent / "requirements.txt"

with p_in.open("rb") as fh:
    o = tomllib.load(fh)

lst = sorted(o["project"]["dependencies"], key=str.casefold)
lst = [
    x.replace("~=", ">=")
    for x in lst
    if "bcrypt" in x
    or "dotenv" in x
    or "fastapi" in x
    or "genai" in x
    or "google-genai" in x
    or "jwt" in x
    or "mistralai" in x
    or "numpy" in x
    or "openai" in x
    or "pandas" in x
    or "pyarrow" in x
    or "pydantic" in x
    or "sentry" in x
    or "slowapi" in x
]

print(lst)

p_out.write_text(
    "# created by gen_requirements.py from pyproject.toml\n" + "\n".join(lst) + "\n"
)
