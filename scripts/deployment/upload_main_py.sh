#!/usr/bin/expect -f
# 直接上传main.py文件到服务器

set timeout 60
set host "124.221.58.149"
set user "ubuntu"
set password "wine2025@"
set local_file "/Users/scarlett/Projects/BeatSync/web_service/backend/main.py"
set remote_file "/opt/beatsync/web_service/backend/main.py"

# 使用base64编码传输文件内容
spawn ssh -o StrictHostKeyChecking=no ${user}@${host}

expect {
    "password:" {
        send "${password}\r"
        exp_continue
    }
    -re "\\\$ |# " {
        # 读取本地文件并base64编码
        send "cat > /tmp/update_main.py << 'ENDOFFILE'\r"
        expect "> "
        
        # 读取本地文件内容
        set fp [open $local_file r]
        set file_content [read $fp]
        close $fp
        
        # 逐行发送（避免expect缓冲区问题）
        set lines [split $file_content "\n"]
        foreach line $lines {
            send "$line\r"
            expect "> "
        }
        
        send "ENDOFFILE\r"
        expect -re "\\\$ |# "
        
        # 备份原文件并替换
        send "sudo cp /opt/beatsync/web_service/backend/main.py /opt/beatsync/web_service/backend/main.py.backup.old\r"
        expect {
            "password:" {
                send "${password}\r"
                exp_continue
            }
            -re "\\\$ |# " {
                send "sudo cp /tmp/update_main.py /opt/beatsync/web_service/backend/main.py\r"
                expect {
                    "password:" {
                        send "${password}\r"
                        exp_continue
                    }
                    -re "\\\$ |# " {
                        send "cd /opt/beatsync/web_service/backend && wc -l main.py && grep -n '/api/subscription/products' main.py | head -1\r"
                        expect -re "\\\$ |# "
                        send "sudo systemctl restart beatsync\r"
                        expect {
                            "password:" {
                                send "${password}\r"
                                exp_continue
                            }
                            -re "\\\$ |# " {
                                send "sleep 3 && curl -s http://localhost:8000/api/subscription/products | head -10\r"
                                expect -re "\\\$ |# "
                            }
                        }
                    }
                }
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

