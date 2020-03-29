#!/usr/bin/env bash

# Install flow rules for switch S1
simple_switch_CLI --thrift-port 9090 < s1-routingtable

# Install flow rules for switch S2
simple_switch_CLI --thrift-port 9091 < s2-routingtable

# Install flow rules for switch S3
simple_switch_CLI --thrift-port 9092 < s3-routingtable