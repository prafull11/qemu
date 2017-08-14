import operator
import os
import random
import subprocess

paths = ['/tmp/overlay', '/tmp/base.qcow2',
         '/tmp/overlay.qcow2', '/tmp/q1.qcow2', '/tmp/q1.raw',
         '/tmp/extents.test']
 
def test_iteration(extents):

    for p in paths:
        os.path.exists(p) and os.remove(p)

    cmds =  ["dd if=/dev/urandom of=/tmp/base bs=1M count=1024",
             "cp /tmp/base /tmp/overlay",
            ]

    for item in extents:
       cmds.append("dd if=/dev/urandom of=/tmp/overlay conv=nocreat,notrunc "
                   "seek=%d bs=1 count=%d" % (item['offset'], item['length']))

    with open("/tmp/extents.test", "w") as f:
        f.write('Offset   Length  Type\n')
        for item in extents:
            f.write("%d %d data\n" % (item['offset'], item['length']))

    cmds += [
             "./qemu-img convert -f raw -O qcow2 -W -E /tmp/extents.test -D /tmp/base /tmp/overlay /tmp/q1.qcow2",
             "./qemu-img info /tmp/q1.qcow2",
             "./qemu-img convert -f qcow2 -O raw /tmp/q1.qcow2 /tmp/q1.raw",
             "stat /tmp/q1.raw",
             "cmp /tmp/q1.raw /tmp/overlay"
            ]

    for cmd in cmds:
        print cmd
        subprocess.call(cmd.split())

for i in range(10):
    extents = [];
    for j in range(4096 * 1024, 64 * 1024 * 1024, 4096 * 1024):
        extents.append({'offset': j,
                        'length': random.randrange(1024 * 6) * 512})
    test_iteration(extents)
