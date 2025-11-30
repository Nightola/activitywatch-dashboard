# ActivityWatch数据获取脚本 - 修复数据格式版
import requests
import json
from datetime import datetime, timedelta
import os

print("🎯 ActivityWatch数据获取工具 - 修复版")
print("=" * 50)

def get_activitywatch_data():
    try:
        # 1. 连接到ActivityWatch
        print("1. 正在连接到ActivityWatch...")
        base_url = "http://localhost:5600/api/0"
        
        response = requests.get(f"{base_url}/buckets")
        if response.status_code != 200:
            print("❌ 无法连接到ActivityWatch！")
            return None
        
        print("✅ 成功连接到ActivityWatch")
        
        # 2. 获取存储桶信息
        print("\n2. 正在获取数据...")
        buckets = response.json()
        
        # 3. 设置时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)  # 获取最近1天的数据
        
        start_str = start_time.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        end_str = end_time.isoformat()
        
        print(f"   时间范围: {start_time.strftime('%Y-%m-%d %H:%M')} 到 {end_time.strftime('%Y-%m-%d %H:%M')}")
        
        # 4. 获取所有事件数据
        all_events = []
        
        for bucket_id in buckets:
            if any(keyword in bucket_id for keyword in ['window', 'afk', 'browser']):
                print(f"   处理存储桶: {bucket_id}")
                
                events_url = f"{base_url}/buckets/{bucket_id}/events"
                params = {
                    'start': start_str,
                    'end': end_str
                }
                
                events_response = requests.get(events_url, params=params)
                if events_response.status_code == 200:
                    events_data = events_response.json()
                    all_events.extend(events_data)
                    print(f"     获取到 {len(events_data)} 个事件")
        
        print(f"\n3. 总共获取到 {len(all_events)} 个事件")
        
        # 5. 转换为网站期望的格式
        print("4. 正在转换数据格式...")
        
        # 网站期望的格式：包含 buckets 的字典
        formatted_data = {
            "buckets": {},
            "export_info": {
                "export_time": datetime.now().isoformat(),
                "time_range": {"start": start_str, "end": end_str},
                "total_events": len(all_events)
            }
        }
        
        # 按存储桶分组事件
        for event in all_events:
            # 这里需要确定事件属于哪个存储桶
            # 由于API返回的事件不直接包含bucket信息，我们需要从URL推断
            # 简化处理：创建一个虚拟的存储桶结构
            bucket_key = "aw-watcher-window_unknown"
            
            if 'data' in event and 'app' in event['data']:
                app_name = event['data']['app']
                if 'chrome' in app_name.lower() or 'firefox' in app_name.lower():
                    bucket_key = "aw-watcher-browser_unknown"
                else:
                    bucket_key = "aw-watcher-window_unknown"
            
            if bucket_key not in formatted_data["buckets"]:
                formatted_data["buckets"][bucket_key] = {
                    "id": bucket_key,
                    "type": "unknown",
                    "events": []
                }
            
            formatted_data["buckets"][bucket_key]["events"].append(event)
        
        # 6. 保存数据
        print("5. 正在保存数据...")
        output_file = "activitywatch_data.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 数据已保存到: {output_file}")
        
        # 显示统计信息
        total_duration = sum(event.get('duration', 0) for event in all_events)
        unique_apps = set()
        
        for event in all_events:
            if 'data' in event and 'app' in event['data']:
                unique_apps.add(event['data']['app'])
        
        print(f"\n📊 数据统计:")
        print(f"   总使用时间: {total_duration/3600:.2f} 小时")
        print(f"   唯一应用数: {len(unique_apps)}")
        print(f"   事件总数: {len(all_events)}")
        
        return formatted_data
        
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")
        return None

def check_activitywatch_running():
    print("🔍 检查ActivityWatch状态...")
    try:
        response = requests.get("http://localhost:5600", timeout=5)
        if response.status_code == 200:
            print("✅ ActivityWatch正在运行")
            return True
        else:
            print("❌ ActivityWatch未正常运行")
            return False
    except:
        print("❌ 无法连接到ActivityWatch")
        return False

# 主程序
if __name__ == "__main__":
    if not check_activitywatch_running():
        print("\n💡 请先启动ActivityWatch，然后重新运行此脚本")
        input("按回车键退出...")
        exit()
    
    data = get_activitywatch_data()
    
    if data:
        print("\n🎉 数据获取成功！格式已调整为网站兼容格式")
        print("\n接下来:")
        print("1. 将 activitywatch_data.json 复制到网站文件夹")
        print("2. 替换原有的数据文件")
        print("3. 刷新你的网站查看效果")
    else:
        print("\n😞 数据获取失败")
    
    input("\n按回车键退出...")