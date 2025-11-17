#!/usr/bin/env python3
"""
列出所有Cursor聊天记录及其ID
方便选择要保存的对话
"""

import sqlite3
import json
import os
from datetime import datetime

def main():
    global_db = os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage/state.vscdb")
    
    if not os.path.exists(global_db):
        print("❌ 错误: 找不到全局数据库")
        return
    
    try:
        conn = sqlite3.connect(global_db)
        cursor = conn.cursor()
        
        # 获取composer.composerData
        cursor.execute("SELECT value FROM ItemTable WHERE key = 'composer.composerData'")
        result = cursor.fetchone()
        
        if not result or not result[0]:
            print("❌ 未找到聊天记录")
            return
        
        data = json.loads(result[0])
        composers = data.get('allComposers', [])
        
        # 按最后更新时间排序
        composers.sort(key=lambda x: x.get('lastUpdatedAt', 0), reverse=True)
        
        print("=" * 80)
        print("Cursor 聊天记录列表")
        print("=" * 80)
        print()
        print(f"总共 {len(composers)} 条聊天记录")
        print()
        
        for i, composer in enumerate(composers, 1):
            name = composer.get('name', '未命名')
            composer_id = composer.get('composerId', '')
            subtitle = composer.get('subtitle', '')
            last_updated = composer.get('lastUpdatedAt', 0)
            
            if last_updated:
                updated_time = datetime.fromtimestamp(last_updated / 1000).strftime('%Y-%m-%d %H:%M:%S')
                days_ago = (datetime.now().timestamp() * 1000 - last_updated) / (1000 * 60 * 60 * 24)
                time_str = f"{updated_time} ({int(days_ago)}天前)"
            else:
                time_str = "未知"
            
            print(f"{i:2d}. {name}")
            print(f"    ID: {composer_id}")
            print(f"    描述: {subtitle}")
            print(f"    最后更新: {time_str}")
            print()
        
        conn.close()
        
        print("=" * 80)
        print("💡 提示: 使用以下命令保存聊天记录:")
        print("   python3 save_chat_message.py save --id <ID> --title \"标题\" --tags \"标签1,标签2\"")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()




