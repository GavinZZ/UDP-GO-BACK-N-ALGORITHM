# UDP-GO-BACK-N-ALGORITHM

There are total 4 files present, nEmulator-linux386, packet.py, sender.py, receiver.py.

## How to run:
1. Make sure to use chmod to make sure you are able to execute each file.
2. On Host One, run `./nEmulator-linux386 9991 host2 9994 9993 host3 9992 1 0.2 0`
3. On Host Two, run `python3 receiver.py host1 9993 9994 <output-file>`
4. On Host Three, run `python3 sender.py host1 9991 9992 <input-file>`

## Behaviour:
1. If there is an error message, `Wrong Number of Arguments Given`, please make sure the arguments passed are correct.
2. Sender will parse the entire file and read 500 bytes of data and create a packet.
3. Receiver will output the data into <output-file> specified, and generate `arrival.log` containing all the sequence number arriving.
4. Sender will output `ack.log` and `seqnum.log` as required.
5. EOT will never lost.

## NOTE:
1. Please make sure to use `python3` to run to avoid errors.
