import pexpect
import time
import os

#copy softwlc disk to system
print("Copying disk...")
os.system('dd if=/cdrom/softwlc.img of=/dev/nvme0n1 bs=64k conv=sync,noerror status=progress')
print("Copying complete")

print("Resizing disk...")
s = pexpect.spawn('parted -l')
s.expect('Warning:')
s.sendline('Fix')             #repair GPT
s.expect('Model:')
#resize disk to all spare space
s = pexpect.spawn('fdisk /dev/nvme0n1')
s.expect('Command')
s.sendline('d')               #delete old partition
s.expect('Partition')
time.sleep(2)
s.sendline('2')               #select /dev/sda2
s.expect('Command')
time.sleep(2)
s.sendline('n')               #create new partition
s.expect('Partition')
time.sleep(2)
s.sendline('2')              #new index of partition
s.expect('First')
time.sleep(2)
s.sendline()              #set first sector to default
s.expect('Last')
time.sleep(2)
s.sendline()               #set last sector to default
s.expect('Created')
time.sleep(2)
s.sendline('N')               #save ext4 signature
s.expect('Command')
time.sleep(2)
s.sendline('w')               #save new partition table
s.expect('Syncing')
time.sleep(2)
os.system('e2fsck -f /dev/nvme0n1p2')
os.system('resize2fs /dev/nvme0n1p2')         #resize filesystem
print('Resizing complete')