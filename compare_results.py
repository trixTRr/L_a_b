import json
import sys

def main():
    print("\n" + "="*60)
    print("EXPERIMENT RESULTS")
    print("="*60)
    
    try:
        with open('metrics.json', 'r') as f:
            metrics = [json.loads(line) for line in f if line.strip()]
        
        if not metrics:
            print("No metrics found. Run experiments first.")
            return
        
        print("\n{:<25} {:<15} {:<15} {:<15}".format(
            "Experiment", "Duration(s)", "Optimization", "Partitions"
        ))
        print("-" * 70)
        
        for m in metrics:
            print("{:<25} {:<15} {:<15} {:<15}".format(
                m.get('experiment', 'Unknown'),
                m.get('duration_seconds', 'N/A'),
                "Yes" if m.get('optimization') else "No",
                m.get('partitions', 'N/A')
            ))
        
        # Простой анализ
        if len(metrics) >= 2:
            base_time = metrics[0].get('duration_seconds', 0)
            opt_time = metrics[1].get('duration_seconds', 0) if len(metrics) > 1 else 0
            
            if base_time and opt_time:
                speedup = base_time / opt_time
                print(f"\nOptimization speedup (1 DN): {speedup:.2f}x")
        
    except FileNotFoundError:
        print("No metrics file found. Run experiments first.")
    except Exception as e:
        print(f"Error reading metrics: {e}")

if __name__ == "__main__":
    main()