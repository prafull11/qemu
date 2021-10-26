import os
import random
import subprocess
from pathlib import Path

images_path = os.path.join(os.getcwd(), "tmp")
Path(images_path).mkdir(parents=True, exist_ok=True)

for mainloop in range(1):
    print("Iteration %d" % mainloop)
    paths = [os.path.join(images_path, 'base.raw'), os.path.join(images_path, 'overlay.raw'), os.path.join(images_path, 'base.qcow2'),
             os.path.join(images_path, 'overlay.qcow2'), os.path.join(images_path, 'q1.qcow2'), os.path.join(images_path, 'q1.raw')]
 
    for p in paths:
        os.path.exists(p) and os.remove(p)

    cmds =  ["dd if=/dev/urandom of=%s bs=1M count=10240" % os.path.join(images_path, 'base'),
             "cp %s %s" % (os.path.join(images_path, 'base'), os.path.join(images_path, 'overlay')),
            ]

    cmds.append("stat %s" % os.path.join(images_path, "base"))
    cmds.append("stat %s" % os.path.join(images_path, "overlay"))
    for i in range(1000):
       cmds.append("dd if=/dev/urandom of=%s conv=nocreat,notrunc seek=%d bs=1024 count=1" % (os.path.join(images_path, 'overlay'), random.randrange(10240)))
       cmds.append("stat %s" % os.path.join(images_path, "overlay"))
    cmds += [
             "./qemu-img convert -f raw -O qcow2 -D %s -F raw %s %s" % (os.path.join(images_path, "base"),  os.path.join(images_path, "overlay"), os.path.join(images_path, "q1.qcow2")),
             "./qemu-img rebase -u -f qcow2 -F raw -b %s %s" % (os.path.join(images_path, "base"),  os.path.join(images_path, "q1.qcow2")),
             "./qemu-img info %s" % os.path.join(images_path, "q1.qcow2"),
             "./qemu-img convert -f qcow2 -O raw %s %s" % (os.path.join(images_path, "q1.qcow2"), os.path.join(images_path, "q1.raw")),
             "stat %s" % os.path.join(images_path, "q1.raw"),
            ]

    for i in range(1):
        for cmd in cmds:
            print(cmd)
            #if 'qemu-img convert' in cmd:
            my_env = os.environ.copy()
            my_env["LD_LIBRARY_PATH"] = ".:" + my_env["LD_LIBRARY_PATH"]
            subprocess.Popen(cmd.split(), env=my_env).wait()
        cmp_command = "cmp %s %s" % (os.path.join(images_path, "q1.raw"), os.path.join(images_path, "overlay"))
        print(cmp_command)
        assert subprocess.call(cmp_command.split()) == 0
        print(cmp_command)
