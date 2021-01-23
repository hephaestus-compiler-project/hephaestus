Setup a new machine
===================

The machines we use have a single root user.

```bash
scp setup.sh run.sh MACHINE:
ssh MACHINE
ssh-keygen
# Add the pub key to your GitHub account if the repo is private

./setup.sh -k  # or -s or -a
# Setup cron job
apt install postfix python3.9-gdbm # In postfix select only local
crontab -e

PATH=/sbin:/bin:/usr/sbin:/usr/bin
MAILTO=root
HOME=/root/
SHELL=/bin/bash
0 0 1-31/2 * * /root/bin/run.sh -k # or -s or -a
# to check the logs you can run
journalctl -u cron
# to ge tthe output of cron runs
cat /var/mail/root
```
