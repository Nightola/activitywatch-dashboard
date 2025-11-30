document.addEventListener('DOMContentLoaded', function() {
    console.log("🔍 开始加载数据...");
    
    fetch('activitywatch_data.json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP错误! 状态: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log("✅ 数据加载成功");
            processData(data);
        })
        .catch(error => {
            console.error('❌ 加载数据失败:', error);
            document.getElementById('app-list').innerHTML = 
                '<p style="color: red;">无法加载数据文件</p>';
        });
});

function processData(rawData) {
    console.log("🔍 处理数据...");
    
    let activities = [];
    
    // 检查数据格式并提取活动
    if (rawData.buckets && typeof rawData.buckets === 'object') {
        Object.values(rawData.buckets).forEach(bucket => {
            if (bucket.events && Array.isArray(bucket.events)) {
                bucket.events.forEach(event => {
                    if (event.data) {
                        activities.push({
                            app: event.data.app || '未知应用',
                            title: event.data.title || '未知窗口',
                            duration: event.duration || 0,
                            timestamp: event.timestamp
                        });
                    }
                });
            }
        });
    }
    
    console.log(`📊 成功提取 ${activities.length} 个活动`);
    
    if (activities.length === 0) {
        document.getElementById('app-list').innerHTML = 
            '<p>没有找到活动数据</p>';
        return;
    }
    
    // 更新最后更新时间
    if (rawData.export_info && rawData.export_info.export_time) {
        const updateTime = new Date(rawData.export_info.export_time);
        document.getElementById('last-update').textContent = 
            updateTime.toLocaleString('zh-CN');
    }
    
    const totalTime = activities.reduce((sum, activity) => sum + activity.duration, 0) / 3600;
    
    // 按应用分组
    const appUsage = {};
    activities.forEach(activity => {
        const app = activity.app;
        if (!appUsage[app]) {
            appUsage[app] = 0;
        }
        appUsage[app] += activity.duration;
    });
    
    // 转换为数组并排序
    const appUsageArray = Object.keys(appUsage).map(app => ({
        app: app,
        duration: appUsage[app] / 3600
    })).sort((a, b) => b.duration - a.duration);
    
    updateStats(appUsageArray, totalTime, activities);
    createCharts(appUsageArray, activities);
    displayAppList(appUsageArray);
}

function updateStats(appUsageArray, totalTime, activities) {
    document.getElementById('total-time').textContent = totalTime.toFixed(2);
    
    if (appUsageArray.length > 0) {
        document.getElementById('top-app').textContent = appUsageArray[0].app;
        document.getElementById('top-app-time').textContent = appUsageArray[0].duration.toFixed(2) + ' 小时';
    }
    
    const uniqueApps = new Set(activities.map(a => a.app));
    document.getElementById('window-count').textContent = uniqueApps.size;
    
    // 显示数据时间范围
    if (activities.length > 0) {
        const firstDate = new Date(activities[0].timestamp);
        const lastDate = new Date(activities[activities.length - 1].timestamp);
        document.getElementById('data-range').textContent = 
            `${firstDate.toLocaleDateString('zh-CN')}`;
    }
}

function createCharts(appUsageArray, activities) {
    // 应用使用时间饼图
    const timeCtx = document.getElementById('timeChart').getContext('2d');
    const topApps = appUsageArray.slice(0, 8);
    
    new Chart(timeCtx, {
        type: 'pie',
        data: {
            labels: topApps.map(app => app.app),
            datasets: [{
                data: topApps.map(app => app.duration),
                backgroundColor: [
                    '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
                    '#9966FF', '#FF9F40', '#FF6384', '#C9CBCF'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
    
    // 使用时间趋势图
    const trendCtx = document.getElementById('trendChart').getContext('2d');
    
    const hourlyUsage = {};
    activities.forEach(activity => {
        const hour = new Date(activity.timestamp).getHours();
        if (!hourlyUsage[hour]) {
            hourlyUsage[hour] = 0;
        }
        hourlyUsage[hour] += activity.duration / 3600;
    });
    
    const hours = Array.from({length: 24}, (_, i) => i);
    const hourlyData = hours.map(hour => hourlyUsage[hour] || 0);
    
    new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: hours.map(h => `${h}:00`),
            datasets: [{
                label: '使用时间 (小时)',
                data: hourlyData,
                borderColor: '#36A2EB',
                backgroundColor: 'rgba(54, 162, 235, 0.1)',
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
    
    // 生产力分析图
    const productivityCtx = document.getElementById('productivityChart').getContext('2d');
    
    const categories = {
        '生产力': ['Code', 'Visual Studio Code', 'Sublime Text', 'IntelliJ IDEA', 'Terminal', '命令行'],
        '沟通': ['Slack', 'Discord', '微信', 'QQ', 'Telegram', 'Microsoft Teams'],
        '浏览器': ['Chrome', 'Firefox', 'Safari', 'Edge'],
        '娱乐': ['Steam', 'Spotify', 'Netflix', 'YouTube', '游戏'],
        '其他': []
    };
    
    const categoryUsage = {};
    Object.keys(categories).forEach(category => {
        categoryUsage[category] = 0;
    });
    
    appUsageArray.forEach(appData => {
        let categorized = false;
        for (const [category, apps] of Object.entries(categories)) {
            if (apps.some(appName => appData.app.includes(appName))) {
                categoryUsage[category] += appData.duration;
                categorized = true;
                break;
            }
        }
        if (!categorized) {
            categoryUsage['其他'] += appData.duration;
        }
    });
    
    new Chart(productivityCtx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(categoryUsage),
            datasets: [{
                data: Object.values(categoryUsage),
                backgroundColor: [
                    '#4BC0C0', '#FF6384', '#FFCE56', '#36A2EB', '#9966FF'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function displayAppList(appUsageArray) {
    const appList = document.getElementById('app-list');
    appList.innerHTML = '';
    
    appUsageArray.forEach((appData, index) => {
        const appItem = document.createElement('div');
        appItem.className = 'app-item';
        appItem.innerHTML = `
            <div>
                <strong>${index + 1}. ${appData.app}</strong>
            </div>
            <div>${appData.duration.toFixed(2)} 小时</div>
        `;
        appList.appendChild(appItem);
    });
}