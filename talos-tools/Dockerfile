FROM alpine:3.23
ARG TALOSCTL_VERSION=1.12.7
ARG KUBECTL_VERSION=1.36.0
ARG JQ_VERSION=1.8.1

RUN apk add --no-cache curl \
    && wget -qO /usr/local/bin/talosctl "https://github.com/siderolabs/talos/releases/download/v${TALOSCTL_VERSION}/talosctl-linux-amd64" \
    && wget -qO /usr/local/bin/kubectl "https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
    && wget -qO /usr/local/bin/jq "https://github.com/jqlang/jq/releases/download/jq-${JQ_VERSION}/jq-linux-amd64" \
    && chmod +x /usr/local/bin/talosctl /usr/local/bin/kubectl /usr/local/bin/jq
USER 65532:65532
