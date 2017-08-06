import subprocess
import os

paths = ['/tmp/base.raw', '/tmp/overlay.raw', '/tmp/base.qcow2', '/tmp/overlay.qcow2',
         '/tmp/q1.qcow2', '/tmp/q1.raw']
 
for p in paths:
    os.path.exists(p) and os.remove(p)

cmds = ["dd if=/dev/urandom of=/tmp/base bs=1M count=1024",
        "cp /tmp/base /tmp/overlay",
        "dd if=/dev/urandom of=/tmp/overlay conv=nocreat,notrunc seek=1 bs=1M count=1",
        "./qemu-img convert -f raw -O qcow2 -D /tmp/base /tmp/overlay /tmp/q1.qcow2",
        "./qemu-img convert -f qcow2 -O raw /tmp/q1.qcow2 /tmp/q1.raw",
        "stat /tmp/q1.raw",
       ]

for cmd in cmds:
    print cmd
    subprocess.call(cmd.split())
