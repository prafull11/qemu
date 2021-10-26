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

    cmds =  [("dd if=/dev/urandom of=%s bs=1M count=1024" % os.path.join(images_path, "base")).split(),
             ("cp %s %s" % (os.path.join(images_path, "base"), os.path.join(images_path, "overlay"))).split(),
             ("./qemu-img convert -p --object secret,id=sec0,data=backing --object secret,id=sec2,data=backing --image-opts driver=raw,file.filename=%s -O qcow2 -o encrypt.format=luks,encrypt.key-secret=sec2 %s" % (os.path.join(images_path, "base"), os.path.join(images_path, "base.qcow2"))).split(),
             ("stat %s" % os.path.join(images_path, "base.qcow2")).split(),
             ("./qemu-img convert -p --object secret,id=sec0,data=backing --object secret,id=sec2,data=backing "
             "--image-opts driver=qcow2,encrypt.key-secret=sec0,file.filename=%s -O qcow2 -o "
             "encrypt.format=aes,encrypt.key-secret=sec2 %s" % (os.path.join(images_path, "base.qcow2"), os.path.join(images_path, "convert.qcow2"))).split(),
             ("cp %s %s" % (os.path.join(images_path, "base.qcow2"), os.path.join(images_path, "base.qcow2.bak"))).split(),
             ("./qemu-img info %s" % os.path.join(images_path, "base.qcow2")).split(),
            ]

    for item in extents:
       cmds.append(("dd if=/dev/urandom of=tmp/overlay conv=nocreat,notrunc "
                    "seek=%d bs=1 count=%d" % (item['offset'], item['length'])).split())

    with open("tmp/extents.test", "w") as f:
        f.write('Offset   Length  Type\n')
        for item in extents:
            f.write("%d %d data\n" % (item['offset'], item['length']))
    json_payload = 'json:{ "encrypt.key-secret": "sec0", "driver": "qcow2", "file": { "driver": "file", "filename": "%s" }}' % os.path.join(images_path, "base.qcow2"),
    ext_cnvt = "./qemu-img create -f qcow2 --object secret,id=sec0,data=backing -F qcow2 -b".split()
    ext_cnvt.append("%s" %json_payload)
    ext_cnvt += ("-o encrypt.format=luks,encrypt.key-secret=sec0 %s 1G" % os.path.join(images_path, "overlay.qcow2")).split()
    cmds += [
             ("stat %s" % os.path.join(images_path, "base.qcow2")).split(),

             ext_cnvt,

             ("./qemu-img convert -n -p --object secret,id=sec0,data=backing --image-opts driver=raw,file.filename=%s -W -E %s -F raw --base-image-opts driver=raw,file.filename=%s --target-image-opts driver=qcow2,encrypt.format=luks,encrypt.key-secret=sec0,file.filename=%s" % (os.path.join(images_path, "overlay"), os.path.join(images_path, "extents.test"), os.path.join(images_path, "base"), os.path.join(images_path, "overlay.qcow2"))).split(),

             ("./qemu-img info %s" % os.path.join(images_path, "overlay.qcow2")).split(),

             ("./qemu-img convert --object secret,id=sec0,data=backing -O raw "
             "--image-opts driver=qcow2,encrypt.key-secret=sec0,file.filename=%s %s" % (os.path.join(images_path, "overlay.qcow2"), os.path.join(images_path, "overlay.raw"))).split(),
             ("stat %s" % os.path.join(images_path, "overlay.raw")).split()
            ]

    for cmd in cmds:
        print(cmd)
        my_env = os.environ.copy()
        my_env["LD_LIBRARY_PATH"] = ".:" + my_env["LD_LIBRARY_PATH"]
        subprocess.Popen(cmd, env=my_env).wait()
    print("cmp %s %s" % (os.path.join(images_path, "overlay.raw"), os.path.join(images_path, "overlay")))
    assert subprocess.call(("cmp %s %s" % (os.path.join(images_path, "overlay.raw"), os.path.join(images_path, "overlay"))).split()) == 0

for i in range(100):
    extents = [];
    print("Iteration: ----- %d -----" % i)
    for j in range(4096 * 1024, 64 * 1024 * 1024, 4096 * 1024):
        extents.append({'offset': j + random.randrange(1024),
                        'length': random.randrange(1024 * 1024)})
    test_iteration(extents)
