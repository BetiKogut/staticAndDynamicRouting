#!/usr/bin/env bash

simple_switch_CLI --thrift-port 9091 < ./controlplane-rules/s1-controlplane
simple_switch_CLI --thrift-port 9092 < ./controlplane-rules/s2-controlplane
simple_switch_CLI --thrift-port 9093 < ./controlplane-rules/s3-controlplane
simple_switch_CLI --thrift-port 9094 < ./controlplane-rules/s4-controlplane
simple_switch_CLI --thrift-port 9095 < ./controlplane-rules/s5-controlplane