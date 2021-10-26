import operator
import os
import random
import subprocess
from pathlib import Path

images_path = os.path.join(os.getcwd(), "tmp")
Path(images_path).mkdir(parents=True, exist_ok=True)

paths = [os.path.join(images_path, 'overlay'), os.path.join(images_path, 'base.qcow2'),
         os.path.join(images_path, 'overlay.qcow2'), os.path.join(images_path, 'q1.qcow2'), os.path.join(images_path, 'q1.raw'),
         os.path.join(images_path, 'extents.test')]
 
def test_iteration(extents):

    for p in paths:
        os.path.exists(p) and os.remove(p)

    cmds =  ["dd if=/dev/urandom of=%s bs=1M count=1024" % os.path.join(images_path, "base"),
             "cp %s %s" % (os.path.join(images_path, "base"), os.path.join(images_path, "overlay")),
             "./qemu-img convert -f raw -O qcow2 %s %s" % (os.path.join(images_path, "base"), os.path.join(images_path, "base.qcow2")),
             "stat %s" % os.path.join(images_path, "base.qcow2"), 
             "cp %s %s" % (os.path.join(images_path, "base.qcow2"), os.path.join(images_path, "base.qcow2.bak")),
             "./qemu-img info %s" % os.path.join(images_path, "base.qcow2"),
            ]

    for item in extents:
       cmds.append("dd if=/dev/urandom of=%s conv=nocreat,notrunc "
                   "seek=%d bs=1 count=%d" % (os.path.join(images_path, "overlay"), item['offset'], item['length']))

    with open(os.path.join(images_path, "extents.test"), "w") as f:
        f.write('Offset   Length  Type\n')
        for item in extents:
            f.write("%d %d data\n" % (item['offset'], item['length']))

    cmds += [
             "stat %s" % os.path.join(images_path, "base.qcow2"),
             "./qemu-img create -f qcow2 -b %s %s" % (os.path.join(images_path, "base.qcow2"), os.path.join(images_path, "q1.qcow2")),
             "./qemu-img convert -f raw -O qcow2 -W -E %s -D %s %s %s" % (os.path.join(images_path, "extents.test"), os.path.join(images_path, "base.qcow2"), os.path.join(images_path, "overlay"), os.path.join(images_path, "q1.qcow2")),
             "./qemu-img info %s" % os.path.join(images_path, "q1.qcow2"),
             "./qemu-img convert -f qcow2 -O raw %s %s" % (os.path.join(images_path, "q1.qcow2"), os.path.join(images_path, "q1.raw")),
             "stat %s" % os.path.join(images_path, "q1.qcow2")
            ]

    for cmd in cmds:
        print(cmd)
        my_env = os.environ.copy()
        my_env["LD_LIBRARY_PATH"] = ".:" + my_env.get("LD_LIBRARY_PATH". "")
        subprocess.Popen(cmd.split(), env=my_env).wait()
    cmd = "cmp %s %s" % (os.path.join(images_path, "q1.raw"), os.path.join(images_path, "overlay"))
    print(cmd)
    assert subprocess.call(cmd.split()) == 0

for i in range(100):
    extents = [];
    print("Iteration: ----- %d -----" % i)
    for j in range(4096 * 1024, 64 * 1024 * 1024, 4096 * 1024):
        extents.append({'offset': j + random.randrange(1024),
                        'length': random.randrange(1024 * 1024)})
    test_iteration(extents)
