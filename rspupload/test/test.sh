#!/bin/bash

for run in {1..100}
do
  sleep 2 
  echo "stdout content" >&2
  echo "sterr content" >&1
done