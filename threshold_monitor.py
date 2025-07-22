#!/usr/bin/env python3
"""
Threshold Monitor - A multiprocessing-based system for monitoring data sources
and exporting data when threshold rules are violated.
"""

import yaml
import json
import csv
import os
import time
import logging
import psutil
import requests
import gzip
from datetime import datetime, timedelta
from multiprocessing import Process, Queue, Manager, Event
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from logging.handlers import RotatingFileHandler

# Optional email imports - will skip email functionality if not available
try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    print("Warning: Email functionality not available. Install email packages if needed.")
    EMAIL_AVAILABLE = False


@dataclass
class MetricData:
    """Data class for metric information."""
    timestamp: str
    data_source: str
    metric_name: str
    value: float
    threshold_violated: bool
    threshold_value: float
    metadata: Dict[str, Any]


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self.load_config()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file {self.config_path} not found")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")


class DataCollector:
    """Collects data from various sources."""
    
    def __init__(self):
        self.previous_network_stats = None
        self.previous_network_time = None
    
    def collect_system_metric(self, source: str, **kwargs) -> Dict[str, Any]:
        """Collect system metrics using psutil."""
        try:
            if source == "psutil.cpu_percent":
                return {"cpu_percent": psutil.cpu_percent(interval=1)}
            
            elif source == "psutil.virtual_memory":
                mem = psutil.virtual_memory()
                return {
                    "memory_percent": mem.percent,
                    "memory_total": mem.total,
                    "memory_used": mem.used,
                    "memory_available": mem.available
                }
            
            elif source == "psutil.disk_usage":
                path = kwargs.get("path", "/")
                disk = psutil.disk_usage(path)
                total_gb = disk.total / (1024**3)
                used_gb = disk.used / (1024**3)
                return {
                    "disk_percent": (disk.used / disk.total) * 100,
                    "disk_total_gb": total_gb,
                    "disk_used_gb": used_gb,
                    "disk_free_gb": (disk.total - disk.used) / (1024**3)
                }
            
            elif source == "psutil.net_io_counters":
                current_stats = psutil.net_io_counters()
                current_time = time.time()
                
                if self.previous_network_stats and self.previous_network_time:
                    time_diff = current_time - self.previous_network_time
                    bytes_sent_diff = current_stats.bytes_sent - self.previous_network_stats.bytes_sent
                    bytes_recv_diff = current_stats.bytes_recv - self.previous_network_stats.bytes_recv
                    
                    bytes_sent_per_sec = bytes_sent_diff / time_diff if time_diff > 0 else 0
                    bytes_recv_per_sec = bytes_recv_diff / time_diff if time_diff > 0 else 0
                else:
                    bytes_sent_per_sec = 0
                    bytes_recv_per_sec = 0
                
                self.previous_network_stats = current_stats
                self.previous_network_time = current_time
                
                return {
                    "bytes_sent_per_sec": bytes_sent_per_sec,
                    "bytes_recv_per_sec": bytes_recv_per_sec,
                    "total_bytes_sent": current_stats.bytes_sent,
                    "total_bytes_recv": current_stats.bytes_recv
                }
            
        except Exception as e:
            logging.error(f"Error collecting system metric {source}: {e}")
            return {}
    
    def collect_api_metric(self, source: str, **kwargs) -> Dict[str, Any]:
        """Collect data from API endpoints."""
        try:
            response = requests.get(source, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Error collecting API metric from {source}: {e}")
            return {}


class ThresholdChecker:
    """Checks if metrics violate threshold rules."""
    
    def __init__(self):
        self.violation_counts = {}
    
    def check_threshold(self, rule: Dict[str, Any], metric_data: Dict[str, Any]) -> bool:
        """Check if a metric violates the threshold rule."""
        metric_name = rule["metric_name"]
        threshold_type = rule["threshold_type"]
        threshold_value = rule["threshold_value"]
        consecutive_violations = rule["consecutive_violations"]
        
        if metric_name not in metric_data:
            return False
        
        current_value = metric_data[metric_name]
        rule_key = f"{rule['data_source']}_{metric_name}"
        
        # Check if threshold is violated
        violation = False
        if threshold_type == "greater_than":
            violation = current_value > threshold_value
        elif threshold_type == "less_than":
            violation = current_value < threshold_value
        elif threshold_type == "equals":
            violation = current_value == threshold_value
        
        # Track consecutive violations
        if violation:
            self.violation_counts[rule_key] = self.violation_counts.get(rule_key, 0) + 1
        else:
            self.violation_counts[rule_key] = 0
        
        # Return True if consecutive violations threshold is met
        return self.violation_counts[rule_key] >= consecutive_violations


class DataExporter:
    """Handles data export functionality."""
    
    def __init__(self, export_settings: Dict[str, Any]):
        self.settings = export_settings
        self.export_dir = Path(export_settings["export_directory"])
        self.export_dir.mkdir(exist_ok=True)
        
        # Create logs directory if needed
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
    
    def export_data(self, metric_data: MetricData) -> None:
        """Export metric data using configured destinations."""
        if not self.settings["enabled"]:
            return
        
        for destination in self.settings["destinations"]:
            if not destination["enabled"]:
                continue
                
            try:
                if destination["type"] == "file":
                    self._export_to_file(metric_data)
                elif destination["type"] == "webhook":
                    self._export_to_webhook(metric_data, destination)
                elif destination["type"] == "email":
                    self._export_to_email(metric_data, destination)
            except Exception as e:
                logging.error(f"Error exporting to {destination['type']}: {e}")
    
    def _export_to_file(self, metric_data: MetricData) -> None:
        """Export data to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for format_type in self.settings["export_formats"]:
            if format_type == "json":
                filename = f"threshold_violation_{timestamp}.json"
                filepath = self.export_dir / filename
                
                with open(filepath, 'w') as f:
                    json.dump(asdict(metric_data), f, indent=2)
                
                if self.settings.get("compress_exports", False):
                    self._compress_file(filepath)
                    
            elif format_type == "csv":
                filename = f"threshold_violation_{timestamp}.csv"
                filepath = self.export_dir / filename
                
                with open(filepath, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=asdict(metric_data).keys())
                    writer.writeheader()
                    writer.writerow(asdict(metric_data))
                
                if self.settings.get("compress_exports", False):
                    self._compress_file(filepath)
        
        self._cleanup_old_exports()
    
    def _export_to_webhook(self, metric_data: MetricData, destination: Dict[str, Any]) -> None:
        """Export data to webhook."""
        headers = destination.get("headers", {})
        response = requests.post(
            destination["url"],
            json=asdict(metric_data),
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        logging.info(f"Data exported to webhook: {destination['url']}")
    
    def _export_to_email(self, metric_data: MetricData, destination: Dict[str, Any]) -> None:
        """Export data via email."""
        if not EMAIL_AVAILABLE:
            logging.error("Email functionality not available. Cannot send email notifications.")
            return
            
        msg = MimeMultipart()
        msg['From'] = destination["username"]
        msg['To'] = ", ".join(destination["to_addresses"])
        msg['Subject'] = f"Threshold Violation Alert - {metric_data.data_source}"
        
        body = f"""
        Threshold Violation Detected:
        
        Data Source: {metric_data.data_source}
        Metric: {metric_data.metric_name}
        Current Value: {metric_data.value}
        Threshold: {metric_data.threshold_value}
        Timestamp: {metric_data.timestamp}
        
        Metadata: {json.dumps(metric_data.metadata, indent=2)}
        """
        
        msg.attach(MimeText(body, 'plain'))
        
        server = smtplib.SMTP(destination["smtp_server"], destination["smtp_port"])
        server.starttls()
        server.login(destination["username"], destination["password"])
        server.send_message(msg)
        server.quit()
        
        logging.info(f"Alert email sent to {destination['to_addresses']}")
    
    def _compress_file(self, filepath: Path) -> None:
        """Compress a file using gzip."""
        with open(filepath, 'rb') as f_in:
            with gzip.open(f"{filepath}.gz", 'wb') as f_out:
                f_out.writelines(f_in)
        filepath.unlink()  # Remove original file
    
    def _cleanup_old_exports(self) -> None:
        """Clean up old export files."""
        max_files = self.settings.get("max_export_files", 100)
        
        # Get all export files
        export_files = []
        for pattern in ["*.json", "*.csv", "*.json.gz", "*.csv.gz"]:
            export_files.extend(self.export_dir.glob(pattern))
        
        # Sort by modification time and remove oldest files
        export_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for old_file in export_files[max_files:]:
            try:
                old_file.unlink()
                logging.info(f"Removed old export file: {old_file}")
            except Exception as e:
                logging.error(f"Error removing old export file {old_file}: {e}")


def data_source_worker(data_source: Dict[str, Any], shared_data: Dict, stop_event: Event, 
                      violation_queue: Queue) -> None:
    """Worker process for monitoring a single data source."""
    logging.info(f"Started worker for data source: {data_source['name']}")
    
    collector = DataCollector()
    checker = ThresholdChecker()
    
    # Get threshold rules for this data source
    config = ConfigManager().config
    rules = [rule for rule in config["threshold_rules"] 
             if rule["data_source"] == data_source["name"] and rule["enabled"]]
    
    while not stop_event.is_set():
        try:
            # Collect data
            if data_source["type"] == "system_metric":
                metric_data = collector.collect_system_metric(
                    data_source["source"], 
                    **{k: v for k, v in data_source.items() if k not in ["name", "type", "source", "interval", "enabled"]}
                )
            elif data_source["type"] == "api_endpoint":
                metric_data = collector.collect_api_metric(data_source["source"])
            else:
                logging.warning(f"Unknown data source type: {data_source['type']}")
                continue
            
            if not metric_data:
                logging.warning(f"No data collected from {data_source['name']}")
                time.sleep(data_source["interval"])
                continue
            
            # Check thresholds
            for rule in rules:
                if checker.check_threshold(rule, metric_data):
                    # Threshold violated - create export data
                    export_data = MetricData(
                        timestamp=datetime.now().isoformat(),
                        data_source=data_source["name"],
                        metric_name=rule["metric_name"],
                        value=metric_data[rule["metric_name"]],
                        threshold_violated=True,
                        threshold_value=rule["threshold_value"],
                        metadata={
                            "rule": rule,
                            "all_metrics": metric_data,
                            "data_source_config": data_source
                        }
                    )
                    
                    # Send to violation queue for export
                    violation_queue.put(export_data)
                    logging.warning(f"Threshold violation detected: {data_source['name']}.{rule['metric_name']} = {metric_data[rule['metric_name']]}")
            
            # Update shared data for monitoring
            shared_data[data_source["name"]] = {
                "last_update": datetime.now().isoformat(),
                "metrics": metric_data,
                "status": "healthy"
            }
            
        except Exception as e:
            logging.error(f"Error in worker for {data_source['name']}: {e}")
            shared_data[data_source["name"]] = {
                "last_update": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }
        
        time.sleep(data_source["interval"])


def export_worker(violation_queue: Queue, stop_event: Event, export_settings: Dict[str, Any]) -> None:
    """Worker process for handling data exports."""
    logging.info("Started export worker")
    
    exporter = DataExporter(export_settings)
    
    while not stop_event.is_set():
        try:
            # Wait for violation data with timeout
            metric_data = violation_queue.get(timeout=1)
            exporter.export_data(metric_data)
            logging.info(f"Exported violation data for {metric_data.data_source}")
        except:
            # Timeout or queue empty - continue
            continue


def setup_logging(logging_config: Dict[str, Any]) -> None:
    """Setup logging configuration."""
    log_level = getattr(logging, logging_config.get("level", "INFO").upper())
    
    # Create logs directory
    log_file = Path(logging_config.get("file", "./logs/monitor.log"))
    log_file.parent.mkdir(exist_ok=True)
    
    # Setup rotating file handler
    handler = RotatingFileHandler(
        log_file,
        maxBytes=logging_config.get("max_size_mb", 10) * 1024 * 1024,
        backupCount=logging_config.get("backup_count", 5)
    )
    
    # Setup console handler
    console_handler = logging.StreamHandler()
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(processName)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    logging.getLogger().setLevel(log_level)
    logging.getLogger().addHandler(handler)
    logging.getLogger().addHandler(console_handler)


def main():
    """Main function to start the monitoring system."""
    try:
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.config
        
        # Setup logging
        setup_logging(config["logging"])
        logging.info("Starting Threshold Monitor System")
        
        # Create shared data structure for monitoring
        manager = Manager()
        shared_data = manager.dict()
        
        # Create queues and events
        violation_queue = Queue()
        stop_event = Event()
        
        # Start data source workers
        workers = []
        enabled_sources = [ds for ds in config["data_sources"] if ds["enabled"]]
        
        for data_source in enabled_sources:
            worker = Process(
                target=data_source_worker,
                args=(data_source, shared_data, stop_event, violation_queue),
                name=f"Worker-{data_source['name']}"
            )
            worker.start()
            workers.append(worker)
            logging.info(f"Started worker for data source: {data_source['name']}")
        
        # Start export worker
        export_worker_process = Process(
            target=export_worker,
            args=(violation_queue, stop_event, config["export_settings"]),
            name="ExportWorker"
        )
        export_worker_process.start()
        workers.append(export_worker_process)
        
        logging.info(f"Started {len(workers)} worker processes")
        
        # Main monitoring loop
        try:
            while True:
                time.sleep(config["monitoring"]["check_interval"])
                
                # Log system status
                if len(shared_data) > 0:
                    logging.debug(f"Monitoring {len(shared_data)} data sources")
                    for source_name, source_data in shared_data.items():
                        if source_data.get("status") == "error":
                            logging.error(f"Data source {source_name} has error: {source_data.get('error')}")
                
        except KeyboardInterrupt:
            logging.info("Received shutdown signal")
        
    except Exception as e:
        logging.error(f"Fatal error in main: {e}")
        
    finally:
        # Cleanup
        logging.info("Shutting down monitoring system")
        stop_event.set()
        
        # Wait for workers to finish
        for worker in workers:
            worker.join(timeout=5)
            if worker.is_alive():
                logging.warning(f"Force terminating worker: {worker.name}")
                worker.terminate()
        
        logging.info("Monitoring system shutdown complete")


if __name__ == "__main__":
    main()