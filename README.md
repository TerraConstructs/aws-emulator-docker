# AWS Emulator container image (TerraConstructs)

[![Build and publish](https://github.com/TerraConstructs/aws-emulator-docker/actions/workflows/release.yml/badge.svg)](https://github.com/TerraConstructs/aws-emulator-docker/actions/workflows/release.yml)
[![Lint](https://github.com/TerraConstructs/aws-emulator-docker/actions/workflows/lint.yml/badge.svg)](https://github.com/TerraConstructs/aws-emulator-docker/actions/workflows/lint.yml)

A multi-arch (`linux/amd64`, `linux/arm64`) container image of the
[AWS Emulator](https://github.com/aws/aws-emulator), used by the
[TerraConstructs](https://github.com/TerraConstructs/base) integration tests and workshops.

This repository is derived from
[xSAVIKx/aws-emulator-docker](https://github.com/xSAVIKx/aws-emulator-docker) by Yurii
Serhiichuk. Its README documents the entrypoint, the health check and the optional TLS
front end in detail; they behave the same here. What differs:

- Only the Amazon Linux variant is built, and only to `ghcr.io/terraconstructs/aws-emulator`.
- A new emulator version is published on purpose (push to `main` or `workflow_dispatch`),
  not by an hourly upstream check.
- The examples, testcontainers modules and project site are removed.
- Planned: the image will package a patched emulator build that fixes gaps hit by the
  TerraConstructs tests. Until then it packages the upstream LTS package.

This is not an official AWS image.

## Run

```sh
mkdir -p ~/.aws/emulator
docker run --rm -p 127.0.0.1:9297:9297 --user "$(id -u):$(id -g)" \
  -e HOME="$HOME" -v "$HOME/.aws/emulator:$HOME/.aws/emulator" \
  ghcr.io/terraconstructs/aws-emulator -p 9297
```

Then point the AWS CLI or an SDK at it:

```sh
export AWS_ENDPOINT_URL=https://127.0.0.1:9297
export AWS_SHARED_CREDENTIALS_FILE=~/.aws/emulator/9297/emulator_credentials
export AWS_CONFIG_FILE=~/.aws/emulator/9297/config
export AWS_CA_BUNDLE=~/.aws/emulator/9297/ca.pem
export AWS_EC2_METADATA_DISABLED=true
export AWS_DISABLE_HOST_PREFIX_INJECTION=true
export AWS_REGION=us-east-1 AWS_DEFAULT_REGION=us-east-1
unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN AWS_PROFILE

aws sts get-caller-identity   # Account: 000000000000
```

In GitHub Actions, use [TerraConstructs/run-aws-emulator](https://github.com/TerraConstructs/run-aws-emulator).

## Tags

| Tag | Moves? |
|---|---|
| `<upstream>-<yyyymmdd>.<run>` (build tag), for example `1.0.598.1-20261125.3` | Never |
| `<upstream>`, for example `1.0.598.1` | On a rebuild of that version |
| `<version>`, for example `1.0.598` | On a new package of that version |
| `latest` | On every publish |
| `sha-<commit>` | Never |

Pin by digest: `ghcr.io/terraconstructs/aws-emulator:1.0.598.1@sha256:...`. Each
[release](https://github.com/TerraConstructs/aws-emulator-docker/releases) lists the digest.

## Supply chain

- Base images are pinned by digest.
- The upstream `.rpm` package is checked against the AWS package signing key
  (`98BC F336 A3BE 53B7 34E9 67C5 2E5B F49B D940 F624`, [`keys/`](keys/)) and against the
  SHA-256 digests that CI records.
- Each image has a BuildKit SBOM and SLSA provenance (`mode=max`), a keyless cosign
  signature and a GitHub build provenance attestation.

Verify a signature (cosign v3 or later):

```sh
cosign verify ghcr.io/terraconstructs/aws-emulator:latest \
  --certificate-identity 'https://github.com/TerraConstructs/aws-emulator-docker/.github/workflows/release.yml@refs/heads/main' \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com

gh attestation verify oci://ghcr.io/terraconstructs/aws-emulator:latest --owner TerraConstructs
```

## Build it yourself

```sh
docker buildx build --load -t aws-emulator:dev .
tests/smoke.sh aws-emulator:dev
tests/tls.sh aws-emulator:dev
```

To build another version, pass `--build-arg EMULATOR_VERSION=<version>`, with a version from
[`versions.json`](https://downloads.aws.com/aws-emulator/packages/aws-emulator/LTS/versions.json).
To also check the SHA-256 digests, pass `--build-arg RPM_SHA256_AMD64=<sha>` and
`--build-arg RPM_SHA256_ARM64=<sha>`.

## Licenses

- The files in this repository: [Apache License 2.0](LICENSE). Copyright 2026 Yurii
  Serhiichuk, with modifications by TerraConstructs contributors. See [NOTICE](NOTICE).
- The AWS Emulator: CC0 1.0 Universal, with code in its `vendor/` directory under the
  Apache License 2.0. See [aws/aws-emulator](https://github.com/aws/aws-emulator).
- The base image `public.ecr.aws/amazonlinux/amazonlinux:2023-minimal`: see the licenses of
  its packages.
