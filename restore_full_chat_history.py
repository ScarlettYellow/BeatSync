#!/usr/bin/env python3
"""
完整恢复Cursor聊天记录
包括composer元数据和实际的对话内容（存储在cursorDiskKV表中）
"""

import sqlite3
import json
import os
import sys
from datetime import datetime

global_storage_dir = os.path.expanduser("~/Library/Application Support/Cursor/User/globalStorage")
old_global_db = os.path.join(global_storage_dir, "state.vscdb.current_backup")
new_global_db = os.path.join(global_storage_dir, "state.vscdb")

def main():
    print("=" * 60)
    print("Cursor 完整聊天记录恢复工具")
    print("=" * 60)
    print()
    
    # 检查文件
    if not os.path.exists(old_global_db):
        print(f"❌ 错误: 找不到备份文件 {old_global_db}")
        sys.exit(1)
    
    if not os.path.exists(new_global_db):
        print(f"❌ 错误: 找不到当前数据库 {new_global_db}")
        sys.exit(1)
    
    # 备份当前数据库
    backup_path = new_global_db + f".backup_before_full_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"📦 备份当前全局数据库...")
    import shutil
    shutil.copy2(new_global_db, backup_path)
    print(f"✅ 已备份到: {os.path.basename(backup_path)}")
    print()
    
    try:
        # 连接数据库
        old_conn = sqlite3.connect(old_global_db)
        new_conn = sqlite3.connect(new_global_db)
        
        old_cursor = old_conn.cursor()
        new_cursor = new_conn.cursor()
        
        # 1. 恢复composer元数据（ItemTable中的composer.composerData）
        print("🔄 步骤1: 恢复composer元数据...")
        old_cursor.execute("SELECT value FROM ItemTable WHERE key = 'composer.composerData'")
        old_composer_data = old_cursor.fetchone()
        
        if old_composer_data:
            old_data_str = old_composer_data[0]
            new_cursor.execute("SELECT value FROM ItemTable WHERE key = 'composer.composerData'")
            new_result = new_cursor.fetchone()
            
            if new_result:
                # 智能合并
                old_data = json.loads(old_data_str)
                new_data = json.loads(new_result[0])
                
                old_composers = {c.get('composerId'): c for c in old_data.get('allComposers', [])}
                new_composers = {c.get('composerId'): c for c in new_data.get('allComposers', [])}
                
                # 合并
                merged_composers = {**new_composers, **old_composers}
                
                merged_data = {
                    'allComposers': list(merged_composers.values()),
                    'selectedComposerIds': list(set(old_data.get('selectedComposerIds', []) + new_data.get('selectedComposerIds', []))),
                    'lastFocusedComposerIds': list(set(old_data.get('lastFocusedComposerIds', []) + new_data.get('lastFocusedComposerIds', []))),
                    'hasMigratedComposerData': new_data.get('hasMigratedComposerData', False),
                    'hasMigratedMultipleComposers': True
                }
                
                new_cursor.execute("UPDATE ItemTable SET value = ? WHERE key = 'composer.composerData'", 
                                 (json.dumps(merged_data, ensure_ascii=False),))
                print(f"  ✅ 合并了 {len(merged_composers)} 个composer元数据")
            else:
                new_cursor.execute("INSERT INTO ItemTable (key, value) VALUES ('composer.composerData', ?)", 
                                 (old_data_str,))
                print(f"  ✅ 插入了composer元数据")
        
        # 2. 恢复实际的对话内容（cursorDiskKV表中的composerData:*）
        print()
        print("🔄 步骤2: 恢复对话内容（cursorDiskKV表）...")
        
        # 获取所有composerData记录
        old_cursor.execute("SELECT key, value FROM cursorDiskKV WHERE key LIKE 'composerData:%'")
        old_chat_records = old_cursor.fetchall()
        
        print(f"  📊 备份中找到 {len(old_chat_records)} 条对话记录")
        
        # 检查新数据库中有多少
        new_cursor.execute("SELECT COUNT(*) FROM cursorDiskKV WHERE key LIKE 'composerData:%'")
        new_count = new_cursor.fetchone()[0]
        print(f"  📊 当前数据库中有 {new_count} 条对话记录")
        
        restored_count = 0
        updated_count = 0
        skipped_count = 0
        
        for key, value in old_chat_records:
            # 跳过None值
            if value is None:
                continue
                
            # 检查新数据库中是否已存在
            new_cursor.execute("SELECT value FROM cursorDiskKV WHERE key = ?", (key,))
            new_result = new_cursor.fetchone()
            
            if new_result and new_result[0] and new_result[0] is not None:
                # 如果存在，比较大小，保留更大的（通常包含更多对话）
                new_value = new_result[0]
                if len(value) > len(new_value):
                    new_cursor.execute("UPDATE cursorDiskKV SET value = ? WHERE key = ?", (value, key))
                    updated_count += 1
                    print(f"  ✅ 更新: {key[:50]}... (大小: {len(value)} > {len(new_value)})")
                else:
                    skipped_count += 1
            else:
                # 如果不存在，直接插入
                new_cursor.execute("INSERT INTO cursorDiskKV (key, value) VALUES (?, ?)", (key, value))
                restored_count += 1
                # 显示前几个字符以便识别
                try:
                    if isinstance(value, (str, bytes)):
                        data = json.loads(value)
                        composer_id = data.get('composerId', '')[:8]
                        print(f"  ✅ 恢复: {key[:50]}... (ID: {composer_id}..., 大小: {len(value)} bytes)")
                    else:
                        print(f"  ✅ 恢复: {key[:50]}... (大小: {len(str(value))} bytes)")
                except:
                    print(f"  ✅ 恢复: {key[:50]}... (大小: {len(str(value))} bytes)")
        
        new_conn.commit()
        
        print()
        print("=" * 60)
        print("✅ 完整恢复完成！")
        print("=" * 60)
        print()
        print(f"📊 恢复统计:")
        print(f"   新恢复对话记录: {restored_count}")
        print(f"   更新对话记录: {updated_count}")
        print(f"   跳过记录: {skipped_count}")
        print(f"   总计处理: {len(old_chat_records)}")
        print()
        
        # 显示所有composer的统计
        new_cursor.execute("SELECT key, LENGTH(value) as size FROM cursorDiskKV WHERE key LIKE 'composerData:%' ORDER BY size DESC")
        all_composers = new_cursor.fetchall()
        
        print(f"📝 所有对话记录列表 (共 {len(all_composers)} 条):")
        for i, (key, size) in enumerate(all_composers, 1):
            composer_id = key.replace('composerData:', '')[:8]
            if size is not None:
                size_kb = size / 1024
                print(f"   {i}. {key[:60]}... (大小: {size_kb:.1f}KB, ID: {composer_id}...)")
            else:
                print(f"   {i}. {key[:60]}... (大小: 未知, ID: {composer_id}...)")
        
        old_conn.close()
        new_conn.close()
        
        print()
        print("📋 下一步操作:")
        print("   1. 完全退出Cursor应用（Command+Q）")
        print("   2. 重新打开Cursor")
        print("   3. 打开项目文件夹: /Users/scarlett/Projects/BeatSync")
        print("   4. 检查所有聊天记录是否正常加载")
        print()
        
    except Exception as e:
        print(f"❌ 恢复失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

