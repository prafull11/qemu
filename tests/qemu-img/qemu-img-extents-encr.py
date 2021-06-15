import operator
import os
import random
import subprocess

paths = ['tmp/overlay',
         'tmp/base.qcow2',
         'tmp/overlay.qcow2',
         'tmp/q1.qcow2',
         'tmp/q1.raw',
         'tmp/extents.test']
 

def test_iteration(extents):

    for p in paths:
        os.path.exists(p) and os.remove(p)

    cmds =  ["dd if=/dev/urandom of=tmp/base bs=1M count=1024".split(),
             "cp tmp/base tmp/overlay".split(),
             "./qemu-img create --object secret,id=sec0,data=backing -f qcow2 -o encrypt.format=luks,encrypt.key-secret=sec0 tmp/base.qcow2 1G".split(),
             "stat tmp/base.qcow2".split(),

             "./qemu-img convert -p --object secret,id=sec0,data=backing --object secret,id=sec2,data=convert "
             "--image-opts driver=qcow2,encrypt.key-secret=sec0,file.filename=tmp/base.qcow2 -O qcow2 -o "
             "encrypt.format=aes,encrypt.key-secret=sec2 tmp/convert.qcow2".split(),

             "cp tmp/base.qcow2 tmp/base.qcow2.bak".split(),
             "./qemu-img info tmp/base.qcow2".split(),
             "./qemu-img info tmp/convert.qcow2".split(),
            ]

    #for item in extents:
       #cmds.append(("dd if=/dev/urandom of=tmp/overlay conv=nocreat,notrunc "
                   #"seek=%d bs=1 count=%d" % (item['offset'], item['length'])).split())

    with open("tmp/extents.test", "w") as f:
        f.write('Offset   Length  Type\n')
        for item in extents:
            f.write("%d %d data\n" % (item['offset'], item['length']))
    json_payload = 'json:{ "encrypt.key-secret": "sec0", "driver": "qcow2", "file": { "driver": "file", "filename": "tmp/base.qcow2" }}'
    ext_cnvt = "./qemu-img create -f qcow2 --object secret,id=sec0,data=backing -b".split()
    ext_cnvt.append("%s" %json_payload)
    ext_cnvt += "-o encrypt.format=luks,encrypt.key-secret=sec0 tmp/overlay1.qcow2 1G".split()
    cmds += [
             "stat tmp/base.qcow2".split(),

             ext_cnvt,

             "./qemu-img convert -f raw -W -E tmp/extents.test -D tmp/base "
             "tmp/overlay --object secret,id=sec0,data=backing -o encrypt.format=luks,encrypt.key-secret=sec0 tmp/q1.qcow2".split(),

             "./qemu-img info tmp/q1.qcow2".split(),

             "./qemu-img convert --object secret,id=sec0,data=backing -O raw "
             "--image-opts driver=qcow2,encrypt.key-secret=sec0,file.filename=tmp/q1.qcow2 tmp/q1.raw".split(),
             "stat tmp/q1.raw".split()
            ]

    for cmd in cmds:
        if 'q1.qcow2' in cmds:
            import pdb;pdb.set_trace()
        print(cmd)
        subprocess.call(cmd)
    print("cmp tmp/q1.raw tmp/overlay")
    assert subprocess.call("cmp tmp/q1.raw tmp/overlay".split()) == 0

for i in range(100):
    extents = [];
    print("Iteration: ----- %d -----" % i)
    for j in range(4096 * 1024, 64 * 1024 * 1024, 4096 * 1024):
        extents.append({'offset': j + random.randrange(1024),
                        'length': random.randrange(1024 * 1024)})
    test_iteration(extents)
