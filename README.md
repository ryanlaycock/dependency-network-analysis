# Dependency Network Analysis
This component is a microservice built for the system detailed in the [infrastructure repo](https://github.com/ryanlaycock/software-network-analysis-infrastructure).
The docker container can be pulled from [here](https://hub.docker.com/r/ryanlaycock/dependency-network-analysis).

Dependency Network Analysis is a service written in Python using the Networkx library to perform social network analysis
on software dependency graphs, obtained from a Neo4j database. The service [exposes some endpoints](dependency-network-analysis.yaml) 
to trigger analysis that can be called as part of the overall system, or individually.