cat > spark-defaults.conf << EOF
spark.executor.memory 1g
spark.driver.memory 1g
spark.executor.memoryOverhead 512m
spark.sql.adaptive.enabled true
spark.sql.adaptive.coalescePartitions.enabled true
EOF

# Ограничение системной памяти
sudo sysctl -w vm.max_map_count=262144