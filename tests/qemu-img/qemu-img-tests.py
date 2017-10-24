import os
import random
import subprocess

paths = ['/home/centos/qemu-fork/qemu/build/tmp/base.raw', '/home/centos/qemu-fork/qemu/build/tmp/overlay.raw', '/home/centos/qemu-fork/qemu/build/tmp/base.qcow2',
         '/home/centos/qemu-fork/qemu/build/tmp/overlay.qcow2', '/home/centos/qemu-fork/qemu/build/tmp/q1.qcow2', '/home/centos/qemu-fork/qemu/build/tmp/q1.raw']
 
for p in paths:
    os.path.exists(p) and os.remove(p)

cmds =  ["dd if=/dev/urandom of=/home/centos/qemu-fork/qemu/build/tmp/base bs=1M count=1024",
         "cp /home/centos/qemu-fork/qemu/build/tmp/base /home/centos/qemu-fork/qemu/build/tmp/overlay",
         #"./qemu-img convert -f raw -O qcow2 /home/centos/qemu-fork/qemu/build/tmp/base /home/centos/qemu-fork/qemu/build/tmp/base.qcow2",
        ]

for i in range(100):
   cmds.append("dd if=/dev/urandom of=/home/centos/qemu-fork/qemu/build/tmp/overlay conv=nocreat,notrunc "
               "seek=%d bs=1024 count=1" % random.randrange(1024))
cmds += [
         "./qemu-img convert -f raw -O qcow2 -D /home/centos/qemu-fork/qemu/build/tmp/base -F raw /home/centos/qemu-fork/qemu/build/tmp/overlay /home/centos/qemu-fork/qemu/build/tmp/q1.qcow2",
         "./qemu-img info /home/centos/qemu-fork/qemu/build/tmp/q1.qcow2",
         "./qemu-img convert -f qcow2 -O raw /home/centos/qemu-fork/qemu/build/tmp/q1.qcow2 /home/centos/qemu-fork/qemu/build/tmp/q1.raw",
         "stat /home/centos/qemu-fork/qemu/build/tmp/q1.raw",
        ]

for i in range(50):
    for cmd in cmds:
        print cmd
        if 'qemu-img convert' in cmd:
        subprocess.call(cmd.split())
    assert subprocess.call("cmp /home/centos/qemu-fork/qemu/build/tmp/q1.raw /home/centos/qemu-fork/qemu/build/tmp/overlay".split()) == 0
