FROM alpine:3.23

ARG GH_VERSION=2.91.0
ARG SPIN_VERSION=4.0.0
ARG KUBECTL_VERSION=1.36.0
ARG HELM_VERSION=3.18.4
ARG LOGCLI_VERSION=3.6.7

RUN apk add --no-cache \
      bash curl git jq libgcc libstdc++ openssl ripgrep unzip \
      rustup gcc musl-dev

RUN curl -fsSL https://claude.ai/install.sh | bash \
    && cp /root/.local/share/claude/versions/* /usr/local/bin/claude \
    && chmod +x /usr/local/bin/claude \
    && rm -rf /root/.local

RUN rustup-init -y --default-toolchain stable --profile minimal --target wasm32-wasip1 \
    && . /root/.cargo/env \
    && cp -a /root/.cargo /usr/local/cargo \
    && cp -a /root/.rustup /usr/local/rustup \
    && rm -rf /root/.cargo /root/.rustup

RUN apk add --no-cache nodejs npm \
    && npm install -g pnpm@10.32.0

RUN wget -qO /tmp/gh.tar.gz "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_amd64.tar.gz" \
    && tar xzf /tmp/gh.tar.gz -C /tmp && mv /tmp/gh_${GH_VERSION}_linux_amd64/bin/gh /usr/local/bin/ \
    && wget -qO /tmp/spin.tar.gz "https://github.com/spinframework/spin/releases/download/v${SPIN_VERSION}/spin-v${SPIN_VERSION}-linux-amd64.tar.gz" \
    && tar xzf /tmp/spin.tar.gz -C /usr/local/bin spin \
    && wget -qO /usr/local/bin/kubectl "https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
    && wget -qO /tmp/helm.tar.gz "https://get.helm.sh/helm-v${HELM_VERSION}-linux-amd64.tar.gz" \
    && tar xzf /tmp/helm.tar.gz -C /tmp && mv /tmp/linux-amd64/helm /usr/local/bin/ \
    && wget -qO /tmp/logcli.zip "https://github.com/grafana/loki/releases/download/v${LOGCLI_VERSION}/logcli-linux-amd64.zip" \
    && unzip -o /tmp/logcli.zip -d /tmp && mv /tmp/logcli-linux-amd64 /usr/local/bin/logcli \
    && chmod +x /usr/local/bin/gh /usr/local/bin/spin /usr/local/bin/kubectl /usr/local/bin/helm /usr/local/bin/logcli \
    && rm -rf /tmp/*

ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    USE_BUILTIN_RIPGREP=0 \
    PNPM_HOME="/usr/local/share/pnpm"
ENV PATH="/usr/local/share/pnpm:/usr/local/cargo/bin:${PATH}"

USER 65532:65532
