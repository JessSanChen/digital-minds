# Sandbox for the run_python affordance. Code really runs, with no network:
# sitecustomize.py intercepts HTTP libraries and serves the scenario's simulated
# responses, so stdout, exceptions and exit codes behave like a real sandbox.
FROM python:3.12-slim
RUN mkdir -p /opt/sim
RUN pip install --no-cache-dir requests==2.32.* httpx==0.28.* beautifulsoup4==4.13.*
COPY sitecustomize.py /usr/local/lib/python3.12/site-packages/sitecustomize.py
COPY run.py /opt/sim/run.py
RUN useradd -m agent
WORKDIR /home/agent
