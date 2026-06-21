# GSK-LeanBio — reproducible toolchain.
#
# The Python core is dependency-free; the only reason this image is not
# `python:slim` alone is `bsl verify`, which needs a real Lean 4 kernel.
#
#   docker build -t gsk-leanbio .
#   docker run --rm gsk-leanbio check  examples/A-enzyme-kinetics/model.bsl
#   docker run --rm gsk-leanbio verify examples/C-hill/model.bsl
FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates git \
    && rm -rf /var/lib/apt/lists/*

# Lean 4 via elan (standard route). On networks that block lean-lang.org, pull
# the toolchain tarball from GitHub releases instead — see docs/limitations.md.
RUN curl -fsSL https://elan.lean-lang.org/elan-init.sh \
      | sh -s -- -y --default-toolchain stable
ENV PATH="/root/.elan/bin:${PATH}"

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .

ENTRYPOINT ["bsl"]
CMD ["--help"]
