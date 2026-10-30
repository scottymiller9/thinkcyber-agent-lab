FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
      nmap whatweb sqlmap curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

ARG TARGETARCH
RUN curl -sSL "https://github.com/ffuf/ffuf/releases/download/v2.1.0/ffuf_2.1.0_linux_${TARGETARCH}.tar.gz" \
    | tar -xz -C /usr/local/bin ffuf

WORKDIR /workspace
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD ["python", "-m", "agent.run"]
