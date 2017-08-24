import os
import random
import subprocess

paths = ['/tmp/base.raw', '/tmp/overlay.raw', '/tmp/base.qcow2',
         '/tmp/overlay.qcow2', '/tmp/q1.qcow2', '/tmp/q1.raw']
 
for p in paths:
    os.path.exists(p) and os.remove(p)

cmds =  ["dd if=/dev/urandom of=/tmp/base bs=1M count=1024",
         "cp /tmp/base /tmp/overlay",
         #"./qemu-img convert -f raw -O qcow2 /tmp/base /tmp/base.qcow2",
        ]

for i in range(1000):
   cmds.append("dd if=/dev/urandom of=/tmp/overlay conv=nocreat,notrunc "
               "seek=%d bs=1M count=1" % random.randrange(1024))
cmds += [
         "./qemu-img convert -f raw -O qcow2 -D /tmp/base -F raw /tmp/overlay /tmp/q1.qcow2",
         "./qemu-img info /tmp/q1.qcow2",
         "./qemu-img convert -f qcow2 -O raw /tmp/q1.qcow2 /tmp/q1.raw",
         "stat /tmp/q1.raw",
        ]

for i in range(50):
    for cmd in cmds:
        print cmd
        subprocess.call(cmd.split())
    assert subprocess.call("cmp /tmp/q1.raw /tmp/overlay".split()) == 0
