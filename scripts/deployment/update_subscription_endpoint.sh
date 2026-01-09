#!/usr/bin/expect -f
# 更新服务器上的订阅端点
# 将本地main.py中的订阅相关代码添加到服务器

set timeout 60
set host "124.221.58.149"
set user "ubuntu"
set password "wine2025@"

spawn ssh -o StrictHostKeyChecking=no ${user}@${host}

expect {
    "password:" {
        send "${password}\r"
        exp_continue
    }
    -re "\\\$ |# " {
        # 先备份原文件
        send "cd /opt/beatsync/web_service/backend && cp main.py main.py.backup\r"
        expect -re "\\\$ |# "
        
        # 从GitHub拉取最新代码（如果本地代码已推送）
        send "cd /opt/beatsync && git fetch origin && git reset --hard origin/main\r"
        expect -re "\\\$ |# "
        
        # 检查更新后的文件
        send "cd /opt/beatsync/web_service/backend && wc -l main.py && grep -n '/api/subscription/products' main.py || echo '端点不存在'\r"
        expect -re "\\\$ |# "
        
        # 重启服务
        send "sudo systemctl restart beatsync\r"
        expect {
            "password:" {
                send "${password}\r"
                exp_continue
            }
            -re "\\\$ |# " {
                send "sleep 2\r"
                expect -re "\\\$ |# "
                send "sudo systemctl status beatsync --no-pager | head -10\r"
                expect -re "\\\$ |# "
            }
        }
        
        send "exit\r"
        expect eof
    }
    timeout {
        send_user "❌ 连接超时\n"
        exit 1
    }
}

