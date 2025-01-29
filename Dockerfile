FROM python:3.13-slim

ENV DEBIAN_FRONTEND=noninteractive
# Disable pip cache and poetry venvs
ENV PIP_NO_CACHE_DIR=false \
	POETRY_VIRTUALENVS_CREATE=false

# Get poetry
RUN pip install -U poetry

RUN apt update \
	&& apt install -y --no-install-recommends \
	   texlive \
	   texlive-fonts-extra texlive-latex-extra texlive-science \
	   texlive-pictures texlive-plain-generic \
	   cm-super dvipng imagemagick \
	   curl xz-utils \
	&& rm -rf /var/lib/apt/lists/*

RUN curl -L https://github.com/typst/typst/releases/download/v0.12.0/typst-x86_64-unknown-linux-musl.tar.xz -o typst.tar.xz
RUN tar xf typst.tar.xz
RUN mv typst-x86_64-unknown-linux-musl/typst /usr/bin/

# Fix imagemagick being annoying
RUN sed -i '/<policy domain="coder" rights="none" pattern="PDF" \/>/c\<policy domain="coder" rights="read|write" pattern="PDF" \/>' /etc/ImageMagick-6/policy.xml

WORKDIR /example-discord-bot

# Install deps
COPY pyproject.toml poetry.lock ./
RUN poetry install

COPY ./template.tex ./template.tex

COPY ./bot ./bot

CMD [ "python3", "-m", "bot" ]
