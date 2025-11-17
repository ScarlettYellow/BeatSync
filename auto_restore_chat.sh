#!/bin/bash
# 自动恢复聊天记录脚本 - 在Cursor关闭后运行

GLOBAL_DB="$HOME/Library/Application Support/Cursor/User/globalStorage/state.vscdb"
WORKSPACE_DB="$HOME/Library/Application Support/Cursor/User/workspaceStorage/e3c46ccc1c74070ac7d5311c8949f2f3/state.vscdb"

# 检查Cursor是否在运行
if pgrep -f "Cursor" > /dev/null; then
    echo "⚠️  Cursor仍在运行，请先退出Cursor（Command+Q）"
    exit 1
fi

echo "🔄 正在恢复聊天记录..."

python3 << 'PYTHON_SCRIPT'
import sqlite3
import json
import os
from datetime import datetime

global_db = os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/state.vscdb")
workspace_db = os.path.expanduser("~/Library/Application Support/Cursor/User/workspaceStorage/e3c46ccc1c74070ac7d5311c8949f2f3/state.vscdb")

try:
    global_conn = sqlite3.connect(global_db)
    workspace_conn = sqlite3.connect(workspace_db)
    
    global_cursor = global_conn.cursor()
    workspace_cursor = workspace_conn.cursor()
    
    # 1. 复制对话内容
    global_cursor.execute("SELECT key, value FROM cursorDiskKV WHERE key LIKE 'composerData:%'")
    chat_records = global_cursor.fetchall()
    
    workspace_cursor.execute("""
        CREATE TABLE IF NOT EXISTS cursorDiskKV (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    for key, value in chat_records:
        if value:
            workspace_cursor.execute("INSERT OR REPLACE INTO cursorDiskKV (key, value) VALUES (?, ?)", (key, value))
    
    workspace_conn.commit()
    
    # 2. 复制并更新composer元数据
    global_cursor.execute("SELECT value FROM ItemTable WHERE key = 'composer.composerData'")
    global_result = global_cursor.fetchone()
    
    if global_result:
        data = json.loads(global_result[0])
        
        # 更新BeatSync (2573条) 时间戳
        beat_sync_id = "1a38076e-352d-4639-a7b4-4c0b0a1ee6f6"
        for composer in data.get('allComposers', []):
            if composer.get('composerId') == beat_sync_id:
                composer['lastUpdatedAt'] = int(datetime.now().timestamp() * 1000)
                data['selectedComposerIds'] = [beat_sync_id]
                data['lastFocusedComposerIds'] = [beat_sync_id]
                break
        
        data['allComposers'].sort(key=lambda x: x.get('lastUpdatedAt', 0), reverse=True)
        
        workspace_cursor.execute("INSERT OR REPLACE INTO ItemTable (key, value) VALUES ('composer.composerData', ?)", 
                               (json.dumps(data, ensure_ascii=False),))
        workspace_conn.commit()
    
    global_conn.close()
    workspace_conn.close()
    
    print("✅ 聊天记录已恢复到工作区")
    
except Exception as e:
    print(f"❌ 恢复失败: {e}")
    exit(1)
PYTHON_SCRIPT

echo "✅ 完成！现在可以打开Cursor了"






