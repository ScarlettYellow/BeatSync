#!/bin/bash
# 检查Python进程和内存使用情况

echo "=" * 60
echo "Python进程检查"
echo "=" * 60
echo ""

echo "所有Python进程:"
ps aux | grep python | grep -v grep | head -20

echo ""
echo "BeatSync相关进程:"
ps aux | grep -E "beatsync|BeatSync" | grep -v grep

echo ""
echo "按内存使用排序的Python进程（前10个）:"
ps aux | grep python | grep -v grep | sort -k4 -rn | head -10 | awk '{printf "PID: %-8s Memory: %8s (%.2f GB)  Command: %s\n", $2, $6, $6/1024/1024, $11" "$12" "$13" "$14" "$15}'

echo ""
echo "总内存使用统计:"
TOTAL_MEM=$(ps aux | grep python | grep -v grep | awk '{sum+=$6} END {print sum/1024/1024}')
echo "所有Python进程总内存: ${TOTAL_MEM} GB"



