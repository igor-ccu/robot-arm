#!/bin/bash
tar -xzf driver.tar.gz -C /Execute /try
cd Execute
cmake .
make 
cd ../try 
cmake .
make
cd ..
