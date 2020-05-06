#!/bin/bash
docker build . -f Dockerfile -t ryanlaycock/dependency-network-analysis:1.0.0
docker push ryanlaycock/dependency-network-analysis:1.0.0
