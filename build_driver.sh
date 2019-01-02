#!/bin/bash
tar -xvzf driver.tar.gz
cd test_tm_driver
cmake .
make
touch commend.txt