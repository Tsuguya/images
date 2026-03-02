FROM alpine:3.23

ARG GH_VERSION=2.74.1
ARG SPIN_VERSION=3.6.2

RUN apk add --no-cache \
      bash curl git libgcc libstdc++ ripgrep \
      rustup gcc musl-dev \
    && curl -fsSL https://claude.ai/install.sh | sh \
    && mv /root/.local/bin/claude /usr/local/bin/claude \
    && rustup-init -y --default-toolchain stable --profile minimal --target wasm32-wasip1 \
    && . /root/.cargo/env \
    && cp -a /root/.cargo /usr/local/cargo \
    && cp -a /root/.rustup /usr/local/rustup \
    && wget -qO /tmp/gh.tar.gz "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_amd64.tar.gz" \
    && tar xzf /tmp/gh.tar.gz -C /tmp && mv /tmp/gh_${GH_VERSION}_linux_amd64/bin/gh /usr/local/bin/ \
    && wget -qO /tmp/spin.tar.gz "https://github.com/spinframework/spin/releases/download/v${SPIN_VERSION}/spin-v${SPIN_VERSION}-linux-amd64.tar.gz" \
    && tar xzf /tmp/spin.tar.gz -C /usr/local/bin spin \
    && chmod +x /usr/local/bin/gh /usr/local/bin/spin /usr/local/bin/claude \
    && rm -rf /tmp/* /root/.cargo /root/.rustup /root/.local

ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH="/usr/local/cargo/bin:${PATH}" \
    USE_BUILTIN_RIPGREP=0

USER 65532:65532
