FROM alpine:3.23
ARG JQ_VERSION=1.8.1
ARG KUBECTL_VERSION=1.35.4
ARG GH_VERSION=2.90.0
ARG YQ_VERSION=4.53.2
ARG COSIGN_VERSION=3.0.5
ARG ARGOCD_VERSION=3.3.4

RUN apk add --no-cache curl git openssl \
    && wget -qO /usr/local/bin/jq "https://github.com/jqlang/jq/releases/download/jq-${JQ_VERSION}/jq-linux-amd64" \
    && wget -qO /usr/local/bin/kubectl "https://dl.k8s.io/release/v${KUBECTL_VERSION}/bin/linux/amd64/kubectl" \
    && wget -qO /tmp/gh.tar.gz "https://github.com/cli/cli/releases/download/v${GH_VERSION}/gh_${GH_VERSION}_linux_amd64.tar.gz" \
    && tar xzf /tmp/gh.tar.gz -C /tmp && mv /tmp/gh_${GH_VERSION}_linux_amd64/bin/gh /usr/local/bin/ && rm -rf /tmp/gh* \
    && wget -qO /usr/local/bin/yq "https://github.com/mikefarah/yq/releases/download/v${YQ_VERSION}/yq_linux_amd64" \
    && wget -qO /usr/local/bin/cosign "https://github.com/sigstore/cosign/releases/download/v${COSIGN_VERSION}/cosign-linux-amd64" \
    && wget -qO /usr/local/bin/argocd "https://github.com/argoproj/argo-cd/releases/download/v${ARGOCD_VERSION}/argocd-linux-amd64" \
    && chmod +x /usr/local/bin/jq /usr/local/bin/kubectl /usr/local/bin/gh /usr/local/bin/yq /usr/local/bin/cosign /usr/local/bin/argocd
COPY --chmod=755 github-auth.sh github-signed-commit.sh /usr/local/bin/
USER 65532:65532
