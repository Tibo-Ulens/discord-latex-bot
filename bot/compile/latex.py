import os
import subprocess
import shutil
import tempfile
import logging


logger = logging.getLogger("latex")


def compile(head: str, body: str, dest_path: str, log_path: str):
    with open("template.tex", "r") as template:
        template_str = template.read()

    source = template_str.replace(r"%%% HEAD %%%", head).replace(r"%%% BODY %%%", body)

    with tempfile.TemporaryDirectory() as tmp_dir:
        src_file = os.path.join(tmp_dir, "tmp.tex")
        pdf_file = os.path.join(tmp_dir, "tmp.pdf")
        png_file = os.path.join(tmp_dir, "tmp.png")
        latex_log_file = os.path.join(tmp_dir, "tmp.log")
        magick_log_file = os.path.join(tmp_dir, "magick.log")

        with open(src_file, "w") as f:
            f.write(source)

        with open(os.devnull, "w") as null:
            try:
                logger.info("compiling latex to pdf")
                subprocess.check_call(
                    [
                        "latex",
                        "-no-file-line-error",
                        "-halt-on-error",
                        "-output-format=pdf",
                        src_file,
                    ],
                    cwd=tmp_dir,
                    stdout=null,
                    stderr=null,
                )
            except Exception as e:
                logger.error(f"latex exception: {e}")
                with open(latex_log_file, "r") as f:
                    logger.error(f.read())

                shutil.copy(latex_log_file, log_path)

                raise (e)

            try:
                logger.info("converting pdf to png")

                output = subprocess.check_output(
                    [
                        "convert",
                        "-density",
                        "400",
                        pdf_file,
                        "-background",
                        "white",
                        "-alpha",
                        "remove",
                        f"PNG32:{png_file}",
                    ],
                    cwd=tmp_dir,
                )
                output = str(output)
            except Exception as e:
                logger.error(f"magick exception: {e}")
                logger.error(output)

                with open(magick_log_file, "w") as f:
                    f.write(output)

                shutil.copy(magick_log_file, log_path)

                raise (e)

            shutil.copy(png_file, dest_path)
