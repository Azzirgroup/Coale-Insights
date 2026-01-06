# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import asyncio
from enum import Enum
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import json
import time
from concurrent.futures import ThreadPoolExecutor
import queue
import threading


class ProcessingMode(Enum):
    """Processing mode for different operation types"""
    REALTIME = "realtime"    # Immediate processing (<3 seconds)
    NEAR_REALTIME = "near_realtime"  # Quick background processing (<30 seconds)  
    BATCH = "batch"          # Scheduled batch processing (minutes to hours)


class Priority(Enum):
    """Task priority levels"""
    CRITICAL = 1  # User-facing interactions
    HIGH = 2      # Business alerts
    MEDIUM = 3    # Standard analytics
    LOW = 4       # Background optimization


@dataclass
class ProcessingTask:
    """Task definition for processing pipeline"""
    task_id: str
    task_type: str
    mode: ProcessingMode
    priority: Priority
    payload: Dict[str, Any]
    user_id: str
    created_at: datetime
    timeout: int = 30
    retry_count: int = 0
    max_retries: int = 3
    callback: Optional[Callable] = None


class ProcessingPipeline:
    """Intelligent processing pipeline for real-time vs batch operations"""
    
    def __init__(self):
        self.realtime_queue = queue.PriorityQueue()
        self.batch_queue = queue.Queue()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.processing_rules = self._initialize_processing_rules()
        self.active_tasks = {}
        self.performance_metrics = {}
        
    def _initialize_processing_rules(self) -> Dict[str, Dict]:
        """Initialize processing rules for different operation types"""
        return {
            # Real-time Operations (< 3 seconds)
            "dashboard_refresh": {
                "mode": ProcessingMode.REALTIME,
                "priority": Priority.CRITICAL,
                "timeout": 3,
                "description": "Dashboard widget data updates"
            },
            "simple_query": {
                "mode": ProcessingMode.REALTIME, 
                "priority": Priority.HIGH,
                "timeout": 5,
                "description": "Simple data queries (<3 tables)"
            },
            "user_question": {
                "mode": ProcessingMode.REALTIME,
                "priority": Priority.CRITICAL,
                "timeout": 10,
                "description": "Natural language Q&A"
            },
            "sales_alert": {
                "mode": ProcessingMode.REALTIME,
                "priority": Priority.HIGH,
                "timeout": 2,
                "description": "Sales order/invoice alerts"
            },
            "inventory_alert": {
                "mode": ProcessingMode.REALTIME,
                "priority": Priority.HIGH,
                "timeout": 2,
                "description": "Stock shortage warnings"
            },
            "customer_insight": {
                "mode": ProcessingMode.REALTIME,
                "priority": Priority.MEDIUM,
                "timeout": 8,
                "description": "Customer interaction insights"
            },
            
            # Near Real-time Operations (< 30 seconds)
            "medium_query": {
                "mode": ProcessingMode.NEAR_REALTIME,
                "priority": Priority.MEDIUM,
                "timeout": 30,
                "description": "Medium complexity queries (3-8 tables)"
            },
            "chart_generation": {
                "mode": ProcessingMode.NEAR_REALTIME,
                "priority": Priority.MEDIUM,
                "timeout": 20,
                "description": "Chart and visualization generation"
            },
            "report_preview": {
                "mode": ProcessingMode.NEAR_REALTIME,
                "priority": Priority.MEDIUM,
                "timeout": 25,
                "description": "Report preview generation"
            },
            
            # Batch Operations (minutes to hours)
            "sales_forecast": {
                "mode": ProcessingMode.BATCH,
                "priority": Priority.MEDIUM,
                "timeout": 300,
                "description": "Sales forecasting models"
            },
            "customer_segmentation": {
                "mode": ProcessingMode.BATCH,
                "priority": Priority.LOW,
                "timeout": 600,
                "description": "Customer segmentation analysis"
            },
            "trend_analysis": {
                "mode": ProcessingMode.BATCH,
                "priority": Priority.MEDIUM,
                "timeout": 900,
                "description": "Multi-period trend analysis"
            },
            "financial_analysis": {
                "mode": ProcessingMode.BATCH,
                "priority": Priority.MEDIUM,
                "timeout": 1800,
                "description": "Complex financial analysis"
            },
            "manufacturing_optimization": {
                "mode": ProcessingMode.BATCH,
                "priority": Priority.LOW,
                "timeout": 1200,
                "description": "Manufacturing process optimization"
            },
            "audit_report": {
                "mode": ProcessingMode.BATCH,
                "priority": Priority.LOW,
                "timeout": 2400,
                "description": "Comprehensive audit reports"
            },
            "ml_model_training": {
                "mode": ProcessingMode.BATCH,
                "priority": Priority.LOW,
                "timeout": 3600,
                "description": "Machine learning model training"
            }
        }
    
    def submit_task(self, task_type: str, payload: Dict[str, Any], 
                   user_id: str = None, callback: Callable = None) -> str:
        """Submit task for processing with automatic mode detection"""
        
        # Get processing rule for task type
        rule = self.processing_rules.get(task_type)
        if not rule:
            # Default to medium complexity
            rule = {
                "mode": ProcessingMode.NEAR_REALTIME,
                "priority": Priority.MEDIUM,
                "timeout": 30
            }
        
        # Create processing task
        task = ProcessingTask(
            task_id=frappe.generate_hash(length=12),
            task_type=task_type,
            mode=ProcessingMode(rule["mode"]),
            priority=Priority(rule["priority"]),
            payload=payload,
            user_id=user_id or frappe.session.user,
            created_at=datetime.now(),
            timeout=rule["timeout"],
            callback=callback
        )
        
        # Route to appropriate processing pipeline
        if task.mode == ProcessingMode.REALTIME:
            return self._process_realtime(task)
        elif task.mode == ProcessingMode.NEAR_REALTIME:
            return self._process_near_realtime(task)
        else:
            return self._process_batch(task)
    
    def _process_realtime(self, task: ProcessingTask) -> str:
        """Process real-time tasks immediately"""
        start_time = time.time()
        
        try:
            # Execute task immediately
            result = self._execute_task(task)
            
            # Send immediate response
            response_time = time.time() - start_time
            
            # Publish real-time update via WebSocket
            self._publish_realtime_result(task, result, response_time)
            
            # Log performance
            self._log_performance(task, response_time, success=True)
            
            return task.task_id
            
        except Exception as e:
            frappe.log_error(f"Real-time task failed: {str(e)}")
            self._publish_realtime_error(task, str(e))
            self._log_performance(task, time.time() - start_time, success=False, error=str(e))
            return task.task_id
    
    def _process_near_realtime(self, task: ProcessingTask) -> str:
        """Process near real-time tasks with background execution"""
        
        # Add to priority queue for background processing
        self.realtime_queue.put((task.priority.value, task.created_at.timestamp(), task))
        
        # Start background worker if not running
        self._ensure_background_workers()
        
        # Return task ID for tracking
        return task.task_id
    
    def _process_batch(self, task: ProcessingTask) -> str:
        """Process batch tasks via Celery or scheduler"""
        
        # For immediate implementation, use background queue
        self.batch_queue.put(task)
        
        # In production, this would submit to Celery
        # self._submit_to_celery(task)
        
        # Start batch worker if needed
        self._ensure_batch_workers()
        
        return task.task_id
    
    def _execute_task(self, task: ProcessingTask) -> Any:
        """Execute the actual task logic"""
        
        # Import task processors
        from insights.processing.task_processors import TaskProcessor
        
        processor = TaskProcessor()
        
        # Route to appropriate processor method
        method_name = f"process_{task.task_type}"
        
        if hasattr(processor, method_name):
            method = getattr(processor, method_name)
            return method(task.payload, task.user_id)
        else:
            # Fallback to generic processor
            return processor.process_generic(task.task_type, task.payload, task.user_id)
    
    def _publish_realtime_result(self, task: ProcessingTask, result: Any, response_time: float):
        """Publish real-time result via WebSocket"""
        
        message = {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "result": result,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        # Publish via Frappe's realtime system
        frappe.publish_realtime(
            event="insights_task_completed",
            message=message,
            user=task.user_id
        )
        
        # Execute callback if provided
        if task.callback:
            try:
                task.callback(result)
            except Exception as e:
                frappe.log_error(f"Task callback failed: {str(e)}")
    
    def _publish_realtime_error(self, task: ProcessingTask, error: str):
        """Publish real-time error via WebSocket"""
        
        message = {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "status": "failed"
        }
        
        frappe.publish_realtime(
            event="insights_task_failed",
            message=message,
            user=task.user_id
        )
    
    def _ensure_background_workers(self):
        """Ensure background workers are running for near real-time processing"""
        
        # Check if background worker thread is running
        if not hasattr(self, '_background_worker_running'):
            self._background_worker_running = True
            threading.Thread(target=self._background_worker, daemon=True).start()
    
    def _ensure_batch_workers(self):
        """Ensure batch workers are running"""
        
        if not hasattr(self, '_batch_worker_running'):
            self._batch_worker_running = True
            threading.Thread(target=self._batch_worker, daemon=True).start()
    
    def _background_worker(self):
        """Background worker for near real-time tasks"""
        
        while True:
            try:
                # Get task from priority queue (blocks until available)
                _, _, task = self.realtime_queue.get(timeout=60)
                
                start_time = time.time()
                
                try:
                    # Execute task
                    result = self._execute_task(task)
                    response_time = time.time() - start_time
                    
                    # Publish result
                    self._publish_realtime_result(task, result, response_time)
                    self._log_performance(task, response_time, success=True)
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    self._publish_realtime_error(task, str(e))
                    self._log_performance(task, response_time, success=False, error=str(e))
                
                self.realtime_queue.task_done()
                
            except queue.Empty:
                # Timeout waiting for tasks - continue loop
                continue
            except Exception as e:
                frappe.log_error(f"Background worker error: {str(e)}")
                time.sleep(1)  # Brief pause before retry
    
    def _batch_worker(self):
        """Batch worker for long-running tasks"""
        
        while True:
            try:
                # Get task from batch queue
                task = self.batch_queue.get(timeout=300)  # 5 minute timeout
                
                start_time = time.time()
                
                try:
                    # Update task status
                    self._update_task_status(task.task_id, "processing")
                    
                    # Execute task
                    result = self._execute_task(task)
                    response_time = time.time() - start_time
                    
                    # Update completion status
                    self._update_task_status(task.task_id, "completed", result)
                    self._log_performance(task, response_time, success=True)
                    
                    # Notify completion
                    frappe.publish_realtime(
                        event="insights_batch_completed",
                        message={
                            "task_id": task.task_id,
                            "task_type": task.task_type,
                            "response_time": response_time,
                            "timestamp": datetime.now().isoformat()
                        },
                        user=task.user_id
                    )
                    
                except Exception as e:
                    response_time = time.time() - start_time
                    self._update_task_status(task.task_id, "failed", error=str(e))
                    self._log_performance(task, response_time, success=False, error=str(e))
                
                self.batch_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                frappe.log_error(f"Batch worker error: {str(e)}")
                time.sleep(5)
    
    def _update_task_status(self, task_id: str, status: str, result: Any = None, error: str = None):
        """Update task status in database"""
        
        try:
            # Check if task status record exists
            existing = frappe.db.get_value("Processing Task Status", {"task_id": task_id}, "name")
            
            if existing:
                # Update existing
                frappe.db.set_value(
                    "Processing Task Status", 
                    existing,
                    {
                        "status": status,
                        "result": json.dumps(result) if result else None,
                        "error": error,
                        "completed_at": datetime.now() if status in ["completed", "failed"] else None
                    }
                )
            else:
                # Create new status record
                status_doc = frappe.get_doc({
                    "doctype": "Processing Task Status",
                    "task_id": task_id,
                    "status": status,
                    "result": json.dumps(result) if result else None,
                    "error": error,
                    "started_at": datetime.now() if status == "processing" else None,
                    "completed_at": datetime.now() if status in ["completed", "failed"] else None
                })
                status_doc.insert(ignore_permissions=True)
            
            frappe.db.commit()
            
        except Exception as e:
            frappe.log_error(f"Task status update failed: {str(e)}")
    
    def _log_performance(self, task: ProcessingTask, response_time: float, 
                        success: bool, error: str = None):
        """Log task performance metrics"""
        
        try:
            perf_log = frappe.get_doc({
                "doctype": "Processing Performance Log",
                "task_id": task.task_id,
                "task_type": task.task_type,
                "processing_mode": task.mode.value,
                "priority": task.priority.value,
                "response_time": response_time,
                "success": success,
                "error": error,
                "user": task.user_id,
                "timestamp": datetime.now()
            })
            perf_log.insert(ignore_permissions=True)
            
            # Update performance metrics cache
            if task.task_type not in self.performance_metrics:
                self.performance_metrics[task.task_type] = {
                    "total_requests": 0,
                    "success_count": 0,
                    "avg_response_time": 0,
                    "last_updated": datetime.now()
                }
            
            metrics = self.performance_metrics[task.task_type]
            metrics["total_requests"] += 1
            if success:
                metrics["success_count"] += 1
            
            # Update running average
            metrics["avg_response_time"] = (
                (metrics["avg_response_time"] * (metrics["total_requests"] - 1) + response_time)
                / metrics["total_requests"]
            )
            metrics["last_updated"] = datetime.now()
            
        except Exception as e:
            frappe.log_error(f"Performance logging failed: {str(e)}")
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get current status of a task"""
        
        try:
            status_record = frappe.db.get_value(
                "Processing Task Status",
                {"task_id": task_id},
                ["status", "result", "error", "started_at", "completed_at"],
                as_dict=True
            )
            
            if status_record:
                return {
                    "task_id": task_id,
                    **status_record
                }
            else:
                return {"task_id": task_id, "status": "unknown"}
                
        except Exception as e:
            return {"task_id": task_id, "status": "error", "error": str(e)}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for all task types"""
        return self.performance_metrics.copy()


# Global processing pipeline instance
processing_pipeline = ProcessingPipeline()


# Convenience functions for external use
def submit_processing_task(task_type: str, payload: Dict[str, Any], 
                         user_id: str = None, callback: Callable = None) -> str:
    """Submit task for intelligent processing routing"""
    return processing_pipeline.submit_task(task_type, payload, user_id, callback)


def get_task_status(task_id: str) -> Dict[str, Any]:
    """Get current status of a processing task"""
    return processing_pipeline.get_task_status(task_id)


def get_processing_performance() -> Dict[str, Any]:
    """Get performance metrics for processing pipeline"""
    return processing_pipeline.get_performance_metrics()


# Task type helpers
def is_realtime_task(task_type: str) -> bool:
    """Check if task type is processed in real-time"""
    rule = processing_pipeline.processing_rules.get(task_type, {})
    return rule.get("mode") == ProcessingMode.REALTIME


def get_processing_rules() -> Dict[str, Dict]:
    """Get all processing rules for reference"""
    return processing_pipeline.processing_rules.copy()


# Decorator for automatic task submission
def process_intelligently(task_type: str = None):
    """Decorator for automatic intelligent processing"""
    
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Determine task type from function name if not provided
            actual_task_type = task_type or func.__name__
            
            # Prepare payload
            payload = {
                "function": func.__name__,
                "args": args,
                "kwargs": kwargs
            }
            
            # Submit for processing
            task_id = submit_processing_task(
                actual_task_type,
                payload,
                frappe.session.user
            )
            
            # For real-time tasks, wait for result
            if is_realtime_task(actual_task_type):
                # Execute directly for real-time
                return func(*args, **kwargs)
            else:
                # Return task ID for async tracking
                return {"task_id": task_id, "status": "submitted"}
        
        return wrapper
    return decorator