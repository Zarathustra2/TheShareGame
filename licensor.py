"""
Copyright 2020 Dario Heinisch. All rights reserved.
Use of this source code is governed by a AGPL-3.0
license that can be found in the LICENSE.txt file.
"""

import os
import re

license = ["Copyright 2020 Dario Heinisch. All rights reserved.\n",
           "Use of this source code is governed by a AGPL-3.0\n",
           "license that can be found in the LICENSE.txt file."]

extensions = [".go", ".py"]
excluded_directories = [".venv", "migrations", "frontend", "latex"]
excluded_files = [
    "manage.py"
]


def get_doc_license(filename: str):
    if filename.endswith(".go"):
        return "//" + "//".join(license) + "\n\n"

    if filename.endswith(".py"):
        return "\"\"\"\n" + "".join(license) + "\n\"\"\"\n\n"

    raise ValueError(f"File {filename} could not be processed")


def main():
    files = []
    for r, d, f in os.walk("."):

        # Filter directories out which do net get a license header
        if any([ex in r for ex in excluded_directories]):
            continue

        for file in f:

            if any(file.endswith(ex) for ex in excluded_files):
                continue

            # Update only those files which have a valid extension
            if any([file.endswith(ext) for ext in extensions]):
                files.append(os.path.join(r, file))

    for f in files:
        with open(f, "r") as original:
            data = original.read()

        res = re.match("\"\"\"(.|\n)*Copyright(.|\n)*\"\"\"", data)
        # TODO: Add golang regex

        if f.endswith(".go"):
            continue

        doc_license = get_doc_license(f)

        if res is not None and res.group(0).replace("\n", "").strip() == doc_license.replace("\n", "").strip():
            continue

        with open(f, "w") as modified:
            if res is None:
                modified.write(doc_license + data)
                modified.close()
            else:
                modified.write(doc_license + data.replace(res.group(0), ""))
                modified.close()


if __name__ == "__main__":
    main()
