Setup a new machine
===================

```bash
scp setup.sh run.sh MACHINE:
ssh MACHINE
ssh-keygen -p -N "" -f ~/.ssh/id_rsa -t rsa
# Add the pub key to your GitHub account if the repo is private

sudo visudo
# ALL            ALL = (ALL) NOPASSWD: ALL

./setup.sh -k  # or -s or -a
crontab -e
0 0 * * * source /home/user/.bashrc; run.sh -r  # or -s or -a
```
