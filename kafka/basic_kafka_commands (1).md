
# Kafka Commands (Basic to Advanced)

## 1. Cluster Information
```bash
# List all Kafka topics
kafka-topics.sh --list --bootstrap-server localhost:9092

# Describe a topic
kafka-topics.sh --describe --topic my-topic --bootstrap-server localhost:9092

# Get broker information
kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```

## 2. Topic Management
```bash
# Create a topic
kafka-topics.sh --create --topic my-topic --partitions 3 --replication-factor 2 --bootstrap-server localhost:9092

# Delete a topic
kafka-topics.sh --delete --topic my-topic --bootstrap-server localhost:9092

# Increase partitions
kafka-topics.sh --alter --topic my-topic --partitions 5 --bootstrap-server localhost:9092
```

## 3. Producing Messages
```bash
# Console producer
kafka-console-producer.sh --topic my-topic --bootstrap-server localhost:9092

# Producer with key
kafka-console-producer.sh --topic my-topic --property parse.key=true --property key.separator=: --bootstrap-server localhost:9092
```

## 4. Consuming Messages
```bash
# Console consumer
kafka-console-consumer.sh --topic my-topic --from-beginning --bootstrap-server localhost:9092

# Consumer from a specific group
kafka-console-consumer.sh --topic my-topic --group my-group --bootstrap-server localhost:9092
```

## 5. Consumer Groups
```bash
# List consumer groups
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --list

# Describe a consumer group
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group my-group

# Reset offsets (to earliest)
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group my-group --reset-offsets --to-earliest --execute --topic my-topic
```

## 6. Kafka ACLs (Security)
```bash
# Add an ACL for a user to produce to a topic
kafka-acls.sh --authorizer-properties zookeeper.connect=localhost:2181 --add --allow-principal User:alice --operation Write --topic my-topic

# List ACLs
kafka-acls.sh --authorizer-properties zookeeper.connect=localhost:2181 --list
```

## 7. Kafka Connect
```bash
# List connectors
curl -s localhost:8083/connectors

# Create a connector
curl -X POST -H "Content-Type: application/json" --data @connector-config.json http://localhost:8083/connectors

# Get connector status
curl -s localhost:8083/connectors/my-connector/status
```

## 8. Kafka MirrorMaker
```bash
# Start MirrorMaker
kafka-mirror-maker.sh --consumer.config consumer.properties --producer.config producer.properties --whitelist=".*"
```

## 9. Advanced Tools
```bash
# Check log segments of a topic
kafka-run-class.sh kafka.tools.DumpLogSegments --files /tmp/kafka-logs/my-topic-0/00000000000000000000.log

# Run Kafka performance producer test
kafka-producer-perf-test.sh --topic test --num-records 100000 --record-size 100 --throughput -1 --producer-props bootstrap.servers=localhost:9092

# Run Kafka performance consumer test
kafka-consumer-perf-test.sh --bootstrap-server localhost:9092 --topic test --fetch-size 1048576 --messages 1000000 --threads 1
```
