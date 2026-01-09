#!/usr/bin/expect -f
# 自动化SSH执行脚本
# 使用方法: ./ssh_exec.sh "command1; command2; ..."

set timeout 30
set host "124.221.58.149"
set user "ubuntu"
set password "wine2025@"
set commands [lindex $argv 0]

spawn ssh -o StrictHostKeyChecking=no ${user}@${host}

expect {
    "password:" {
        send "${password}\r"
        exp_continue
    }
    "Permission denied" {
        send_user "❌ SSH认证失败\n"
        exit 1
    }
    -re "\\\$ |# " {
        send "${commands}\r"
        expect {
            -re "\\\$ |# " {
                # 命令执行完成
            }
            timeout {
                # 超时也继续
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

expect eof

