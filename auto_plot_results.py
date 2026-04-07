import json
import glob
import os
import sys
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def load_all_metrics(results_dir):
    # Загрузка всех метрик из директории
    all_metrics = []
    
    metrics_files = glob.glob(f"{results_dir}/metrics.json")
    
    for file_path in metrics_files:
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        all_metrics.append(data)
                    except json.JSONDecodeError:
                        pass
                        
            if all_metrics:
                print(f"Loaded {len(all_metrics)} metrics from: {os.path.basename(file_path)}")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return all_metrics

def extract_experiment_data(metrics_list):
    # Извлечение данных для построения графиков
    experiments = []
    durations = []
    optimizations = []
    partitions = []
    load_times = []
    query_times = []
    
    # RAM метрики
    peak_memory = []
    start_memory = []
    memory_increase = []
    system_memory_percent = []
    
    for m in metrics_list:
        experiments.append(m.get('experiment', 'Unknown'))
        durations.append(m.get('duration_seconds', 0))
        optimizations.append(m.get('optimization', False))
        partitions.append(m.get('partitions', 20))
        load_times.append(m.get('load_time_seconds', 0))
        query_times.append(m.get('query_time_seconds', 0))
        
        # Извлечение RAM метрик
        mem = m.get('memory', {})
        peak_memory.append(mem.get('peak_mb', 0))
        start_memory.append(mem.get('start_mb', 0))
        memory_increase.append(mem.get('memory_increase_mb', 0))
        system_memory_percent.append(mem.get('system_used_percent', 0))
    
    return {
        'experiments': experiments,
        'durations': durations,
        'optimizations': optimizations,
        'partitions': partitions,
        'load_times': load_times,
        'query_times': query_times,
        'peak_memory': peak_memory,
        'start_memory': start_memory,
        'memory_increase': memory_increase,
        'system_memory_percent': system_memory_percent
    }

