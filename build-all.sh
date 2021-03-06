#!/usr/bin/env bash
set -e
set -o pipefail
set -u

workdir=$(dirname $(readlink -e $0))
cd ${workdir}

# just avoid double confirmations
./build-env.sh
export CANOPSIS_ENV_CONFIRM=0

# launch all builds
./build-docker.sh
./build-packages.sh
