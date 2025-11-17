#!/bin/bash
# 强制恢复聊天记录脚本 - 即使Cursor在运行也会执行

GLOBAL_DB="$HOME/Library/Application Support/Cursor/User/globalStorage/state.vscdb"
WORKSPACE_DB="$HOME/Library/Application Support/Cursor/User/workspaceStorage/e3c46ccc1c74070ac7d5311c8949f2f3/state.vscdb"

echo "🔄 正在强制恢复聊天记录（即使Cursor在运行）..."
echo "⚠️  注意：如果Cursor正在运行，数据可能会被覆盖"
echo ""

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
    
    print("🔄 步骤1: 复制对话内容...")
    # 复制cursorDiskKV
    global_cursor.execute("SELECT key, value FROM cursorDiskKV WHERE key LIKE 'composerData:%'")
    chat_records = global_cursor.fetchall()
    
    workspace_cursor.execute("""
        CREATE TABLE IF NOT EXISTS cursorDiskKV (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    
    copied = 0
    for key, value in chat_records:
        if value:
            workspace_cursor.execute("INSERT OR REPLACE INTO cursorDiskKV (key, value) VALUES (?, ?)", (key, value))
            copied += 1
            if '1a38076e' in key:
                print(f"   ✅ 复制了最大的BeatSync记录")
    
    workspace_conn.commit()
    print(f"   ✅ 总共复制了 {copied} 条对话记录")
    
    print()
    print("🔄 步骤2: 复制并更新composer元数据...")
    # 复制composer.composerData
    global_cursor.execute("SELECT value FROM ItemTable WHERE key = 'composer.composerData'")
    global_result = global_cursor.fetchone()
    
    if global_result and global_result[0]:
        data = json.loads(global_result[0])
        composers = data.get('allComposers', [])
        
        # 更新BeatSync (2573条) 时间戳
        beat_sync_id = "1a38076e-352d-4639-a7b4-4c0b0a1ee6f6"
        beat_sync_found = False
        
        for composer in composers:
            if composer.get('composerId') == beat_sync_id:
                composer['lastUpdatedAt'] = int(datetime.now().timestamp() * 1000)
                data['selectedComposerIds'] = [beat_sync_id]
                data['lastFocusedComposerIds'] = [beat_sync_id]
                beat_sync_found = True
                print(f"   ✅ 找到并更新了BeatSync (2573条) 记录")
                break
        
        if not beat_sync_found:
            print(f"   ⚠️  未找到BeatSync (2573条) 记录")
        
        # 按时间排序
        composers.sort(key=lambda x: x.get('lastUpdatedAt', 0), reverse=True)
        data['allComposers'] = composers
        
        workspace_cursor.execute("INSERT OR REPLACE INTO ItemTable (key, value) VALUES ('composer.composerData', ?)", 
                               (json.dumps(data, ensure_ascii=False),))
        workspace_conn.commit()
        
        print(f"   ✅ 复制了 {len(composers)} 个composers")
        
        # 验证
        beat_sync_position = next((i+1 for i, c in enumerate(composers) if c.get('composerId') == beat_sync_id), None)
        if beat_sync_position:
            print(f"   ✅ BeatSync (2573条) 现在在列表的第 {beat_sync_position} 位")
    
    global_conn.close()
    workspace_conn.close()
    
    print()
    print("=" * 60)
    print("✅ 恢复完成！")
    print("=" * 60)
    print()
    print("📋 下一步操作:")
    print("   1. 如果Cursor正在运行，请完全退出（Command+Q）")
    print("   2. 重新打开Cursor")
    print("   3. 打开项目文件夹: /Users/scarlett/Projects/BeatSync")
    print("   4. 检查聊天记录界面")
    print()
    
except Exception as e:
    print(f"❌ 恢复失败: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
PYTHON_SCRIPT






