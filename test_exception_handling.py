#!/usr/bin/env python3
"""
异常处理测试用例
测试各种异常场景，验证异常处理机制是否正常工作
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

def create_test_scenarios():
    """创建测试场景"""
    test_dir = Path("test_exception_scenarios")
    test_dir.mkdir(exist_ok=True)
    
    scenarios = {}
    
    # 场景1: 文件不存在
    scenarios['file_not_found'] = {
        'dance': 'test_exception_scenarios/nonexistent_dance.mp4',
        'bgm': 'test_exception_scenarios/nonexistent_bgm.mp4',
        'output': 'test_exception_scenarios/output.mp4',
        'expected_error': '文件不存在'
    }
    
    # 场景2: 无权限目录（创建只读目录）
    read_only_dir = test_dir / 'read_only_output'
    read_only_dir.mkdir(exist_ok=True)
    # 设置目录为只读（macOS/Linux）
    try:
        os.chmod(read_only_dir, 0o555)  # 只读权限
        scenarios['permission_denied'] = {
            'dance': 'test_multiple_videoformats/echo/dance.mp4',  # 使用真实文件
            'bgm': 'test_multiple_videoformats/echo/bgm.mp4',
            'output': str(read_only_dir / 'output.mp4'),
            'expected_error': '权限不足',
            'cleanup': lambda: os.chmod(read_only_dir, 0o755)  # 恢复权限以便清理
        }
    except Exception as e:
        print(f"  警告: 无法创建只读目录测试场景: {e}")
    
    # 场景3: 损坏的视频文件（创建一个无效的MP4文件）
    corrupted_file = test_dir / 'corrupted.mp4'
    with open(corrupted_file, 'w') as f:
        f.write("这不是一个有效的视频文件")
    scenarios['corrupted_file'] = {
        'dance': str(corrupted_file),
        'bgm': 'test_multiple_videoformats/echo/bgm.mp4',
        'output': 'test_exception_scenarios/output.mp4',
        'expected_error': '格式无效'
    }
    
    # 场景4: 无音频轨道的视频（需要实际创建，这里用占位符）
    scenarios['no_audio_track'] = {
        'dance': 'test_multiple_videoformats/echo/dance.mp4',  # 占位符，实际测试需要真实无音频视频
        'bgm': 'test_multiple_videoformats/echo/bgm.mp4',
        'output': 'test_exception_scenarios/output.mp4',
        'expected_error': '没有音频轨道',
        'skip': True  # 跳过，因为需要特殊视频文件
    }
    
    # 场景5: 输出目录不存在（但可以创建）
    scenarios['output_dir_not_exist'] = {
        'dance': 'test_multiple_videoformats/echo/dance.mp4',
        'bgm': 'test_multiple_videoformats/echo/bgm.mp4',
        'output': 'test_exception_scenarios/new_dir/output.mp4',
        'expected_error': None,  # 应该成功创建目录
        'should_succeed': True
    }
    
    return scenarios

def run_test_scenario(name: str, scenario: dict) -> dict:
    """运行单个测试场景"""
    print(f"\n{'='*60}")
    print(f"测试场景: {name}")
    print(f"{'='*60}")
    print(f"  dance: {scenario['dance']}")
    print(f"  bgm: {scenario['bgm']}")
    print(f"  output: {scenario['output']}")
    
    # 检查是否需要跳过
    if scenario.get('skip', False):
        print(f"  ⏭️  跳过（需要特殊测试文件）")
        return {'name': name, 'skipped': True}
    
    # 运行测试
    cmd = [
        'python3', '-u', 'beatsync_fine_cut_modular.py',
        '--dance', scenario['dance'],
        '--bgm', scenario['bgm'],
        '--output', scenario['output']
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        # 检查结果
        output_text = result.stdout + result.stderr
        expected_error = scenario.get('expected_error')
        should_succeed = scenario.get('should_succeed', False)
        
        if should_succeed:
            # 应该成功
            if result.returncode == 0:
                print(f"  ✅ 成功（符合预期）")
                return {'name': name, 'success': True, 'expected': 'success', 'actual': 'success'}
            else:
                print(f"  ❌ 失败（应该成功）")
                print(f"  错误输出: {result.stderr[:300]}")
                return {'name': name, 'success': False, 'expected': 'success', 'actual': 'failure'}
        else:
            # 应该失败
            if result.returncode != 0:
                # 检查是否包含预期的错误信息
                if expected_error and expected_error.lower() in output_text.lower():
                    print(f"  ✅ 正确捕获异常: {expected_error}")
                    return {'name': name, 'success': True, 'expected': 'failure', 'actual': 'failure', 'error_match': True}
                else:
                    print(f"  ⚠️  失败但错误信息不匹配预期")
                    print(f"  预期: {expected_error}")
                    print(f"  实际输出: {output_text[:300]}")
                    return {'name': name, 'success': False, 'expected': 'failure', 'actual': 'failure', 'error_match': False}
            else:
                print(f"  ❌ 应该失败但成功了")
                return {'name': name, 'success': False, 'expected': 'failure', 'actual': 'success'}
                
    except subprocess.TimeoutExpired:
        print(f"  ⏱️  超时")
        return {'name': name, 'success': False, 'timeout': True}
    except Exception as e:
        print(f"  ❌ 测试执行异常: {e}")
        return {'name': name, 'success': False, 'exception': str(e)}
    finally:
        # 清理
        if 'cleanup' in scenario:
            try:
                scenario['cleanup']()
            except:
                pass

def main():
    print("=" * 60)
    print("异常处理测试")
    print("=" * 60)
    
    # 创建测试场景
    scenarios = create_test_scenarios()
    
    print(f"\n找到 {len(scenarios)} 个测试场景")
    print("-" * 60)
    
    results = []
    for name, scenario in scenarios.items():
        result = run_test_scenario(name, scenario)
        results.append(result)
    
    # 生成报告
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    total = len([r for r in results if not r.get('skipped', False)])
    passed = len([r for r in results if r.get('success', False)])
    failed = total - passed
    skipped = len([r for r in results if r.get('skipped', False)])
    
    print(f"\n总测试场景: {len(results)}")
    print(f"  通过: {passed}")
    print(f"  失败: {failed}")
    print(f"  跳过: {skipped}")
    print(f"  成功率: {passed/total*100:.1f}%" if total > 0 else "  成功率: N/A")
    
    print("\n详细结果:")
    for result in results:
        name = result['name']
        if result.get('skipped'):
            print(f"  {name}: ⏭️  跳过")
        elif result.get('success'):
            print(f"  {name}: ✅ 通过")
        else:
            print(f"  {name}: ❌ 失败")
            if 'timeout' in result:
                print(f"    - 超时")
            if 'exception' in result:
                print(f"    - 异常: {result['exception']}")
            if 'error_match' in result and not result['error_match']:
                print(f"    - 错误信息不匹配预期")
    
    # 清理测试输出文件
    test_dir = Path("test_exception_scenarios")
    if test_dir.exists():
        for file in test_dir.glob("output*.mp4"):
            try:
                file.unlink()
            except:
                pass
        # 清理新创建的目录
        new_dir = test_dir / 'new_dir'
        if new_dir.exists():
            try:
                shutil.rmtree(new_dir)
            except:
                pass
    
    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())

