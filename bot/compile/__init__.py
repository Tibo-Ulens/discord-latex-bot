import re
import logging

from . import latex, typst


logger = logging.getLogger("compile")


async def render(input: str) -> str:
    if input.startswith("$render latex"):
        match = re.search(
            r"^(?:\$render latex)\s*([^`]*)\s*(?:(?:\`\`\`)(?:(?:tex)|(?:latex))?\s*([\S\s]*)\s*(?:\`\`\`))?\s+(?:\`\`\`)(?:(?:tex)|(?:latex))?\s*([\S\s]*)\s*(?:\`\`\`)$",
            input,
            re.M | re.I,
        )

        if match is None:
            raise Exception("Invalid syntax")

        args = match.group(1) or ""
        head = match.group(2) or ""
        body = match.group(3)

        if body is None:
            raise Exception("No LaTeX code found")

        try:
            latex.compile(head, body, "output.png", "output.log")
        except Exception:
            with open("output.log") as log:
                output = log.read()

            errors = re.findall(r"![\S\s]*l\.\d+.*$", output, re.M)
            errors = "\n".join(errors)

            raise Exception(f"{errors}")

        return "output.png"
    elif input.startswith("$render typst"):
        match = re.search(
            r"^(?:\$render typst)\s*(?:\`\`\`)(?:typst)?\s*([\S\s]*)\s*(?:\`\`\`)$",
            input,
            re.M | re.I,
        )

        if match is None:
            raise Exception("Invalid syntax")

        code = match.group(1)

        if code is None:
            raise Exception("No typst code found")

        try:
            typst.compile(code, "output.png", "output.log")
        except Exception as e:
            logger.error(e)
            with open("output.log") as log:
                output = log.read()

            raise Exception(output)

        return "output.png"
