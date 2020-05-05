#!/bin/bash
docker build . -f Dockerfile -t ryanlaycock/dependency-network-analysis:0.0.1
docker push ryanlaycock/dependency-network-analysis:0.0.1
