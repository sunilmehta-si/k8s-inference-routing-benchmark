# The load client image: the irb package and the workload specs, nothing else. Built and loaded into kind by
# scripts/cluster-up.sh; PYTHON_IMAGE comes from deploy/versions.env, pinned by digest.
ARG PYTHON_IMAGE=docker.io/library/python:3.12.12-slim-bookworm@sha256:593bd06efe90efa80dc4eee3948be7c0fde4134606dd40d8dd8dbcade98e669c
FROM ${PYTHON_IMAGE}
WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY inference_routing_bench ./inference_routing_bench
COPY workloads ./workloads
RUN pip install --no-cache-dir . && useradd --uid 10001 --no-create-home --shell /usr/sbin/nologin irb
USER 10001
ENTRYPOINT ["irb"]
