# ActivityWatch数据获取脚本 - 修复文件位置问题
import requests
import json
from datetime import datetime, timedelta
import os
import sys

print("🎯 ActivityWatch Data Export Tool - Fixed Path Version")
print("=" * 55)

def get_activitywatch_data():
    try:
        # 0. 确定输出路径（关键修复）
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        output_file = os.path.join(desktop_path, "activitywatch_data.json")
        
        print(f"📁 输出路径: {output_file}")
        
        # 1. 检查ActivityWatch连接
        print("1. 检查ActivityWatch连接...")
        base_url = "http://localhost:5600/api/0"
        
        try:
            response = requests.get(f"{base_url}/buckets", timeout=10)
            if response.status_code != 200:
                print("❌ ActivityWatch未运行或无法访问")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到ActivityWatch")
            return False
        
        print("✅ 成功连接到ActivityWatch")
        
        # 2. 获取存储桶信息
        print("\n2. 获取存储桶信息...")
        buckets = response.json()
        
        # 查找窗口活动存储桶
        window_bucket = None
        for bucket_id in buckets:
            if 'aw-watcher-window' in bucket_id:
                window_bucket = bucket_id
                break
        
        if not window_bucket:
            print("❌ 未找到窗口活动数据存储桶")
            return False
        
        print(f"✅ 使用存储桶: {window_bucket}")
        
        # 3. 设置时间范围（最近12小时）
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=12)
        
        print(f"📅 时间范围: {start_time.strftime('%Y-%m-%d %H:%M')} 到 {end_time.strftime('%Y-%m-%d %H:%M')}")
        
        # 4. 获取事件数据
        print("\n3. 获取事件数据...")
        events_url = f"{base_url}/buckets/{window_bucket}/events"
        params = {
            'start': start_time.isoformat(),
            'end': end_time.isoformat(),
            'limit': 1000
        }
        
        events_response = requests.get(events_url, params=params)
        if events_response.status_code != 200:
            print(f"❌ 获取事件数据失败: {events_response.status_code}")
            return False
        
        events_data = events_response.json()
        print(f"✅ 获取到 {len(events_data)} 个事件")
        
        if len(events_data) == 0:
            print("⚠️  指定时间范围内未找到事件")
        
        # 5. 处理并保存数据
        print("\n4. 处理并保存数据...")
        
        # 创建完整的数据结构
        output_data = {
            "buckets": {
                window_bucket: {
                    "id": window_bucket,
                    "type": "window",
                    "events": events_data
                }
            },
            "export_info": {
                "export_time": datetime.now().isoformat(),
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "total_events": len(events_data)
            }
        }
        
        # 保存到文件 - 使用绝对路径
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据已保存到: {output_file}")
        
        # 6. 显示统计信息
        if events_data:
            total_duration = sum(event.get('duration', 0) for event in events_data)
            unique_apps = set()
            
            for event in events_data:
                if 'data' in event and 'app' in event['data']:
                    unique_apps.add(event['data']['app'])
            
            print(f"\n📊 数据摘要:")
            print(f"   • 总追踪时间: {total_duration/3600:.2f} 小时")
            print(f"   • 唯一应用程序: {len(unique_apps)}")
            
            if unique_apps:
                print(f"   • 追踪的应用: {', '.join(list(unique_apps)[:5])}{'...' if len(unique_apps) > 5 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ 意外错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("开始ActivityWatch数据导出...")
    
    success = get_activitywatch_data()
    
    if success:
        print("\n🎉 数据导出成功完成!")
    else:
        print("\n❌ 导出失败。请检查上面的错误信息。")
    
    input("\n按回车键退出...")