#!/usr/bin/env python3
"""API 测试脚本

用于快速测试各项 API 功能
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
USER_ID = "test_user"


def test_health():
    """测试健康检查"""
    print("\n=== 测试健康检查 ===")
    resp = requests.get(f"{BASE_URL}/health")
    print(f"状态：{resp.json()}")


def test_create_schedule():
    """测试创建日程"""
    print("\n=== 测试创建日程 ===")
    
    data = {
        "event_name": "Python 期末考试",
        "start_time": "2024-06-20 14:00",
        "end_time": "2024-06-20 16:00",
        "location": "计算机楼 301",
        "priority": "high",
        "description": "闭卷考试，可带一张 A4 纸"
    }
    
    resp = requests.post(
        f"{BASE_URL}/api/v1/schedule/create?user_id={USER_ID}",
        json=data
    )
    
    if resp.status_code == 200:
        result = resp.json()
        print(f"✅ 创建成功：{result['event_name']}")
        print(f"   ID: {result['id']}")
        print(f"   时间：{result['start_time']}")
        return result['id']
    else:
        print(f"❌ 创建失败：{resp.text}")
        return None


def test_parse_text():
    """测试文本解析"""
    print("\n=== 测试文本解析 ===")
    
    test_cases = [
        "明天下午 3 点在教学楼 A302 开班会",
        "下周一上午 9 点计算机实验课",
        "6 月 15 日晚上 7 点社团迎新晚会，学生活动中心"
    ]
    
    for text in test_cases:
        print(f"\n解析：{text}")
        resp = requests.post(
            f"{BASE_URL}/api/v1/parse/text?user_id={USER_ID}",
            json={"content": text}
        )
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"  事件：{result['event_name']}")
            print(f"  时间：{result['start_time']}")
            print(f"  地点：{result['location']}")
            print(f"  优先级：{result['priority']}")
            print(f"  置信度：{result['confidence']:.2f}")
        else:
            print(f"  ❌ 解析失败：{resp.text}")


def test_list_schedules():
    """测试获取日程列表"""
    print("\n=== 测试获取日程列表 ===")
    
    resp = requests.get(f"{BASE_URL}/api/v1/schedule/list?user_id={USER_ID}")
    
    if resp.status_code == 200:
        schedules = resp.json()
        print(f"共 {len(schedules)} 个日程：")
        for s in schedules:
            print(f"  - {s['event_name']} ({s['start_time']})")
    else:
        print(f"❌ 获取失败：{resp.text}")


def test_qa():
    """测试智能问答"""
    print("\n=== 测试智能问答 ===")
    
    questions = [
        "图书馆开放时间",
        "教务处联系方式"
    ]
    
    for question in questions:
        print(f"\n问：{question}")
        resp = requests.post(
            f"{BASE_URL}/api/v1/qa/ask?user_id={USER_ID}&question={question}"
        )
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"答：{result['answer']}")
            print(f"置信度：{result['confidence']:.2f}")
        else:
            print(f"❌ 问答失败：{resp.text}")


def test_stats():
    """测试统计信息"""
    print("\n=== 测试统计信息 ===")
    
    resp = requests.get(f"{BASE_URL}/api/v1/schedule/stats?user_id={USER_ID}")
    
    if resp.status_code == 200:
        stats = resp.json()
        print(f"总日程数：{stats['total']}")
        print(f"待处理：{stats['pending']}")
        print(f"已完成：{stats['completed']}")
        print(f"高优先级：{stats['high_priority']}")
        print(f"本周：{stats['this_week']}")


def main():
    """运行所有测试"""
    print("=" * 50)
    print("校园 AI 秘书 API 测试")
    print("=" * 50)
    
    try:
        # 1. 健康检查
        test_health()
        
        # 2. 文本解析测试
        test_parse_text()
        
        # 3. 创建日程
        schedule_id = test_create_schedule()
        
        # 4. 获取日程列表
        test_list_schedules()
        
        # 5. 智能问答
        test_qa()
        
        # 6. 统计信息
        test_stats()
        
        print("\n" + "=" * 50)
        print("✅ 所有测试完成!")
        print("=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到服务，请确保服务已启动")
        print(f"   服务地址：{BASE_URL}")
        print("   启动命令：python -m app.main")
    except Exception as e:
        print(f"\n❌ 测试出错：{e}")


if __name__ == "__main__":
    main()
