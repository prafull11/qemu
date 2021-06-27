import os
import random
import subprocess

#images_path = "/var/triliovault-mounts/test1/"
images_path = os.path.join(os.getcwd(), "/home/murali/fusemnt/tmp")
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
    cmds.append("./qemu-img convert -p -f raw %s -O qcow2  %s" % (os.path.join(images_path, "base"), os.path.join(images_path, "base.qcow2")))
    cmds.append("./qemu-img convert -p -f raw --object secret,id=sec2,data=backing %s -O qcow2 -o encrypt.format=luks,encrypt.key-secret=sec2 %s" % (os.path.join(images_path, "base"), os.path.join(images_path, "base-encr.qcow2")))
    cmds.append("./qemu-img compare -p --object secret,id=sec0,data=backing --image-opts driver=raw,file.filename=%s --image-opts driver=qcow2,encrypt.key-secret=sec0,file.filename=%s" % (os.path.join(images_path, 'base'), os.path.join(images_path, 'base-encr.qcow2')))
    for i in range(1000):
       blk = random.randrange(10240)
       cmds.append("dd if=/dev/urandom of=%s conv=nocreat,notrunc seek=%d bs=512 count=1" % (os.path.join(images_path, 'overlay'), blk))
    cmds.append("./qemu-img convert -p -f raw %s -O qcow2  %s" % (os.path.join(images_path, "overlay"), os.path.join(images_path, "overlay.qcow2")))
    cmds.append("./qemu-img convert -p -f raw --object secret,id=sec2,data=backing %s -O qcow2 -o encrypt.format=luks,encrypt.key-secret=sec2 %s" % (os.path.join(images_path, "overlay"), os.path.join(images_path, "overlay-encr.qcow2")))
    cmds.append("./qemu-img compare -p -f raw --object secret,id=sec2,data=backing %s -O qcow2 -o encrypt.format=luks,encrypt.key-secret=sec2 %s" % (os.path.join(images_path, "overlay"), os.path.join(images_path, "overlay-encr.qcow2")))
    cmds.append("stat %s" % os.path.join(images_path, "overlay"))
    cmds.append("stat %s" % os.path.join(images_path, "overlay.qcow2"))
    cmds.append("stat %s" % os.path.join(images_path, "overlay-encr.qcow2"))

    cmds += [
             "./qemu-img convert -f raw -O qcow2 -D %s -F raw %s %s" % (os.path.join(images_path, "base"),  os.path.join(images_path, "overlay"), os.path.join(images_path, "q1.qcow2")),
             "./qemu-img rebase -u -b %s %s" % (os.path.join(images_path, "base"), os.path.join(images_path, "q1.qcow2")),
             "./qemu-img convert -f qcow2 -O qcow2 -D %s -F qcow2 %s %s" % (os.path.join(images_path, "base.qcow2"),  os.path.join(images_path, "overlay.qcow2"), os.path.join(images_path, "q2.qcow2")),
             "./qemu-img rebase -u -b %s %s" % (os.path.join(images_path, "base.qcow2"), os.path.join(images_path, "q2.qcow2")),
             "./qemu-img convert --object secret,id=sec0,data=backing --image-opts driver=qcow2,encrypt.key-secret=sec0,file.filename=%s -D %s -O qcow2 -o encrypt.format=luks,encrypt.key-secret=sec0 %s" % (os.path.join(images_path, "overlay-encr.qcow2"), os.path.join(images_path, "base.qcow2"), os.path.join(images_path, "q3.qcow2")),
             "./qemu-img rebase  --object secret,id=sec0,data=backing --image-opts driver=qcow2,encrypt.key-secret=sec0,file.filename=%s -b %s" % (os.path.join(images_path, "q3.qcow2"), os.path.join(images_path, "base.qcow2")),
             "./qemu-img compare -p --object secret,id=sec2,data=backing --image-opts driver=raw,file.filename=%s --image-opts driver=qcow2,encrypt.format=luks,encrypt.key-secret=sec2,file.filename=%s" % (os.path.join(images_path, "overlay"), os.path.join(images_path, "q3.qcow2")),

             "./qemu-img create -f qcow2 --object secret,id=sec0,data=backing -b 'json:{ \"encrypt.key-secret\": \"sec0\", \"driver\": \"qcow2\", \"file\": { \"driver\": \"file\", \"filename\": \"%s\" }}' -o encrypt.format=luks,encrypt.key-secret=sec0 %s" % (os.path.join(images_path, "base-encr.qcow2"), os.path.join(images_path, "q4.qcow2")),
             "./qemu-img convert -n --object secret,id=sec0,data=backing --object secret,id=sec2,data=backing --base-image-opts driver=qcow2,encrypt.key-secret=sec0,file.filename=%s --image-opts driver=qcow2,encrypt.key-secret=sec0,file.filename=%s --target-image-opts driver=qcow2,encrypt.format=luks,encrypt.key-secret=sec2,file.filename=%s" % (os.path.join(images_path, "base-encr.qcow2"),  os.path.join(images_path, "overlay-encr.qcow2"), os.path.join(images_path, "q4.qcow2")),
             "./qemu-img compare -p --object secret,id=sec2,data=backing --object secret,id=sec0,data=backing --image-opts driver=raw,file.filename=%s --image-opts driver=qcow2,encrypt.format=luks,encrypt.key-secret=sec2,file.filename=%s" % (os.path.join(images_path, "overlay"), os.path.join(images_path, "q4.qcow2")),
             "./qemu-img info %s" % os.path.join(images_path, "q1.qcow2"),
             "./qemu-img info %s" % os.path.join(images_path, "q2.qcow2"),
             "./qemu-img info %s" % os.path.join(images_path, "q3.qcow2"),
             "./qemu-img info %s" % os.path.join(images_path, "q4.qcow2"),
             "./qemu-img convert -f qcow2 -O raw %s %s" % (os.path.join(images_path, "q1.qcow2"), os.path.join(images_path, "q1.raw")),
             "./qemu-img convert -f qcow2 -O raw %s %s" % (os.path.join(images_path, "q2.qcow2"), os.path.join(images_path, "q2.raw")),
             "./qemu-img convert --object secret,id=sec0,data=backing --image-opts driver=qcow2,encrypt.key-secret=sec0,file.filename=%s -O raw %s" % (os.path.join(images_path, "q3.qcow2"), os.path.join(images_path, "q3.raw")),
             "./qemu-img convert --object secret,id=sec0,data=backing --image-opts driver=qcow2,encrypt.key-secret=sec0,file.filename=%s -O raw %s" % (os.path.join(images_path, "q4.qcow2"), os.path.join(images_path, "q4.raw")),
             "stat %s" % os.path.join(images_path, "q1.raw"),
             "stat %s" % os.path.join(images_path, "q2.raw"),
             "stat %s" % os.path.join(images_path, "q3.raw"),
             "stat %s" % os.path.join(images_path, "q4.raw"),
            ]

    for i in range(1):
        for cmd in cmds:
            c = []
            for t in cmd.split("'"):
                if 'json' not in t:
                    c += t.split()
                else:
                    c.append(t)
            print(c)
            subprocess.call(c)
        cmp_command = "cmp %s %s" % (os.path.join(images_path, "q1.raw"), os.path.join(images_path, "overlay"))
        assert subprocess.call(cmp_command.split()) == 0
        cmp_command = "cmp %s %s" % (os.path.join(images_path, "q2.raw"), os.path.join(images_path, "overlay"))
        assert subprocess.call(cmp_command.split()) == 0
        cmp_command = "cmp %s %s" % (os.path.join(images_path, "q3.raw"), os.path.join(images_path, "overlay"))
        assert subprocess.call(cmp_command.split()) == 0
        cmp_command = "cmp %s %s" % (os.path.join(images_path, "q4.raw"), os.path.join(images_path, "overlay"))
        assert subprocess.call(cmp_command.split()) == 0
