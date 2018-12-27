# robot-arm
ROBOT ARM 107年 PROJECT 

## Execute
Only files that were executed on the robot are in here.
Remember to **build test_tm driver** on your machine.

## try
Only files that need to be yet tested on the robot.

## calib
Calibration program and photos. Also the output matrices mtx and dst.

## test_photos
This is self-explenatory. ( :

# What needs to be done
* 12/27: test new main.py on robot (try folder)


* ~~ cleaning up Execute folder and the files inside!!!!!! this is really messy ~~
* ~~ using new code for circles detection when scanning horizontally when looking for markers ~~

# Driver
To control the robot you need to download the driver [here](https://github.com/kentsai0319/test_tm_driver).

* To start the test program:
```
$ ./test_tm_driver 192.168.0.10
```

* To use build_driver.sh
```
$ sudo chmod +x build_driver.sh
$ sudo ./build_driver.sh
```