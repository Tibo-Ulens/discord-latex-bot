import os
import subprocess
import shutil
import tempfile
import logging


logger = logging.getLogger("typst")


def compile(code: str, dest_path: str, log_path: str):
    with tempfile.TemporaryDirectory() as tmp_dir:
        src_file = os.path.join(tmp_dir, "tmp.typ")
        pdf_file = os.path.join(tmp_dir, "tmp.pdf")
        png_file = os.path.join(tmp_dir, "tmp.png")
        typst_log_file = os.path.join(tmp_dir, "typst.log")
        magick_log_file = os.path.join(tmp_dir, "magick.log")

        with open(src_file, "w") as f:
            f.write(code)

        with open(typst_log_file, "w") as tlog:
            tlog.write("a")

        try:
            tlog = open(typst_log_file, "w+")
            logger.info("compiling typst to pdf")
            subprocess.check_call(
                ["typst", "compile", src_file],
                cwd=tmp_dir,
                stderr=tlog,
            )
            tlog.close()
        except Exception as e:
            tlog.close()
            logger.error(f"typst exception: {e}")
            with open(typst_log_file, "r") as tlog:
                logger.error(tlog.read())

            shutil.copy(typst_log_file, log_path)

            raise e

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

            raise e

        shutil.copy(png_file, dest_path)
