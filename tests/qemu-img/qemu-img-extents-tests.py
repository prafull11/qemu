import operator
import os
import random
import subprocess

paths = ['/home/centos/qemu-merge/qemu/build/tmp/overlay', '/home/centos/qemu-merge/qemu/build/tmp/base.qcow2',
         '/home/centos/qemu-merge/qemu/build/tmp/overlay.qcow2', '/home/centos/qemu-merge/qemu/build/tmp/q1.qcow2', '/home/centos/qemu-merge/qemu/build/tmp/q1.raw',
         '/home/centos/qemu-merge/qemu/build/tmp/extents.test']
 
def test_iteration(extents):

    for p in paths:
        os.path.exists(p) and os.remove(p)

    cmds =  ["dd if=/dev/urandom of=/home/centos/qemu-merge/qemu/build/tmp/base bs=1M count=1024",
             "cp /home/centos/qemu-merge/qemu/build/tmp/base /home/centos/qemu-merge/qemu/build/tmp/overlay",
             "./qemu-img convert -f raw -O qcow2 /home/centos/qemu-merge/qemu/build/tmp/base /home/centos/qemu-merge/qemu/build/tmp/base.qcow2",
             "stat /home/centos/qemu-merge/qemu/build/tmp/base.qcow2",
             "cp /home/centos/qemu-merge/qemu/build/tmp/base.qcow2 /home/centos/qemu-merge/qemu/build/tmp/base.qcow2.bak",
             "./qemu-img info /home/centos/qemu-merge/qemu/build/tmp/base.qcow2",
            ]

    for item in extents:
       cmds.append("dd if=/dev/urandom of=/home/centos/qemu-merge/qemu/build/tmp/overlay conv=nocreat,notrunc "
                   "seek=%d bs=1 count=%d" % (item['offset'], item['length']))

    with open("/home/centos/qemu-merge/qemu/build/tmp/extents.test", "w") as f:
        f.write('Offset   Length  Type\n')
        for item in extents:
            f.write("%d %d data\n" % (item['offset'], item['length']))

    cmds += [
             "stat /home/centos/qemu-merge/qemu/build/tmp/base.qcow2",
             "qemu-img create -f qcow2 -b /home/centos/qemu-merge/qemu/build/tmp/base.qcow2 /home/centos/qemu-merge/qemu/build/tmp/q1.qcow2",
             "./qemu-img convert -f raw -O qcow2 -W -E /home/centos/qemu-merge/qemu/build/tmp/extents.test -D /home/centos/qemu-merge/qemu/build/tmp/base.qcow2 /home/centos/qemu-merge/qemu/build/tmp/overlay /home/centos/qemu-merge/qemu/build/tmp/q1.qcow2",
             "./qemu-img info /home/centos/qemu-merge/qemu/build/tmp/q1.qcow2",
             "./qemu-img convert -f qcow2 -O raw /home/centos/qemu-merge/qemu/build/tmp/q1.qcow2 /home/centos/qemu-merge/qemu/build/tmp/q1.raw",
             "stat /home/centos/qemu-merge/qemu/build/tmp/q1.raw",
            ]

    for cmd in cmds:
        print cmd
        subprocess.call(cmd.split())
    print "cmp /home/centos/qemu-merge/qemu/build/tmp/q1.raw /home/centos/qemu-merge/qemu/build/tmp/overlay"
    assert subprocess.call("cmp /home/centos/qemu-merge/qemu/build/tmp/q1.raw /home/centos/qemu-merge/qemu/build/tmp/overlay".split()) == 0

for i in range(100):
    extents = [];
    print "Iteration: ----- %d -----" % i
    for j in range(4096 * 1024, 64 * 1024 * 1024, 4096 * 1024):
        extents.append({'offset': j + random.randrange(1024),
                        'length': random.randrange(1024 * 1024)})
    test_iteration(extents)