def create_comparison_plots(data, results_dir):
    # Создание всех графиков
    
    if not data['experiments']:
        print("Нет данных для построения графиков!")
        return
    
    plt.style.use('seaborn-v0_8-darkgrid')
    colors_base = '#FF6B6B'
    colors_opt = '#4ECDC4'
    
    # 1. Время выполнения
    fig1, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(data['experiments']))
    colors = [colors_opt if opt else colors_base for opt in data['optimizations']]
    bars = ax.bar(x, data['durations'], color=colors, edgecolor='black', linewidth=1.5)
    
    ax.set_xticks(x)
    ax.set_xticklabels(data['experiments'], rotation=45, ha='right')
    ax.set_ylabel('Время выполнения (секунды)', fontsize=12, fontweight='bold')
    ax.set_title('Сравнение времени выполнения экспериментов', fontsize=14, fontweight='bold')
    
    for bar, duration in zip(bars, data['durations']):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.2,
                f'{duration:.2f}s', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{results_dir}/execution_time.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {results_dir}/execution_time.png")
    plt.close(fig1)
    
    # 2. Сравнение 1DN vs 3DN по времени
    if len(data['durations']) >= 4:
        fig2, ax = plt.subplots(figsize=(10, 6))
        
        dn1_base = data['durations'][0]
        dn1_opt = data['durations'][1]
        dn3_base = data['durations'][2]
        dn3_opt = data['durations'][3]
        
        x = np.arange(2)
        width = 0.35
        
        bars1 = ax.bar(x[0] - width/2, dn1_base, width, label='Базовая', color=colors_base, edgecolor='black')
        bars2 = ax.bar(x[0] + width/2, dn1_opt, width, label='Оптимизированная', color=colors_opt, edgecolor='black')
        bars3 = ax.bar(x[1] - width/2, dn3_base, width, color=colors_base, edgecolor='black')
        bars4 = ax.bar(x[1] + width/2, dn3_opt, width, color=colors_opt, edgecolor='black')
        
        ax.set_xticks(x)
        ax.set_xticklabels(['1 DataNode', '3 DataNodes'], fontsize=12, fontweight='bold')
        ax.set_ylabel('Время выполнения (секунды)', fontsize=12, fontweight='bold')
        ax.set_title('Влияние количества DataNode на производительность', fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        
        for bar, val in zip([bars1[0], bars2[0], bars3[0], bars4[0]], 
                           [dn1_base, dn1_opt, dn3_base, dn3_opt]):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.2,
                    f'{val:.2f}s', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'{results_dir}/nodes_comparison.png', dpi=150, bbox_inches='tight')
        print(f"Saved: {results_dir}/nodes_comparison.png")
        plt.close(fig2)
    
    # 3. Использование RAM (столбчатая диаграмма)
    fig3, ax = plt.subplots(figsize=(12, 6))
    
    x = np.arange(len(data['experiments']))
    colors = [colors_opt if opt else colors_base for opt in data['optimizations']]
    bars = ax.bar(x, data['peak_memory'], color=colors, edgecolor='black', linewidth=1.5)
    
    ax.set_xticks(x)
    ax.set_xticklabels(data['experiments'], rotation=45, ha='right')
    ax.set_ylabel('Пиковое использование RAM (MB)', fontsize=12, fontweight='bold')
    ax.set_title('Сравнение использования памяти', fontsize=14, fontweight='bold')
    
    for bar, memory in zip(bars, data['peak_memory']):
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 5,
                f'{memory:.0f} MB', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{results_dir}/memory_usage.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {results_dir}/memory_usage.png")
    plt.close(fig3)
    
    # 4. Время vs Память (сравнение эффективности)
    fig5, ax = plt.subplots(figsize=(10, 8))
    
    colors = [colors_opt if opt else colors_base for opt in data['optimizations']]
    markers = ['o' for _ in data['experiments']]
    
    for i, (exp, duration, memory, opt) in enumerate(zip(data['experiments'], 
                                                          data['durations'], 
                                                          data['peak_memory'],
                                                          data['optimizations'])):
        color = colors_opt if opt else colors_base
        size = 200 if opt else 100
        ax.scatter(duration, memory, s=size, c=color, alpha=0.7, edgecolors='black', linewidth=1.5)
        ax.annotate(exp, (duration, memory), xytext=(10, 10), textcoords='offset points', 
                   fontsize=9, fontweight='bold')
    
    ax.set_xlabel('Время выполнения (секунды)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Пиковое использование RAM (MB)', fontsize=12, fontweight='bold')
    ax.set_title('Компромисс: Время выполнения vs Использование памяти', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Добавление легенды
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=colors_base, label='Базовая конфигурация'),
                       Patch(facecolor=colors_opt, label='Оптимизированная конфигурация')]
    ax.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.savefig(f'{results_dir}/time_vs_memory.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {results_dir}/time_vs_memory.png")
    plt.close(fig5)
    
    # 5. Разбивка времени
    if any(data['load_times']) or any(data['query_times']):
        fig6, ax = plt.subplots(figsize=(12, 6))
        
        x = np.arange(len(data['experiments']))
        width = 0.35
        
        bars_load = ax.bar(x - width/2, data['load_times'], width, label='Загрузка данных', 
                          color='#FFB347', edgecolor='black')
        bars_query = ax.bar(x + width/2, data['query_times'], width, label='Выполнение запросов', 
                           color='#5D9B9B', edgecolor='black')
        
        ax.set_xticks(x)
        ax.set_xticklabels(data['experiments'], rotation=45, ha='right')
        ax.set_ylabel('Время (секунды)', fontsize=12, fontweight='bold')
        ax.set_title('Разбивка времени выполнения', fontsize=14, fontweight='bold')
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(f'{results_dir}/time_breakdown.png', dpi=150, bbox_inches='tight')
        print(f"Saved: {results_dir}/time_breakdown.png")
        plt.close(fig6)
    
    # 6. Ускорение от оптимизации
    if len(data['durations']) >= 4:
        fig7, ax = plt.subplots(figsize=(8, 6))
        
        dn1_base = data['durations'][0]
        dn1_opt = data['durations'][1]
        dn3_base = data['durations'][2]
        dn3_opt = data['durations'][3]
        
        speedup_1dn = dn1_base / dn1_opt if dn1_opt > 0 else 1
        speedup_3dn = dn3_base / dn3_opt if dn3_opt > 0 else 1
        
        metrics_names = ['1 DataNode', '3 DataNodes']
        speedups = [speedup_1dn, speedup_3dn]
        
        bars = ax.bar(metrics_names, speedups, color=[colors_opt, colors_opt], 
                     edgecolor='black', linewidth=1.5)
        ax.axhline(y=1, color='gray', linestyle='--', linewidth=2, label='Без изменений')
        
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.05,
                    f'{bar.get_height():.2f}x', ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        ax.set_ylabel('Ускорение (раз)', fontsize=12, fontweight='bold')
        ax.set_title('Ускорение от оптимизации', fontsize=14, fontweight='bold')
        ax.legend()
        ax.set_ylim(0, max(speedups) * 1.2)
        
        plt.tight_layout()
        plt.savefig(f'{results_dir}/speedup.png', dpi=150, bbox_inches='tight')
        print(f"Saved: {results_dir}/speedup.png")
        plt.close(fig7)
    
    # 7. Трендовый график
    fig8, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(data['experiments']))
    ax.plot(x, data['durations'], 'o-', color='#FF6B6B', linewidth=2, markersize=10, label='Время выполнения')
    ax.fill_between(x, data['durations'], alpha=0.3, color='#FF6B6B')
    
    ax.set_xticks(x)
    ax.set_xticklabels(data['experiments'], rotation=45, ha='right')
    ax.set_ylabel('Время выполнения (секунды)', fontsize=12, fontweight='bold')
    ax.set_title('Тренд производительности', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    for i, (xi, yi) in enumerate(zip(x, data['durations'])):
        ax.annotate(f'{yi:.2f}s', (xi, yi), xytext=(0, 10), textcoords='offset points',
                   ha='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(f'{results_dir}/trend.png', dpi=150, bbox_inches='tight')
    print(f"Saved: {results_dir}/trend.png")
    plt.close(fig8)

def create_summary_report(data, results_dir):
    # Создание HTML отчета с результатами
    
    if len(data['durations']) >= 4:
        speedup_1dn = data['durations'][0] / data['durations'][1] if data['durations'][1] > 0 else 1
        speedup_3dn = data['durations'][0] / data['durations'][2] if data['durations'][2] > 0 else 1
        best_time = min(data['durations'])
        best_exp = data['experiments'][data['durations'].index(best_time)]
        best_memory = min(data['peak_memory']) if data['peak_memory'] else 0
        best_memory_exp = data['experiments'][data['peak_memory'].index(best_memory)] if data['peak_memory'] else "Unknown"
    else:
        speedup_1dn = speedup_3dn = 1
        best_time = min(data['durations']) if data['durations'] else 0
        best_exp = data['experiments'][0] if data['experiments'] else "Unknown"
        best_memory = min(data['peak_memory']) if data['peak_memory'] else 0
        best_memory_exp = data['experiments'][0] if data['experiments'] else "Unknown"
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Spark/Hadoop Experiment Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        h1 {{ color: #2c3e50; text-align: center; }}
        h2 {{ color: #34495e; margin-top: 30px; }}
        table {{ border-collapse: collapse; width: 90%; margin: 20px auto; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: center; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
        .chart {{ text-align: center; margin: 30px 0; }}
        img {{ max-width: 90%; height: auto; box-shadow: 0 4px 8px rgba(0,0,0,0.1); border-radius: 5px; }}
        .footer {{ margin-top: 30px; padding: 20px; background-color: #ecf0f1; text-align: center; border-radius: 5px; }}
        .success {{ color: green; font-weight: bold; }}
        .best {{ background-color: #d4edda; }}
    </style>
</head>
<body>
    <h1> Отчет по лабораторной работе №2</h1>
    <p style="text-align: center;"><strong>Дата выполнения:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    <p style="text-align: center;"><strong>Директория результатов:</strong> {results_dir}</p>
    <p style="text-align: center;"><strong>Датасет:</strong> 150,000 строк, 8 признаков</p>
    
    <h2> Результаты экспериментов</h2>
    <table>
        <tr>
            <th>Эксперимент</th>
            <th>Время (сек)</th>
            <th>Пик RAM (MB)</th>
            <th>Оптимизация</th>
            <th>Партиции</th>
        </tr>
    """
    
    for i, exp in enumerate(data['experiments']):
        best_class = 'best' if data['durations'][i] == min(data['durations']) else ''
        html_content += f"""
        <tr> class="{best_class}">
            <td>{exp}</td>
            <td><strong>{data['durations'][i]:.2f}</strong></td>
            <td>{data['peak_memory'][i]:.0f} MB</td>
            <td class="{'success' if data['memory_increase'][i] < 100 else ''}">+{data['memory_increase'][i]:.0f} MB</td>
            <td class="{'success' if data['optimizations'][i] else ''}">{'Да' if data['optimizations'][i] else 'Нет'}</td>
            <td>{data['partitions'][i]}</td>
        </tr>
        """
    
    html_content += f"""
    </table>
    
    <h2> Графики производительности</h2>
    <div class="chart">
        <h3>Время выполнения</h3>
        <img src="execution_time.png" alt="Execution Time">
    </div>
    
    <div class="chart">
        <h3>Сравнение DataNode</h3>
        <img src="nodes_comparison.png" alt="Nodes Comparison">
    </div>
    
    <h2> Графики использования памяти (RAM)</h2>
    <div class="chart">
        <h3>Пиковое использование RAM</h3>
        <img src="memory_usage.png" alt="Memory Usage">
    </div>
    
    <div class="chart">
        <h3>Время vs Память</h3>
        <img src="time_vs_memory.png" alt="Time vs Memory">
    </div>
    """
    
    if os.path.exists(f'{results_dir}/time_breakdown.png'):
        html_content += """
    <div class="chart">
        <h3>Разбивка времени</h3>
        <img src="time_breakdown.png" alt="Time Breakdown">
    </div>
    """
    
    html_content += f"""
    <div class="chart">
        <h3>Тренд производительности</h3>
        <img src="trend.png" alt="Trend">
    </div>
    
    <div class="footer">
        <h3> Выводы</h3>
        <ul style="text-align: left; max-width: 80%; margin: 0 auto;">
            <li> Лучшее время: <strong>{best_time:.2f} секунд</strong> в конфигурации <strong>{best_exp}</strong></li>
            <li> Лучшее использование RAM: <strong>{best_memory:.0f} MB</strong> в конфигурации <strong>{best_memory_exp}</strong></li>
            <li> Оптимизация на 1 DataNode дала ускорение в <strong>{speedup_1dn:.2f}x</strong></li>
            <li> Масштабирование до 3 DataNodes дало ускорение в <strong>{speedup_3dn:.2f}x</strong></li>
        </ul>
    </div>
</body>
</html>
    """
    
    with open(f'{results_dir}/report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"HTML отчет сохранен: {results_dir}/report.html")

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 auto_plot_results.py <results_directory>")
        print("Example: python3 auto_plot_results.py results_20260406_222731")
        sys.exit(1)
    
    results_dir = sys.argv[1]
    
    if not os.path.exists(results_dir):
        print(f"Error: Directory {results_dir} not found")
        sys.exit(1)
    
    print(f"\nLoading metrics from: {results_dir}")
    metrics = load_all_metrics(results_dir)
    
    if not metrics:
        print("No metrics found!")
        if os.path.exists('metrics.json'):
            print("Found metrics.json in current directory, using it...")
            with open('metrics.json', 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            metrics.append(json.loads(line))
                        except:
                            pass
        if not metrics:
            print("No metrics to plot!")
            sys.exit(1)
    
    print(f"\nLoaded {len(metrics)} experiment results")
    
    data = extract_experiment_data(metrics)
    
    print("\nCreating plots...")
    create_comparison_plots(data, results_dir)
    
    print("\nCreating HTML report...")
    create_summary_report(data, results_dir)
    
    print(f"\nAnalysis complete! Open {results_dir}/report.html to view results")

if __name__ == "__main__":
    main()