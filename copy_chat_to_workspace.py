#!/usr/bin/env python3
"""
将全局数据库中的聊天记录复制到工作区数据库
确保工作区能看到所有聊天记录
"""

import sqlite3
import json
import os
import sys
from datetime import datetime

global_storage_dir = os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage")
workspace_storage_dir = os.path.expanduser("~/Library/Application Support/Cursor/User/workspaceStorage/e3c46ccc1c74070ac7d5311c8949f2f3")

global_db = os.path.join(global_storage_dir, "state.vscdb")
workspace_db = os.path.join(workspace_storage_dir, "state.vscdb")

def main():
    print("=" * 60)
    print("复制聊天记录到工作区数据库")
    print("=" * 60)
    print()
    
    if not os.path.exists(global_db):
        print(f"❌ 错误: 找不到全局数据库 {global_db}")
        sys.exit(1)
    
    if not os.path.exists(workspace_db):
        print(f"❌ 错误: 找不到工作区数据库 {workspace_db}")
        sys.exit(1)
    
    # 备份工作区数据库
    backup_path = workspace_db + f".backup_before_copy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"📦 备份工作区数据库...")
    import shutil
    shutil.copy2(workspace_db, backup_path)
    print(f"✅ 已备份到: {os.path.basename(backup_path)}")
    print()
    
    try:
        # 连接数据库
        global_conn = sqlite3.connect(global_db)
        workspace_conn = sqlite3.connect(workspace_db)
        
        global_cursor = global_conn.cursor()
        workspace_cursor = workspace_conn.cursor()
        
        # 1. 从全局数据库获取composer.composerData
        print("🔍 读取全局composer.composerData...")
        global_cursor.execute("SELECT value FROM ItemTable WHERE key = 'composer.composerData'")
        global_result = global_cursor.fetchone()
        
        if not global_result or not global_result[0]:
            print("❌ 全局composer.composerData为空")
            sys.exit(1)
        
        global_composer_data = json.loads(global_result[0])
        global_composers = global_composer_data.get('allComposers', [])
        print(f"   找到 {len(global_composers)} 个composers")
        
        # 找到最大的BeatSync记录
        beat_sync_composer = None
        for composer in global_composers:
            if '1a38076e' in composer.get('composerId', ''):
                beat_sync_composer = composer
                break
        
        if beat_sync_composer:
            print(f"   ✅ 找到最大的BeatSync记录: {beat_sync_composer.get('name')} ({beat_sync_composer.get('subtitle')})")
        else:
            print("   ⚠️  未找到最大的BeatSync记录")
        
        # 2. 复制所有对话内容到工作区（cursorDiskKV表）
        print()
        print("🔄 复制对话内容到工作区...")
        global_cursor.execute("SELECT key, value FROM cursorDiskKV WHERE key LIKE 'composerData:%'")
        all_chat_records = global_cursor.fetchall()
        
        print(f"   找到 {len(all_chat_records)} 条对话记录")
        
        # 确保工作区有cursorDiskKV表
        workspace_cursor.execute("""
            CREATE TABLE IF NOT EXISTS cursorDiskKV (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        
        copied_count = 0
        updated_count = 0
        
        for key, value in all_chat_records:
            if value is None:
                continue
            
            # 检查工作区是否已存在
            workspace_cursor.execute("SELECT value FROM cursorDiskKV WHERE key = ?", (key,))
            exists = workspace_cursor.fetchone()
            
            if exists:
                # 如果存在，比较大小，保留更大的
                if len(value) > len(exists[0]):
                    workspace_cursor.execute("UPDATE cursorDiskKV SET value = ? WHERE key = ?", (value, key))
                    updated_count += 1
                # 否则跳过
            else:
                # 如果不存在，直接插入
                workspace_cursor.execute("INSERT INTO cursorDiskKV (key, value) VALUES (?, ?)", (key, value))
                copied_count += 1
        
        workspace_conn.commit()
        print(f"   ✅ 复制了 {copied_count} 条新记录")
        print(f"   ✅ 更新了 {updated_count} 条记录")
        
        # 3. 将全局的composer.composerData复制到工作区
        print()
        print("🔄 复制composer.composerData到工作区...")
        
        # 检查工作区是否已有composer.composerData
        workspace_cursor.execute("SELECT value FROM ItemTable WHERE key = 'composer.composerData'")
        workspace_result = workspace_cursor.fetchone()
        
        if workspace_result and workspace_result[0]:
            # 如果存在，合并
            workspace_data = json.loads(workspace_result[0])
            workspace_composers = {c.get('composerId'): c for c in workspace_data.get('allComposers', [])}
            global_composers_dict = {c.get('composerId'): c for c in global_composers}
            
            # 合并：工作区的优先，但添加全局中缺失的
            merged_composers = {**workspace_composers, **global_composers_dict}
            merged_composers_list = list(merged_composers.values())
            merged_composers_list.sort(key=lambda x: x.get('lastUpdatedAt', 0), reverse=True)
            
            merged_data = {
                'allComposers': merged_composers_list,
                'selectedComposerIds': list(set(workspace_data.get('selectedComposerIds', []) + global_composer_data.get('selectedComposerIds', []))),
                'lastFocusedComposerIds': list(set(workspace_data.get('lastFocusedComposerIds', []) + global_composer_data.get('lastFocusedComposerIds', []))),
                'hasMigratedComposerData': True,
                'hasMigratedMultipleComposers': True
            }
            
            workspace_cursor.execute("UPDATE ItemTable SET value = ? WHERE key = 'composer.composerData'", 
                                   (json.dumps(merged_data, ensure_ascii=False),))
            print(f"   ✅ 合并了 {len(merged_composers_list)} 个composers")
        else:
            # 如果不存在，直接复制全局的
            workspace_cursor.execute("INSERT INTO ItemTable (key, value) VALUES ('composer.composerData', ?)", 
                                   (global_result[0],))
            print(f"   ✅ 复制了 {len(global_composers)} 个composers")
        
        workspace_conn.commit()
        
        # 4. 验证
        print()
        print("🔍 验证工作区数据...")
        workspace_cursor.execute("SELECT value FROM ItemTable WHERE key = 'composer.composerData'")
        workspace_final = workspace_cursor.fetchone()
        
        if workspace_final:
            final_data = json.loads(workspace_final[0])
            final_composers = final_data.get('allComposers', [])
            beat_sync_found = any('1a38076e' in c.get('composerId', '') for c in final_composers)
            
            workspace_cursor.execute("SELECT COUNT(*) FROM cursorDiskKV WHERE key LIKE 'composerData:%'")
            chat_count = workspace_cursor.fetchone()[0]
            
            print(f"   工作区composers: {len(final_composers)}")
            print(f"   工作区对话记录: {chat_count}")
            print(f"   BeatSync (2573条) 存在: {'✅ 是' if beat_sync_found else '❌ 否'}")
        
        global_conn.close()
        workspace_conn.close()
        
        print()
        print("=" * 60)
        print("✅ 复制完成！")
        print("=" * 60)
        print()
        print("📋 下一步操作:")
        print("   1. 完全退出Cursor应用（Command+Q）")
        print("   2. 重新打开Cursor")
        print("   3. 打开项目文件夹: /Users/scarlett/Projects/BeatSync")
        print("   4. 检查聊天记录界面，应该能看到所有记录")
        print()
        
    except Exception as e:
        print(f"❌ 复制失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()








