python 3.10
ansible.runner
subprocess.run
panda
paramiko

python 3.10
sshpass
python-pip
ansible

# system-tools

[iptables]

iptables trong ubuntu không được cài đặt sẵn 
apt install iptables
tuy nhiên trong hệ điều hành ubuntu, iptables sẽ tự động reset và deactive môi khi reboot lại
để khắc phục tình trạng này cần cài đặt 
> apt install iptables-persistent
sau khi cài đặt sẽ có sinh ra 2 folder để lưu lại các rules của iptables
> /etc/profile/rules.v4
> /etc/profile/rules.v6
lúc này chúng ta cần active 1 package được cài đặt mặc định sẫn trong ubuntu là netfilter-persistent
> systemctl enable netfilter-persistent
> systemctl start netfilter-persistent
như vậy mỗi lần reboot package này sẽ lấy thông só đã được lưu của iptables và áp dụng.

[nf_contrack]

Mặc định không được cài đặt sẵn trong ubuntu
ssh> apt install conntrack
conntrack chỉ được kích hoạt auto sau khi reboot nếu có thông số này được cấu hình trong iptables
các thông số được cấu hình của nf_conntrack sẽ bị reset sau khi reboot ubuntu
Giải pháp sử dụng rc-local.services sẽ tự động triển khai các câu lệnh sau khi boot OS
> vi /etc/rc.local
> #!/bin/sh
> echo "524288" > /proc/sys/net/netfilter/nf_conntrack_max
> echo "131072" > /sys/module/nf_conntrack/parameters/hashsize
> exit 0
Khởi động dịch vụ rc-local
> systemctl enable rc-local && systemctl start rc-local

[kdump]

Mặc định không được cài đặt sẵn như trong CentOS
> apt install linux-crashdump
nếu như centos không được cài đặt sẵn 
> yum install kexec-tools
Cách kích hoạt và tên gọi trong ubuntu cũng sẽ khác
> systemctl enable kdump-tools
> systemctl start kdump-tools
ISSUES thường gặp: No memory reserved to start kdump trên Centos
Solved:
> sed -i 's/crashkernel=auto/crashkernel=128M/g' /etc/default/grub
> grub2-mkconfig -o /boot/grub2/grub.cfg
> systemctl restart kdump

[sendmail|postfix|SELinux]

Các phần mềm này đều không được cài đặt sẵn khi setup Ubuntu
SELinux được cài đặt mặc định trên CentOS
