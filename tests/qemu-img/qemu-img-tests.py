import os
import random
import subprocess

for mainloop in range(1):
    print "Iteration %d" % mainloop
    paths = ['/var/triliovault-mounts/test1/base.raw', '/var/triliovault-mounts/test1/overlay.raw', '/var/triliovault-mounts/test1/base.qcow2',
             '/var/triliovault-mounts/test1/overlay.qcow2', '/var/triliovault-mounts/test1/q1.qcow2', '/var/triliovault-mounts/test1/q1.raw']
 
    for p in paths:
        os.path.exists(p) and os.remove(p)

    cmds =  ["dd if=/dev/urandom of=/var/triliovault-mounts/test1/base bs=1M count=1024",
             "cp /var/triliovault-mounts/test1/base /var/triliovault-mounts/test1/overlay",
             #"./qemu-img convert -f raw -O qcow2 /var/triliovault-mounts/test1/base /var/triliovault-mounts/test1/base.qcow2",
            ]

    cmds.append("stat /var/triliovault-mounts/test1/base")
    cmds.append("stat /var/triliovault-mounts/test1/overlay")
    for i in range(100):
       cmds.append("dd if=/dev/urandom of=/var/triliovault-mounts/test1/overlay conv=nocreat,notrunc "
                   "seek=%d bs=1024 count=1" % random.randrange(1024))
       cmds.append("stat /var/triliovault-mounts/test1/overlay")
    cmds += [
             "./qemu-img convert -f raw -O qcow2 -D /var/triliovault-mounts/test1/base -F raw /var/triliovault-mounts/test1/overlay /var/triliovault-mounts/test1/q1.qcow2",
             "./qemu-img info /var/triliovault-mounts/test1/q1.qcow2",
             "./qemu-img convert -f qcow2 -O raw /var/triliovault-mounts/test1/q1.qcow2 /root/q1.raw",
             "cp /root/q1.raw /var/triliovault-mounts/test1/q1.raw",
             "stat /var/triliovault-mounts/test1/q1.raw",
            ]

    for i in range(1):
        for cmd in cmds:
            print cmd
            #if 'qemu-img convert' in cmd:
            subprocess.call(cmd.split())
        assert subprocess.call("cmp /var/triliovault-mounts/test1/q1.raw /var/triliovault-mounts/test1/overlay".split()) == 0
