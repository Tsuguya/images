FROM alpine:3.23

ARG GH_VERSION=2.87.3
ARG SPIN_VERSION=3.6.2

RUN apk add --no-cache \
      bash curl git jq libgcc libstdc++ openssl ripgrep \
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
    && chmod +x /usr/local/bin/gh /usr/local/bin/spin \
    && rm -rf /tmp/*

ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    USE_BUILTIN_RIPGREP=0 \
    PNPM_HOME="/usr/local/share/pnpm"
ENV PATH="/usr/local/share/pnpm:/usr/local/cargo/bin:${PATH}"

USER 65532:65532
