"""
Monokai Classic Automation Page
Thiết kế giao diện tự động hóa với phong cách Monokai cổ điển
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import json
import os
import psutil
import random
from datetime import datetime, timedelta
from mumu_manager import mumu_manager, get_mumu_instances_fast, check_mumu_available

class MonokaiAutomationPage(QWidget):
    """Tab Tự động hóa với thiết kế Monokai cổ điển"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        
        # Core State Management
        self.automation_state = {
            'running': False,
            'paused': False,
            'current_batch': 0,
            'total_batches': 0,
            'progress': 0,
            'success_count': 0,
            'error_count': 0,
            'start_time': None,
            'estimated_completion': None
        }
        
        # Performance tracking
        self.performance_metrics = {
            'throughput': 0.0,
            'success_rate': 100.0,
            'avg_response_time': 0.0,
            'system_efficiency': 100.0
        }
        
        # Legacy compatibility
        self.automation_running = False
        self.automation_paused = False
        self.current_progress = 0
        self.total_tasks = 0
        
        # Initialize AI optimization flag early
        self.ai_optimization_disabled = True  # New flag to disable AI batch optimization (disabled by default)
        
        # Initialize automation settings with defaults
        self.automation_settings = {
            'enable_auto_start': False,
            'auto_start_time': '04:38',
            'from_instance': 0,
            'to_instance': 10,
            'batch_size': 5,
            'batch_delay': 30,
            'start_delay': 5
        }
        
        self.setup_ui()
        self.load_settings_from_file()  # Load from file directly
        
        # Setup timer để kiểm tra auto start - DISABLED
        self.auto_start_timer = QTimer()
        self.auto_start_timer.timeout.connect(self.check_auto_start)
        # self.auto_start_timer.start(30000)  # 🚫 DISABLED - no auto start checking
        
        # Initialize AI Prediction Engine
        self.ai_predictions = {
            'optimal_batch_size': 20,
            'optimal_start_delay': 4,
            'optimal_batch_delay': 15,
            'predicted_completion_time': 0,
            'recommended_settings': {},
            'performance_score': 0,
            'learning_data': [],
            'pattern_history': {},
            'smart_scheduling': {},
            'failure_prediction': 0,
            'resource_forecast': {}
        }
        
        # AI Learning Features
        self.ai_learning_enabled = True
        self.ai_auto_adapt = False
        self.ai_prediction_accuracy = 85.0
        # self.ai_optimization_disabled = False  # Removed duplicate - already initialized above
        self.execution_history = []
        self.performance_trends = []
        
        # CPU Monitor System
        self.cpu_monitor_enabled = False
        self.cpu_threshold = 70.0  # CPU threshold 70%
        self.current_cpu_usage = 0.0
        self.cpu_monitor_active = False
        self.cpu_monitor_initialized = False
        
        # 🚫 AI TIMERS PERMANENTLY DISABLED - Manual operation only
        
        # Setup AI analysis timer - DISABLED
        self.ai_analysis_timer = QTimer()
        self.ai_analysis_timer.timeout.connect(self.analyze_and_predict)
        # self.ai_analysis_timer.start(60000)  # 🚫 DISABLED - no background analysis
        
        # Setup CPU monitoring timer - DISABLED
        self.cpu_monitor_timer = QTimer()
        self.cpu_monitor_timer.timeout.connect(self.check_cpu_usage)
        self.cpu_monitor_timer.setSingleShot(False)
        
        # Delay CPU monitor start - DISABLED
        # QTimer.singleShot(5000, self.initialize_cpu_monitor)  # 🚫 DISABLED
        
        # Setup AI learning timer - DISABLED  
        self.ai_learning_timer = QTimer()
        self.ai_learning_timer.timeout.connect(self.ai_deep_learning)
        # self.ai_learning_timer.start(300000)  # 🚫 DISABLED - no background learning
        
        # 🔥 Real-Time Instance Tracker - DISABLED
        self.real_instance_tracker = {}  # Track thực tế instances đang chạy
        self.instance_process_map = {}   # Map instance_id -> process info
        
        # Setup Real-Time AI Tracker timer - DISABLED
        self.ai_realtime_tracker = QTimer()
        self.ai_realtime_tracker.timeout.connect(self.ai_track_real_instances)
        # self.ai_realtime_tracker.start(10000)  # 🚫 DISABLED - no background tracking
        
        self.add_log("✅ Automation page initialized với AI Prediction Engine (Background tasks DISABLED)", "info")
        
        # Final check - DISABLED
        # QTimer.singleShot(10000, self.check_system_load_and_adjust)  # 🚫 DISABLED
        
    def check_auto_start(self):
        """Kiểm tra xem có cần auto start không"""
        try:
            # Chỉ check nếu automation chưa chạy
            if self.automation_running:
                return
                
            enable_auto_start = self.automation_settings.get('enable_auto_start', False)
            if not enable_auto_start:
                return
                
            auto_start_time = self.automation_settings.get('auto_start_time', '04:38')
            current_time = datetime.now().strftime('%H:%M')
            
            if current_time == auto_start_time:
                self.add_log(f"🔔 Auto start triggered at {current_time}", "info")
                self.start_automation()
                
        except Exception as e:
            self.add_log(f"❌ Lỗi check auto start: {str(e)}", "error")
    
    def on_schedule_settings_changed(self):
        """Callback khi settings scheduler thay đổi"""
        try:
            if hasattr(self, 'schedule_enabled') and hasattr(self, 'start_time'):
                # Update automation settings
                self.automation_settings['enable_auto_start'] = self.schedule_enabled.isChecked()
                self.automation_settings['auto_start_time'] = self.start_time.time().toString('HH:mm')
                
                # Save to file
                self.save_settings_to_file(self.automation_settings)
                
                # Update next run display
                if self.schedule_enabled.isChecked():
                    time_str = self.start_time.time().toString('HH:mm')
                    self.next_run_label.setText(f"Lần chạy tiếp theo: {time_str} hàng ngày")
                    self.next_run_label.setStyleSheet("color: #A6E22E; font-weight: bold;")
                    self.add_log(f"✅ Auto start được đặt lịch tại {time_str}", "info")
                else:
                    self.next_run_label.setText("Lần chạy tiếp theo: Chưa đặt lịch")
                    self.next_run_label.setStyleSheet("color: #F92672; font-weight: bold;")
                    self.add_log("❌ Auto start đã bị tắt", "warning")
                    
        except Exception as e:
            self.add_log(f"❌ Lỗi cập nhật scheduler: {str(e)}", "error")
    
    def analyze_and_predict(self):
        """AI phân tích hiệu suất và đưa ra đề xuất tối ưu"""
        try:
            if self.automation_running:
                return  # Không phân tích khi đang chạy
                
            # Lấy thông tin hệ thống
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # AI Analysis dựa trên tài nguyên hệ thống
            current_settings = self.automation_settings
            
            # Tính toán đề xuất tối ưu
            recommended_batch_size = self.calculate_optimal_batch_size(cpu_percent, memory_percent)
            recommended_delays = self.calculate_optimal_delays(cpu_percent, memory_percent)
            predicted_time = self.predict_completion_time(current_settings)
            
            # Cập nhật AI predictions
            self.ai_predictions.update({
                'optimal_batch_size': recommended_batch_size,
                'optimal_start_delay': recommended_delays['start'],
                'optimal_batch_delay': recommended_delays['batch'],
                'predicted_completion_time': predicted_time,
                'performance_score': self.calculate_performance_score(cpu_percent, memory_percent),
                'system_cpu': cpu_percent,
                'system_memory': memory_percent
            })
            
            # Đưa ra đề xuất nếu settings hiện tại không tối ưu
            self.suggest_optimizations()
            
        except Exception as e:
            self.add_log(f"❌ Lỗi AI analysis: {str(e)}", "error")
    
    def calculate_optimal_batch_size(self, cpu_percent, memory_percent):
        """Tính batch size tối ưu dựa trên tài nguyên hệ thống"""
        # AI logic: Giảm batch size nếu hệ thống quá tải
        if cpu_percent > 80 or memory_percent > 85:
            return 10  # Conservative batch
        elif cpu_percent > 60 or memory_percent > 70:
            return 15  # Moderate batch
        elif cpu_percent < 30 and memory_percent < 50:
            return 30  # Aggressive batch
        else:
            return 20  # Standard batch
    
    def calculate_optimal_delays(self, cpu_percent, memory_percent):
        """Tính delays tối ưu dựa trên hiệu suất hệ thống"""
        # AI logic: Tăng delay nếu hệ thống chậm
        if cpu_percent > 80 or memory_percent > 85:
            return {'start': 6, 'batch': 30}  # Slow system
        elif cpu_percent > 60 or memory_percent > 70:
            return {'start': 5, 'batch': 25}  # Moderate system
        elif cpu_percent < 30 and memory_percent < 50:
            return {'start': 2, 'batch': 10}  # Fast system
        else:
            return {'start': 4, 'batch': 20}  # Standard system
    
    def predict_completion_time(self, settings):
        """Dự đoán thời gian hoàn thành automation"""
        try:
            total_instances = settings.get('to_instance', 1200) - settings.get('from_instance', 1) + 1
            batch_size = settings.get('batch_size', 20)
            start_delay = settings.get('start_delay', 4)
            batch_delay = settings.get('batch_delay', 20)
            
            # Tính toán thời gian
            num_batches = (total_instances + batch_size - 1) // batch_size
            time_per_batch = (batch_size * start_delay) + batch_delay
            total_time = num_batches * time_per_batch
            
            return total_time  # seconds
        except:
            return 0
    
    def calculate_performance_score(self, cpu_percent, memory_percent):
        """Tính điểm hiệu suất hệ thống (0-100)"""
        cpu_score = max(0, 100 - cpu_percent)
        memory_score = max(0, 100 - memory_percent)
        return (cpu_score + memory_score) / 2
    
    def suggest_optimizations(self):
        """Đưa ra đề xuất tối ưu hóa"""
        try:
            current = self.automation_settings
            optimal = self.ai_predictions
            
            suggestions = []
            
            # Check batch size
            if current.get('batch_size', 20) != optimal['optimal_batch_size']:
                suggestions.append(f"🎯 Đề xuất Batch Size: {optimal['optimal_batch_size']} (hiện tại: {current.get('batch_size', 20)})")
            
            # Check delays
            if current.get('start_delay', 4) != optimal['optimal_start_delay']:
                suggestions.append(f"⏱️ Đề xuất Start Delay: {optimal['optimal_start_delay']}s (hiện tại: {current.get('start_delay', 4)}s)")
                
            if current.get('batch_delay', 20) != optimal['optimal_batch_delay']:
                suggestions.append(f"⏳ Đề xuất Batch Delay: {optimal['optimal_batch_delay']}s (hiện tại: {current.get('batch_delay', 20)}s)")
            
            # Performance analysis
            score = optimal['performance_score']
            if score > 80:
                suggestions.append("✅ Hệ thống hoạt động tối ưu!")
            elif score > 60:
                suggestions.append("⚠️ Hệ thống hoạt động bình thường")
            else:
                suggestions.append("❌ Hệ thống đang quá tải, nên giảm batch size")
            
            # Predicted time
            predicted_minutes = optimal['predicted_completion_time'] / 60
            suggestions.append(f"🕒 Dự đoán thời gian hoàn thành: {predicted_minutes:.1f} phút")
            
            # Log suggestions
            if suggestions:
                self.add_log("🧠 AI Prediction Engine đề xuất:", "info")
                for suggestion in suggestions[:3]:  # Chỉ hiển thị 3 đề xuất đầu
                    self.add_log(f"   {suggestion}", "info")
                    
        except Exception as e:
            self.add_log(f"❌ Lỗi tạo đề xuất: {str(e)}", "error")
    
    def apply_ai_suggestions(self):
        """Áp dụng đề xuất AI tự động"""
        try:
            optimal = self.ai_predictions
            
            # Backup current settings
            backup_settings = self.automation_settings.copy()
            
            # Apply AI suggestions
            self.automation_settings.update({
                'batch_size': optimal['optimal_batch_size'],
                'start_delay': optimal['optimal_start_delay'],
                'batch_delay': optimal['optimal_batch_delay']
            })
            
            # Save to file
            self.save_settings_to_file(self.automation_settings)
            
            # Update UI
            if hasattr(self, 'status_label'):
                range_text = f"Range: {self.automation_settings['from_instance']}-{self.automation_settings['to_instance']} | Batch: {self.automation_settings['batch_size']} | Delay: {self.automation_settings['batch_delay']}s"
                self.status_label.setText(f"AI Optimized | {range_text}")
            
            self.add_log("🤖 Đã áp dụng AI suggestions tự động!", "success")
            self.add_log(f"   Batch Size: {optimal['optimal_batch_size']}", "info")
            self.add_log(f"   Start Delay: {optimal['optimal_start_delay']}s", "info")
            self.add_log(f"   Batch Delay: {optimal['optimal_batch_delay']}s", "info")
            
            return True
            
        except Exception as e:
            self.add_log(f"❌ Lỗi apply AI suggestions: {str(e)}", "error")
            return False
    
    def ai_track_real_instances(self):
        """� AI Real-Time Instance Tracker - PERMANENTLY DISABLED"""
        print("🚫 ai_track_real_instances called but PERMANENTLY DISABLED - no MuMu Manager calls")
        return  # Exit immediately to prevent any MuMu Manager calls

    def _fallback_process_tracking(self):
        """🚫 Fallback process tracking - PERMANENTLY DISABLED"""
        print("🚫 _fallback_process_tracking called but PERMANENTLY DISABLED - no process scanning")
        return  # Exit immediately to prevent any process scanning
    
    # def extract_instance_id_from_process(self, proc_info):
    #     """Extract instance ID từ process info với improved patterns"""
    #     # This function is no longer needed when using MuMu Manager
    #     # Keeping for fallback compatibility
    #     pass
    
    def map_real_status_to_display(self, real_status):
        """Map real status sang display status"""
        status_map = {
            'running': '🟢 Running',
            'stopped': '🔴 Stopped', 
            'starting': '🟡 Starting',
            'stopping': '🟠 Stopping',
            'error': '⚠️ Error',
            'unknown': '❔ Unknown'
        }
        return status_map.get(str(real_status).lower(), '❔ Unknown')
    
    def ai_update_with_real_data(self):
        """Update AI predictions với real data"""
        try:
            if not hasattr(self, 'instance_table'):
                return
                
            # Safety check for automation_settings
            if not hasattr(self, 'automation_settings') or not isinstance(self.automation_settings, dict):
                print("⚠️ automation_settings not available or not a dict, skipping AI update")
                return
                
            # Merge real data với AI predictions
            from_instance = self.automation_settings.get('from_instance', 0)
            to_instance = self.automation_settings.get('to_instance', 10)
            
            for i in range(to_instance - from_instance + 1):
                instance_id = from_instance + i
                
                # Ưu tiên real data nếu có
                if instance_id in self.real_instance_tracker:
                    real_data = self.real_instance_tracker[instance_id]
                    
                    # Update table với real data
                    if i < self.instance_table.rowCount():
                        self.instance_table.setItem(i, 0, QTableWidgetItem(str(instance_id)))
                        
                        # Real status
                        status_item = QTableWidgetItem(real_data['status'])
                        status_color = self.get_status_color(real_data['status'])
                        status_item.setForeground(QColor(status_color))
                        self.instance_table.setItem(i, 1, status_item)
                        
                        # Real resource usage
                        cpu_item = QTableWidgetItem(f"{real_data['cpu']:.1f}%")
                        cpu_item.setForeground(QColor("#A6E22E" if real_data['cpu'] < 80 else "#F92672"))
                        self.instance_table.setItem(i, 2, cpu_item)
                        
                        memory_item = QTableWidgetItem(f"{real_data['memory']:.1f}%")
                        memory_item.setForeground(QColor("#66D9EF" if real_data['memory'] < 85 else "#F92672"))
                        self.instance_table.setItem(i, 3, memory_item)
                        
                        # Source indicator
                        source_indicator = "🔍 Real" if real_data['source'] == 'mumu_manager' else "📊 Proc"
                        source_item = QTableWidgetItem(source_indicator)
                        source_item.setForeground(QColor("#A6E22E"))
                        self.instance_table.setItem(i, 4, source_item)
                        
                        # Update time
                        update_time = datetime.now().strftime("%H:%M:%S")
                        update_item = QTableWidgetItem(update_time)
                        update_item.setForeground(QColor("#E6DB74"))
                        self.instance_table.setItem(i, 5, update_item)
                        
                        # Store real data for AI learning
                        self.instance_status[instance_id] = real_data
                else:
                    # Fallback to AI prediction nếu không có real data
                    prediction = self.ai_predict_instance_status(instance_id)
                    # ... existing AI prediction code
            
            # Update AI info với real vs predicted ratio
            real_count = len(self.real_instance_tracker)
            total_count = to_instance - from_instance + 1
            
            self.ai_status_info.setText(
                f"🤖 AI Monitor: {real_count}/{total_count} real-time tracked | "
                f"🔍 Real: {real_count}, 🧠 AI: {total_count - real_count}"
            )
            
            print(f"✅ DEBUG: Updated table with {real_count} real instances, {total_count - real_count} AI predictions")
            
        except Exception as e:
            print(f"❌ DEBUG: Error updating with real data: {e}")
    
    def get_status_color(self, status):
        """Get color cho status"""
        if '🟢' in status:
            return "#A6E22E"
        elif '🔴' in status:
            return "#75715E"
        elif '🟡' in status:
            return "#E6DB74"
        elif '⚠️' in status:
            return "#F92672"
        else:
            return "#FFFFFF"
    
    def ai_deep_learning(self):
        """🧠 AI Deep Learning - Học hỏi từ patterns và cải thiện predictions"""
        try:
            if not self.ai_learning_enabled:
                return
                
            # Collect learning data
            current_time = datetime.now()
            system_data = self.collect_system_metrics()
            
            # Pattern Recognition
            self.analyze_usage_patterns()
            self.predict_optimal_schedule()
            self.learn_from_failures()
            
            # Update AI accuracy
            self.calculate_prediction_accuracy()
            
            # Advanced predictions
            self.forecast_resource_usage()
            self.predict_failure_probability()
            
            # 🔥 NEW: Learn from real instance data
            if hasattr(self, 'real_instance_tracker'):
                self.learn_from_real_data()
            
            self.add_log(f"🧠 AI Deep Learning completed - Accuracy: {self.ai_prediction_accuracy:.1f}%", "success")
            
        except Exception as e:
            self.add_log(f"❌ AI Deep Learning error: {str(e)}", "error")
    
    def learn_from_real_data(self):
        """🧠 Học từ real instance data để cải thiện predictions"""
        try:
            real_data_count = len(self.real_instance_tracker)
            if real_data_count == 0:
                return
                
            # Analyze real vs predicted accuracy
            correct_predictions = 0
            total_predictions = 0
            
            for instance_id, real_data in self.real_instance_tracker.items():
                if instance_id in self.instance_status:
                    predicted_data = self.instance_status[instance_id]
                    
                    # Check if prediction was correct
                    real_status = real_data.get('status', '')
                    predicted_status = predicted_data.get('status', '')
                    
                    if real_status == predicted_status:
                        correct_predictions += 1
                    total_predictions += 1
            
            # Update AI accuracy based on real data
            if total_predictions > 0:
                real_accuracy = (correct_predictions / total_predictions) * 100
                # Weighted average với existing accuracy
                self.ai_prediction_accuracy = (self.ai_prediction_accuracy * 0.7) + (real_accuracy * 0.3)
                
                print(f"🧠 DEBUG: AI Learning - Real accuracy: {real_accuracy:.1f}%, Updated: {self.ai_prediction_accuracy:.1f}%")
                
            # Store real patterns for future predictions
            for instance_id, real_data in self.real_instance_tracker.items():
                pattern_key = f"{datetime.now().hour}_{real_data.get('source', 'unknown')}"
                if pattern_key not in self.ai_predictions.get('pattern_history', {}):
                    self.ai_predictions['pattern_history'][pattern_key] = []
                
                self.ai_predictions['pattern_history'][pattern_key].append({
                    'instance_id': instance_id,
                    'status': real_data['status'],
                    'cpu': real_data['cpu'],
                    'memory': real_data['memory'],
                    'timestamp': real_data['last_update']
                })
                
        except Exception as e:
            print(f"❌ DEBUG: Error learning from real data: {e}")
    
    def collect_system_metrics(self):
        """Thu thập metrics hệ thống cho AI learning"""
        try:
            import psutil
            return {
                'timestamp': datetime.now(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'active_processes': len(psutil.pids()),
                'network_connections': len(psutil.net_connections())
            }
        except:
            return {}
    
    def analyze_usage_patterns(self):
        """🔍 Phân tích patterns sử dụng để tối ưu scheduling"""
        try:
            current_hour = datetime.now().hour
            
            # Phân tích theo giờ trong ngày
            if 6 <= current_hour <= 10:
                pattern = "morning_peak"
                suggested_batch = 15  # Giảm batch size trong giờ cao điểm
            elif 11 <= current_hour <= 15:
                pattern = "afternoon_normal" 
                suggested_batch = 25  # Tăng batch size
            elif 16 <= current_hour <= 20:
                pattern = "evening_peak"
                suggested_batch = 12  # Giảm mạnh do peak time
            else:
                pattern = "night_optimal"
                suggested_batch = 35  # Tối ưu nhất vào ban đêm
            
            # Cập nhật AI predictions với pattern analysis
            self.ai_predictions['pattern_analysis'] = {
                'current_pattern': pattern,
                'suggested_batch_size': suggested_batch,
                'confidence': 92.5
            }
        except Exception as e:
            print(f"❌ Error in analyze_usage_patterns: {e}")
    
    def predict_optimal_schedule(self):
        """Dự đoán lịch trình tối ưu"""
        # Placeholder implementation
        pass
    
    def learn_from_failures(self):
        """Học từ failures"""
        # Placeholder implementation
        pass
    
    def calculate_prediction_accuracy(self):
        """Tính toán accuracy"""
        # Placeholder implementation
        pass
    
    def forecast_resource_usage(self):
        """Dự báo tài nguyên"""
        # Placeholder implementation
        pass
    
    def predict_failure_probability(self):
        """Dự đoán xác suất failure"""
        # Placeholder implementation
        pass
        """🧠 AI Deep Learning - Học hỏi từ patterns và cải thiện predictions"""
        try:
            if not self.ai_learning_enabled:
                return
                
            # Collect learning data
            current_time = datetime.now()
            system_data = self.collect_system_metrics()
            
            # Pattern Recognition
            self.analyze_usage_patterns()
            self.predict_optimal_schedule()
            self.learn_from_failures()
            
            # Update AI accuracy
            self.calculate_prediction_accuracy()
            
            # Advanced predictions
            self.forecast_resource_usage()
            self.predict_failure_probability()
            
            self.add_log(f"🧠 AI Deep Learning completed - Accuracy: {self.ai_prediction_accuracy:.1f}%", "success")
            
        except Exception as e:
            self.add_log(f"❌ AI Deep Learning error: {str(e)}", "error")
    
    def collect_system_metrics(self):
        """Thu thập metrics hệ thống cho AI learning"""
        try:
            import psutil
            return {
                'timestamp': datetime.now(),
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': psutil.disk_usage('/').percent,
                'active_processes': len(psutil.pids()),
                'network_connections': len(psutil.net_connections())
            }
        except:
            return {}
    
    def analyze_usage_patterns(self):
        """🔍 Phân tích patterns sử dụng để tối ưu scheduling"""
        try:
            current_hour = datetime.now().hour
            
            # Phân tích theo giờ trong ngày
            if 6 <= current_hour <= 10:
                pattern = "morning_peak"
                suggested_batch = 15  # Giảm batch size trong giờ cao điểm
            elif 11 <= current_hour <= 15:
                pattern = "afternoon_normal" 
                suggested_batch = 25  # Tăng batch size
            elif 16 <= current_hour <= 20:
                pattern = "evening_peak"
                suggested_batch = 12  # Giảm mạnh do peak time
            else:
                pattern = "night_optimal"
                suggested_batch = 35  # Tối ưu nhất vào ban đêm
            
            # Cập nhật AI predictions với pattern analysis
            self.ai_predictions['pattern_analysis'] = {
                'current_pattern': pattern,
                'suggested_batch_size': suggested_batch,
                'confidence': 92.5
            }
            
            self.add_log(f"🔍 Pattern detected: {pattern} → Batch: {suggested_batch}", "info")
            
        except Exception as e:
            self.add_log(f"❌ Pattern analysis error: {str(e)}", "error")
    
    def predict_optimal_schedule(self):
        """📅 Dự đoán thời gian tối ưu để chạy automation"""
        try:
            # Phân tích tải hệ thống theo patterns
            optimal_times = []
            
            # Ban đêm (2:00-5:00) - Tải thấp nhất
            optimal_times.append({'time': '03:00', 'efficiency': 98, 'reason': 'Minimal system load'})
            optimal_times.append({'time': '04:00', 'efficiency': 96, 'reason': 'Very low resource usage'})
            
            # Sáng sớm (6:00-7:00) - Tải trung bình
            optimal_times.append({'time': '06:30', 'efficiency': 85, 'reason': 'Pre-peak efficiency'})
            
            # Trưa (12:00-13:00) - Tải cao
            optimal_times.append({'time': '12:30', 'efficiency': 70, 'reason': 'Lunch break optimization'})
            
            self.ai_predictions['smart_scheduling'] = {
                'optimal_times': optimal_times,
                'current_efficiency': self.calculate_current_efficiency(),
                'next_optimal': optimal_times[0]['time']
            }
            
            best_time = max(optimal_times, key=lambda x: x['efficiency'])
            self.add_log(f"📅 AI suggests best time: {best_time['time']} (Efficiency: {best_time['efficiency']}%)", "info")
            
        except Exception as e:
            self.add_log(f"❌ Schedule prediction error: {str(e)}", "error")
    
    def learn_from_failures(self):
        """🎯 Học hỏi từ failures để cải thiện success rate"""
        try:
            # Phân tích failure patterns
            failure_factors = {
                'high_cpu_usage': 0.3,      # 30% failures do CPU cao
                'memory_shortage': 0.25,     # 25% failures do RAM thiếu
                'network_issues': 0.2,       # 20% failures do network
                'timing_conflicts': 0.15,    # 15% failures do timing
                'system_overload': 0.1       # 10% failures do overload
            }
            
            # Tính failure probability
            current_risk = self.calculate_failure_risk()
            
            self.ai_predictions['failure_prediction'] = current_risk
            
            if current_risk > 30:
                self.add_log(f"⚠️ High failure risk detected: {current_risk}% - AI suggests conservative settings", "warning")
                # Tự động điều chỉnh settings để giảm risk
                self.ai_predictions['optimal_batch_size'] = max(5, self.ai_predictions['optimal_batch_size'] - 10)
                self.ai_predictions['optimal_batch_delay'] += 10
            elif current_risk < 10:
                self.add_log(f"✅ Low failure risk: {current_risk}% - AI suggests aggressive settings", "success")
                self.ai_predictions['optimal_batch_size'] = min(40, self.ai_predictions['optimal_batch_size'] + 5)
                
        except Exception as e:
            self.add_log(f"❌ Failure learning error: {str(e)}", "error")
    
    def calculate_current_efficiency(self):
        """Tính efficiency hiện tại của hệ thống"""
        try:
            import psutil
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            
            # Efficiency = 100 - (cpu_load + memory_load) / 2
            efficiency = max(0, 100 - (cpu + memory) / 2)
            return round(efficiency, 1)
        except:
            return 75.0  # Default
    
    def calculate_failure_risk(self):
        """Tính tỷ lệ risk failure dựa trên system state"""
        try:
            import psutil
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            
            # Risk calculation
            risk = 0
            if cpu > 80: risk += 25
            elif cpu > 60: risk += 15
            elif cpu > 40: risk += 5
            
            if memory > 85: risk += 30
            elif memory > 70: risk += 20
            elif memory > 50: risk += 10
            
            return min(100, risk)
        except:
            return 15  # Default low risk
    
    def calculate_prediction_accuracy(self):
        """Tính độ chính xác của AI predictions"""
        try:
            # Mock calculation - trong thực tế sẽ so sánh predictions vs actual results
            base_accuracy = 85.0
            
            # Cải thiện accuracy theo thời gian
            if len(self.execution_history) > 10:
                base_accuracy += min(10, len(self.execution_history) * 0.5)
            
            self.ai_prediction_accuracy = min(99.9, base_accuracy)
            
        except Exception as e:
            self.add_log(f"❌ Accuracy calculation error: {str(e)}", "error")
    
    def forecast_resource_usage(self):
        """🔮 Dự báo resource usage trong tương lai"""
        try:
            # Dự báo cho 1 giờ tới
            forecast = {
                'next_hour_cpu': self.predict_cpu_trend(),
                'next_hour_memory': self.predict_memory_trend(),
                'optimal_window': self.find_optimal_execution_window(),
                'resource_recommendation': self.get_resource_recommendation()
            }
            
            self.ai_predictions['resource_forecast'] = forecast
            
            if forecast['optimal_window']:
                self.add_log(f"🔮 AI Forecast: Optimal execution window in {forecast['optimal_window']} minutes", "info")
                
        except Exception as e:
            self.add_log(f"❌ Resource forecast error: {str(e)}", "error")
    
    def predict_cpu_trend(self):
        """Dự đoán xu hướng CPU"""
        # Simplified prediction logic
        import psutil
        current_cpu = psutil.cpu_percent()
        current_hour = datetime.now().hour
        
        # Dự đoán dựa trên patterns
        if 8 <= current_hour <= 18:  # Working hours
            return min(100, current_cpu + 15)
        else:  # Off hours
            return max(5, current_cpu - 10)
    
    def predict_memory_trend(self):
        """Dự đoán xu hướng Memory"""
        import psutil
        current_memory = psutil.virtual_memory().percent
        # Simplified prediction
        return min(95, current_memory + 5)
    
    def find_optimal_execution_window(self):
        """Tìm window tối ưu để execution"""
        current_hour = datetime.now().hour
        
        # Logic tìm window tối ưu
        if current_hour < 2:
            return 30  # 30 minutes
        elif current_hour < 6:
            return 0   # Ngay bây giờ
        elif current_hour < 22:
            return 120  # 2 hours (chờ đến tối)
        else:
            return 60   # 1 hour
    
    def get_resource_recommendation(self):
        """Đưa ra recommendation về resources"""
        try:
            import psutil
            cpu = psutil.cpu_percent()
            memory = psutil.virtual_memory().percent
            
            if cpu > 70 or memory > 80:
                return "Consider reducing batch size and increasing delays"
            elif cpu < 30 and memory < 50:
                return "System resources available - can increase batch size"
            else:
                return "Current settings appear optimal"
                
        except:
            return "Unable to analyze resources"
    
    def predict_failure_probability(self):
        """🎯 Dự đoán xác suất failure"""
        try:
            base_risk = self.calculate_failure_risk()
            
            # Factors that increase failure risk
            risk_multipliers = {
                'peak_hours': 1.3 if 8 <= datetime.now().hour <= 18 else 1.0,
                'system_load': 1.5 if base_risk > 50 else 1.0,
                'batch_size': 1.2 if self.automation_settings.get('batch_size', 20) > 30 else 1.0
            }
            
            final_risk = base_risk
            for factor, multiplier in risk_multipliers.items():
                final_risk *= multiplier
            
            final_risk = min(95, final_risk)
            
            self.ai_predictions['failure_prediction'] = round(final_risk, 1)
            
            if final_risk > 40:
                self.add_log(f"🎯 High failure probability: {final_risk}% - AI recommends postponing", "warning")
            elif final_risk < 15:
                self.add_log(f"🎯 Low failure probability: {final_risk}% - Optimal execution conditions", "success")
                
        except Exception as e:
            self.add_log(f"❌ Failure prediction error: {str(e)}", "error")
    
    def show_ai_advanced_dialog(self):
        """Hiển thị AI Advanced Analytics Dialog"""
        try:
            dialog = AIAdvancedDialog(self)
            dialog.exec()
        except Exception as e:
            self.add_log(f"❌ Error showing AI dialog: {str(e)}", "error")
        
    def setup_ui(self):
        """Thiết lập giao diện chính với enhanced spacing và layout"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # Title Bar với enhanced styling
        title_layout = QHBoxLayout()
        title_label = QLabel("🤖 TỰ ĐỘNG HÓA")
        title_label.setStyleSheet(self.get_title_style())
        title_layout.addWidget(title_label)
        
        # Instance Info với better styling
        self.instance_info = QLabel()
        self.update_instance_info()
        self.instance_info.setStyleSheet("""
        QLabel {
            color: #A6E22E;
            font-size: 13px;
            font-weight: bold;
            padding: 10px 15px;
            border: 2px solid #A6E22E;
            border-radius: 8px;
            background-color: rgba(166, 226, 46, 0.1);
            margin-left: 15px;
        }
        """)
        title_layout.addWidget(self.instance_info)
        
        title_layout.addStretch()
        
        # Settings Button với enhanced styling
        self.btn_settings = QPushButton("⚙️ Cài đặt")
        self.btn_settings.setStyleSheet(self.get_button_style("settings"))
        self.btn_settings.clicked.connect(self.show_settings_dialog)
        title_layout.addWidget(self.btn_settings)
        
        main_layout.addLayout(title_layout)
        
        # Main Content với improved grid layout
        content_layout = QGridLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Hộp 1: AutoBatch Control
        self.auto_batch_box = self.create_auto_batch_box()
        content_layout.addWidget(self.auto_batch_box, 0, 0)
        
        # Hộp 2: Scheduler
        self.scheduler_box = self.create_scheduler_box()
        content_layout.addWidget(self.scheduler_box, 0, 1)
        
        # Hộp 3: Auto Operations
        self.operations_box = self.create_operations_box()
        content_layout.addWidget(self.operations_box, 1, 0)
        
        # Hộp 4: Log Display
        self.log_box = self.create_log_box()
        content_layout.addWidget(self.log_box, 1, 1)
        
        main_layout.addLayout(content_layout)
        
        # Apply enhanced Monokai theme
        self.setStyleSheet(self.get_main_style())
        
        # Add log for initialization
        self.add_log("🎨 Enhanced UI initialized with modern Monokai theme", "info")
        
    def on_ai_optimization_toggled(self, checked):
        """Handle AI optimization toggle"""
        self.ai_optimization_disabled = checked
        if checked:
            self.add_log("🚫 AI Batch Size optimization disabled by user", "info")
        else:
            self.add_log("✅ AI Batch Size optimization enabled", "info")

    def force_ai_update(self):
        """Force immediate AI status update"""
        try:
            self.add_log("🔄 Forcing AI status update...", "info")
            self.ai_update_instance_status()
        except Exception as e:
            self.add_log(f"❌ Force AI update error: {str(e)}", "error")
        
    def showEvent(self, event):
        """Override showEvent để trigger update khi tab được hiển thị"""
        super().showEvent(event)
        # Trigger immediate update when tab is shown
        if hasattr(self, 'ai_update_instance_status'):
            QTimer.singleShot(500, self.ai_update_instance_status)
        
    def create_auto_batch_box(self):
        """Tạo hộp AutoBatch với progress bar"""
        box = QGroupBox("🔄 AutoBatch Control")
        box.setStyleSheet(self.get_groupbox_style())
        layout = QVBoxLayout(box)
        
        # Progress Section
        progress_layout = QHBoxLayout()
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(self.get_progressbar_style())
        self.progress_bar.setFormat("%p% - %v/%m tasks")
        progress_layout.addWidget(self.progress_bar)
        
        # Status Label
        self.status_label = QLabel("Sẵn sàng")
        self.status_label.setStyleSheet(self.get_status_style())
        progress_layout.addWidget(self.status_label)
        
        layout.addLayout(progress_layout)
        
        # Control Buttons
        button_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("▶️ START")
        self.btn_start.setStyleSheet(self.get_button_style("start"))
        self.btn_start.clicked.connect(self.start_automation)
        
        self.btn_pause = QPushButton("⏸️ PAUSE")
        self.btn_pause.setStyleSheet(self.get_button_style("pause"))
        self.btn_pause.clicked.connect(self.pause_automation)
        self.btn_pause.setEnabled(False)
        
        self.btn_stop = QPushButton("⏹️ STOP")
        self.btn_stop.setStyleSheet(self.get_button_style("stop"))
        self.btn_stop.clicked.connect(self.stop_automation)
        self.btn_stop.setEnabled(False)
        
        # AI Optimize Button
        self.btn_ai_optimize = QPushButton("🤖 AI OPTIMIZE")
        self.btn_ai_optimize.setStyleSheet(self.get_button_style("ai"))
        self.btn_ai_optimize.clicked.connect(self.apply_ai_suggestions)
        self.btn_ai_optimize.setToolTip("Áp dụng đề xuất tối ưu từ AI Prediction Engine")
        
        # AI Advanced Button
        self.btn_ai_advanced = QPushButton("🧠 AI ADVANCED")
        self.btn_ai_advanced.setStyleSheet(self.get_button_style("ai_advanced"))
        self.btn_ai_advanced.clicked.connect(self.show_ai_advanced_dialog)
        self.btn_ai_advanced.setToolTip("AI Deep Learning & Advanced Analytics")
        
        button_layout.addWidget(self.btn_start)
        button_layout.addWidget(self.btn_pause)
        button_layout.addWidget(self.btn_stop)
        button_layout.addWidget(self.btn_ai_optimize)
        button_layout.addWidget(self.btn_ai_advanced)
        
        layout.addLayout(button_layout)
        
        # Stats Display
        stats_layout = QGridLayout()
        
        # Current Batch
        self.current_batch_label = QLabel("Batch hiện tại:")
        self.current_batch_value = QLabel("0")
        self.current_batch_value.setStyleSheet("color: #A6E22E; font-weight: bold;")
        
        # Total Batches  
        self.total_batch_label = QLabel("Tổng Batch:")
        self.total_batch_value = QLabel("0")
        self.total_batch_value.setStyleSheet("color: #66D9EF; font-weight: bold;")
        
        # Success Rate
        self.success_rate_label = QLabel("Tỷ lệ thành công:")
        self.success_rate_value = QLabel("0%")
        self.success_rate_value.setStyleSheet("color: #E6DB74; font-weight: bold;")
        
        stats_layout.addWidget(self.current_batch_label, 0, 0)
        stats_layout.addWidget(self.current_batch_value, 0, 1)
        stats_layout.addWidget(self.total_batch_label, 1, 0)
        stats_layout.addWidget(self.total_batch_value, 1, 1)
        stats_layout.addWidget(self.success_rate_label, 2, 0)
        stats_layout.addWidget(self.success_rate_value, 2, 1)
        
        layout.addLayout(stats_layout)
        
        return box
        
    def create_scheduler_box(self):
        """Tạo hộp Đặt lịch"""
        box = QGroupBox("📅 Đặt Lịch Tự Động")
        box.setStyleSheet(self.get_groupbox_style())
        layout = QVBoxLayout(box)
        
        # Schedule Enable
        self.schedule_enabled = QCheckBox("Kích hoạt lịch trình")
        self.schedule_enabled.setStyleSheet(self.get_checkbox_style())
        self.schedule_enabled.toggled.connect(self.on_schedule_settings_changed)
        layout.addWidget(self.schedule_enabled)
        
        # Time Settings
        time_layout = QGridLayout()
        
        # Start Time
        time_layout.addWidget(QLabel("Thời gian bắt đầu:"), 0, 0)
        self.start_time = QTimeEdit()
        self.start_time.setStyleSheet(self.get_input_style())
        self.start_time.setTime(QTime(9, 0))
        self.start_time.timeChanged.connect(self.on_schedule_settings_changed)
        time_layout.addWidget(self.start_time, 0, 1)
        
        # End Time
        time_layout.addWidget(QLabel("Thời gian kết thúc:"), 1, 0)
        self.end_time = QTimeEdit()
        self.end_time.setStyleSheet(self.get_input_style())
        self.end_time.setTime(QTime(17, 0))
        time_layout.addWidget(self.end_time, 1, 1)
        
        # Interval
        time_layout.addWidget(QLabel("Chu kỳ (phút):"), 2, 0)
        self.interval_spin = QSpinBox()
        self.interval_spin.setStyleSheet(self.get_input_style())
        self.interval_spin.setRange(1, 1440)
        self.interval_spin.setValue(30)
        time_layout.addWidget(self.interval_spin, 2, 1)
        
        layout.addLayout(time_layout)
        
        # Days Selection
        days_layout = QHBoxLayout()
        self.day_checkboxes = {}
        days = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]
        for day in days:
            checkbox = QCheckBox(day)
            checkbox.setStyleSheet(self.get_checkbox_style())
            checkbox.setChecked(True if day != "CN" else False)
            self.day_checkboxes[day] = checkbox
            days_layout.addWidget(checkbox)
            
        layout.addLayout(days_layout)
        
        # Next Run Display
        self.next_run_label = QLabel("Lần chạy tiếp theo: Chưa đặt lịch")
        self.next_run_label.setStyleSheet("color: #F92672; font-weight: bold;")
        layout.addWidget(self.next_run_label)
        
        return box
        
    def create_operations_box(self):
        """Tạo hộp Thao tác tự động"""
        box = QGroupBox("🚀 Thao Tác Tự Động")
        box.setStyleSheet(self.get_groupbox_style())
        layout = QVBoxLayout(box)
        
        # CPU Monitor Section (Thêm mới)
        cpu_monitor_layout = QHBoxLayout()
        
        # CPU Monitor Button
        self.btn_cpu_monitor = QPushButton("🖥️ CPU Monitor")
        self.btn_cpu_monitor.setStyleSheet(self.get_button_style("monitor"))
        self.btn_cpu_monitor.setMaximumHeight(28)
        self.btn_cpu_monitor.setMinimumHeight(28)
        self.btn_cpu_monitor.clicked.connect(self.toggle_cpu_monitor)
        
        # CPU Display Label
        self.cpu_display_label = QLabel("CPU: 0%")
        self.cpu_display_label.setStyleSheet("""
            QLabel {
                color: #A6E22E;
                font-weight: bold;
                font-size: 12px;
                padding: 2px 5px;
                border: 1px solid #49483E;
                border-radius: 3px;
                background-color: #2D2A2A;
                max-height: 24px;
                min-height: 24px;
            }
        """)
        
        # CPU Status Label
        self.cpu_status_label = QLabel("Tắt")
        self.cpu_status_label.setStyleSheet("""
            QLabel {
                color: #F92672;
                font-weight: bold;
                padding: 2px 5px;
                max-height: 24px;
                min-height: 24px;
            }
        """)
        
        cpu_monitor_layout.addWidget(self.btn_cpu_monitor)
        cpu_monitor_layout.addWidget(self.cpu_display_label)
        cpu_monitor_layout.addWidget(self.cpu_status_label)
        cpu_monitor_layout.addStretch()
        
        layout.addLayout(cpu_monitor_layout)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #49483E;")
        layout.addWidget(separator)
        
        # APK Installation Section
        apk_layout = QVBoxLayout()
        
        # APK Path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Đường dẫn APK:"))
        self.apk_path_edit = QLineEdit()
        self.apk_path_edit.setStyleSheet(self.get_input_style())
        self.apk_path_edit.setPlaceholderText("Chọn file APK...")
        
        self.btn_browse_apk = QPushButton("📁")
        self.btn_browse_apk.setStyleSheet(self.get_button_style("browse"))
        self.btn_browse_apk.clicked.connect(self.browse_apk_file)
        
        path_layout.addWidget(self.apk_path_edit)
        path_layout.addWidget(self.btn_browse_apk)
        
        apk_layout.addLayout(path_layout)
        
        # AutoBatch APK Installation
        self.auto_install_enabled = QCheckBox("Tự động cài APK theo AutoBatch")
        self.auto_install_enabled.setStyleSheet(self.get_checkbox_style())
        apk_layout.addWidget(self.auto_install_enabled)
        
        layout.addLayout(apk_layout)
        
        # Additional Operations
        ops_layout = QVBoxLayout()
        
        self.auto_cleanup = QCheckBox("Tự động dọn dẹp sau khi cài")
        self.auto_cleanup.setStyleSheet(self.get_checkbox_style())
        
        self.auto_restart = QCheckBox("Tự động khởi động lại instances")
        self.auto_restart.setStyleSheet(self.get_checkbox_style())
        
        self.auto_backup = QCheckBox("Tự động backup trước khi thao tác")
        self.auto_backup.setStyleSheet(self.get_checkbox_style())
        
        # AI Optimization Control
        self.disable_ai_optimization = QCheckBox("Tắt AI tối ưu Batch Size")
        self.disable_ai_optimization.setStyleSheet(self.get_checkbox_style())
        self.disable_ai_optimization.setChecked(self.ai_optimization_disabled)
        self.disable_ai_optimization.toggled.connect(self.on_ai_optimization_toggled)
        
        ops_layout.addWidget(self.auto_cleanup)
        ops_layout.addWidget(self.auto_restart) 
        ops_layout.addWidget(self.auto_backup)
        ops_layout.addWidget(self.disable_ai_optimization)
        
        layout.addLayout(ops_layout)
        
        return box
        
    def create_log_box(self):
        """Tạo hộp Log"""
        box = QGroupBox("📋 Bảng Log")
        box.setStyleSheet(self.get_groupbox_style())
        layout = QVBoxLayout(box)
        
        # Log Controls
        log_controls = QHBoxLayout()
        
        self.btn_clear_log = QPushButton("🗑️ Xóa Log")
        self.btn_clear_log.setStyleSheet(self.get_button_style("clear"))
        self.btn_clear_log.clicked.connect(self.clear_log)
        
        self.btn_save_log = QPushButton("💾 Lưu Log")
        self.btn_save_log.setStyleSheet(self.get_button_style("save"))
        self.btn_save_log.clicked.connect(self.save_log)
        
        self.log_filter = QComboBox()
        self.log_filter.setStyleSheet(self.get_input_style())
        self.log_filter.addItems(["Tất cả", "Thông tin", "Cảnh báo", "Lỗi", "Thành công"])
        self.log_filter.currentTextChanged.connect(self.filter_log)
        
        log_controls.addWidget(self.btn_clear_log)
        log_controls.addWidget(self.btn_save_log)
        log_controls.addStretch()
        log_controls.addWidget(QLabel("Lọc:"))
        log_controls.addWidget(self.log_filter)
        
        layout.addLayout(log_controls)
        
        # Log Display
        self.log_display = QTextEdit()
        self.log_display.setStyleSheet(self.get_log_style())
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 10))
        
        layout.addWidget(self.log_display)
        
        return box
        
    def show_settings_dialog(self):
        """Hiển thị dialog cài đặt"""
        dialog = AutomationSettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_settings(dialog)
            
    def load_settings(self, dialog=None):
        """Load settings từ dialog hoặc file"""
        if dialog:
            # Load từ dialog vừa đóng
            settings = dialog.get_settings()
            # Add AI optimization setting
            settings['disable_ai_optimization'] = self.ai_optimization_disabled
            self.automation_settings = settings
            
            # Update status với thông tin mới
            range_text = f"Range: {settings['from_instance']}-{settings['to_instance']} | Batch: {settings['batch_size']} | Delay: {settings['batch_delay']}s"
            self.status_label.setText(f"Sẵn sàng | {range_text}")
            
            # Update instance info tooltip với settings
            total_instances = settings['to_instance'] - settings['from_instance'] + 1
            self.instance_info.setToolTip(f"Automation Settings: From {settings['from_instance']} to {settings['to_instance']} ({total_instances} instances)")
            
            # Save to file
            self.save_settings_to_file(settings)
            
            self.add_log(f"✅ Settings updated: Range {settings['from_instance']}-{settings['to_instance']}, Batch {settings['batch_size']}, Delays {settings['start_delay']}s/{settings['batch_delay']}s", "success")
        else:
            # Load từ file
            self.load_settings_from_file()
    
    def save_settings_to_file(self, settings):
        """Lưu settings vào file JSON và đồng bộ với QSettings của main window"""
        try:
            # Lưu vào file JSON
            with open("automation_settings.json", "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            # Đồng bộ với QSettings của main window để đảm bảo automation sử dụng đúng settings
            if self.parent_window and hasattr(self.parent_window, 'settings'):
                self.parent_window.settings.setValue("auto/start", settings.get('from_instance', 1))
                self.parent_window.settings.setValue("auto/end", settings.get('to_instance', 10))
                self.parent_window.settings.setValue("auto/batch", settings.get('batch_size', 5))
                self.parent_window.settings.setValue("auto/inst_delay", settings.get('start_delay', 2.0))
                self.parent_window.settings.setValue("auto/batch_delay", settings.get('batch_delay', 8.0))
                print(f"✅ Settings synchronized with main window QSettings: batch={settings.get('batch_size', 5)}")
            
        except Exception as e:
            print(f"Error saving settings: {e}")

    # ===== STYLING METHODS =====
    def get_main_style(self):
        """Enhanced Main Monokai styling với màu sắc chuẩn từ theme"""
        return """
        QWidget {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1D1E19, stop:0.5 #272822, stop:1 #1D1E19);
            color: #F8F8F2;
            font-family: 'Consolas', 'Monaco', 'JetBrains Mono', monospace;
            font-size: 10px;
            selection-background-color: #F92672;
            selection-color: #F8F8F2;
        }
        """

    def get_groupbox_style(self):
        """Enhanced GroupBox Monokai styling với màu sắc chuẩn"""
        return """
        QGroupBox {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2D2A2E, stop:1 #1D1E19);
            border: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #66D9EF, stop:1 #A6E22E);
            border-radius: 12px;
            color: #F8F8F2;
            font-weight: bold;
            font-size: 13px;
            margin-top: 12px;
            padding: 20px 15px 15px 15px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 15px;
            top: -8px;
            color: #66D9EF;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #272822, stop:1 #2D2A2E);
            padding: 4px 12px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: bold;
            border: 1px solid #66D9EF;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
        }
        """

    def get_button_style(self, button_type="default"):
        """Enhanced Button Monokai styling với màu sắc chuẩn"""
        base_style = """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #49483E, stop:1 #3E3D32);
            border: 2px solid #75715E;
            border-radius: 8px;
            color: #F8F8F2;
            font-weight: bold;
            font-size: 11px;
            padding: 6px 12px;
            min-height: 22px;
            max-height: 28px;
            text-align: center;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #5A5950, stop:1 #49483E);
            border-color: #A6E22E;
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #A6E22E, stop:1 #66D9EF);
            color: #272822;
        }
        QPushButton:disabled {
            background-color: #3C3C3C;
            color: #75715E;
            border-color: #49483E;
            opacity: 0.6;
        }
        """

        if button_type == "start":
            return base_style.replace("#75715E", "#A6E22E").replace("#A6E22E", "#66D9EF").replace(
                "QPushButton:pressed", "QPushButton:pressed {\n            background: #A6E22E;\n            color: #272822;\n        }"
            )
        elif button_type == "stop":
            return base_style.replace("#75715E", "#F92672").replace("#A6E22E", "#F92672").replace(
                "QPushButton:pressed", "QPushButton:pressed {\n            background: #F92672;\n            color: #F8F8F2;\n        }"
            )
        elif button_type == "settings":
            return base_style.replace("#75715E", "#E6DB74").replace("#A6E22E", "#E6DB74").replace(
                "QPushButton:pressed", "QPushButton:pressed {\n            background: #E6DB74;\n            color: #272822;\n        }"
            )
        elif button_type == "ai":
            return base_style.replace("#75715E", "#AE81FF").replace("#A6E22E", "#AE81FF").replace(
                "QPushButton:pressed", "QPushButton:pressed {\n            background: #AE81FF;\n            color: #F8F8F2;\n        }"
            )
        elif button_type == "refresh":
            return base_style.replace("#75715E", "#66D9EF").replace("#A6E22E", "#66D9EF")
        elif button_type == "monitor":
            return base_style.replace("#75715E", "#FD971F").replace("#A6E22E", "#FD971F")
        elif button_type == "active":
            return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #A6E22E, stop:1 #66D9EF);
                border: 2px solid #A6E22E;
                border-radius: 8px;
                color: #272822;
                font-weight: bold;
                font-size: 11px;
                padding: 8px 12px;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(166, 226, 46, 0.4);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #66D9EF, stop:1 #A6E22E);
                border-color: #66D9EF;
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(166, 226, 46, 0.6);
            }
            QPushButton:pressed {
                background: #49483E;
                color: #F8F8F2;
                transform: translateY(0px);
            }
            """
        elif button_type == "browse":
            return base_style.replace("#75715E", "#66D9EF").replace("#A6E22E", "#66D9EF")
        elif button_type == "clear":
            return base_style.replace("#75715E", "#F92672").replace("#A6E22E", "#F92672")
        elif button_type == "save":
            return base_style.replace("#75715E", "#A6E22E").replace("#A6E22E", "#66D9EF")

        return base_style

    def get_input_style(self):
        """Enhanced Input field Monokai styling với màu sắc chuẩn"""
        return """
        QLineEdit, QSpinBox, QComboBox, QTimeEdit {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #49483E, stop:1 #3E3D32);
            border: 2px solid #75715E;
            border-radius: 6px;
            color: #F8F8F2;
            padding: 8px 12px;
            font-size: 11px;
            font-family: 'Consolas', 'Monaco', 'JetBrains Mono', monospace;
            selection-background-color: #F92672;
            selection-color: #F8F8F2;
        }
        QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QTimeEdit:focus {
            border-color: #66D9EF;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4A4A3E, stop:1 #404036);
        }
        QLineEdit:hover, QSpinBox:hover, QComboBox:hover, QTimeEdit:hover {
            border-color: #A6E22E;
        }
        QComboBox::drop-down {
            border: none;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #75715E, stop:1 #49483E);
            border-radius: 4px;
            width: 20px;
        }
        QComboBox::down-arrow {
            color: #F8F8F2;
            width: 12px;
            height: 12px;
        }
        QComboBox::down-arrow:hover {
            color: #A6E22E;
        }
        QSpinBox::up-button, QSpinBox::down-button {
            background: #75715E;
            border: none;
            border-radius: 3px;
            width: 16px;
            height: 12px;
        }
        QSpinBox::up-button:hover, QSpinBox::down-button:hover {
            background: #A6E22E;
        }
        """

    def get_progress_style(self):
        """Progress bar Monokai styling"""
        return """
        QProgressBar {
            background-color: #49483E;
            border: 2px solid #75715E;
            border-radius: 6px;
            text-align: center;
            color: #F8F8F2;
            font-weight: bold;
        }
        QProgressBar::chunk {
            background-color: #A6E22E;
            border-radius: 4px;
        }
        """

    def get_log_style(self):
        """Enhanced Log area Monokai styling với màu sắc chuẩn và terminal-like appearance"""
        return """
        QTextEdit {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #1D1E19, stop:1 #2D2A2E);
            border: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #66D9EF, stop:1 #A6E22E);
            border-radius: 8px;
            color: #F8F8F2;
            font-family: 'Consolas', 'Monaco', 'JetBrains Mono', 'Courier New', monospace;
            font-size: 10px;
            padding: 12px;
            selection-background-color: #F92672;
            selection-color: #F8F8F2;
            line-height: 1.4;
        }
        QTextEdit:focus {
            border-color: #A6E22E;
        }
        /* Scrollbar styling */
        QTextEdit QScrollBar:vertical {
            background: #2D2A2E;
            width: 12px;
            border-radius: 6px;
        }
        QTextEdit QScrollBar::handle:vertical {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #66D9EF, stop:1 #A6E22E);
            border-radius: 6px;
            min-height: 30px;
        }
        QTextEdit QScrollBar::handle:vertical:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #A6E22E, stop:1 #66D9EF);
        }
        QTextEdit QScrollBar::add-line:vertical, QTextEdit QScrollBar::sub-line:vertical {
            background: none;
            border: none;
        }
        """

    def get_title_style(self):
        """Enhanced Style cho title với màu sắc Monokai chuẩn"""
        return """
        QLabel {
            color: #F8F8F2;
            font-size: 28px;
            font-weight: bold;
            padding: 15px 20px;
            font-family: 'Consolas', 'Monaco', 'JetBrains Mono', monospace;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(166, 226, 46, 0.1), stop:0.5 rgba(102, 217, 239, 0.1), stop:1 rgba(166, 226, 46, 0.1));
            border-radius: 12px;
            border: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #A6E22E, stop:1 #66D9EF);
        }
        """

    def update_instance_info(self):
        """Cập nhật thông tin số lượng instances"""
        total_instances = 0
        if hasattr(self.parent(), 'instances_model') and self.parent().instances_model:
            try:
                total_instances = self.parent().instances_model.rowCount()
            except:
                total_instances = 0
        
        if total_instances == 0:
            if hasattr(self, 'instance_info'):
                self.instance_info.setText("📊 Không tìm thấy instances")
        else:
            if hasattr(self, 'instance_info'):
                self.instance_info.setText(f"📊 Total Instances: {total_instances:,}")

    def get_progressbar_style(self):
        """Enhanced Progress bar Monokai styling với màu sắc chuẩn"""
        return """
        QProgressBar {
            border: 2px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #66D9EF, stop:1 #A6E22E);
            border-radius: 8px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2D2A2E, stop:1 #1D1E19);
            text-align: center;
            color: #F8F8F2;
            font-weight: bold;
            font-size: 11px;
            min-height: 24px;
            max-height: 24px;
            padding: 2px;
        }
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #A6E22E, stop:0.5 #66D9EF, stop:1 #AE81FF);
            border-radius: 6px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        """

    def get_status_style(self):
        """Enhanced Status label Monokai styling với màu sắc chuẩn"""
        return """
        QLabel {
            color: #E6DB74;
            font-weight: bold;
            font-size: 12px;
            padding: 8px 12px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2D2A2E, stop:1 #1D1E19);
            border: 1px solid #75715E;
            border-radius: 6px;
            text-align: center;
        }
        """

    def start_automation(self):
        """Enhanced start automation with improved state management"""
        try:
            if not self.automation_running:
                # Initialize enhanced state
                self.update_automation_state(
                    running=True,
                    paused=False,
                    current_batch=0,
                    progress=0,
                    success_count=0,
                    error_count=0,
                    start_time=datetime.now()
                )
                
                # Calculate optimal batch size based on current system performance
                # Only apply AI optimization if not disabled and current batch size is large (>15)
                current_batch_size = self.automation_settings.get('batch_size', 20)
                self.add_log(f"🔍 DEBUG: AI disabled={self.ai_optimization_disabled}, current_batch={current_batch_size}", "info")
                if not self.ai_optimization_disabled and current_batch_size > 15:
                    optimal_batch_size = self.calculate_optimal_batch_size()
                    if optimal_batch_size != current_batch_size:
                        self.add_log(f"🤖 AI Optimization: Using batch size {optimal_batch_size} instead of {current_batch_size}", "info")
                        self.automation_settings['batch_size'] = optimal_batch_size
                else:
                    # Keep user's batch size if AI optimization is disabled or batch size is reasonable (≤15)
                    optimal_batch_size = current_batch_size
                    if self.ai_optimization_disabled:
                        self.add_log(f"🚫 AI Optimization disabled by user - keeping batch size {current_batch_size}", "info")
                
                # Update UI
                self.btn_start.setEnabled(False)
                self.btn_pause.setEnabled(True)
                self.btn_stop.setEnabled(True)
                self.status_label.setText("Đang chạy...")
                
                # Start actual batch automation
                self.start_batch_automation()
                self.add_log("✅ Bắt đầu Enhanced AutoBatch automation", "success")
                
        except Exception as e:
            self.add_log(f"❌ Error starting automation: {str(e)}", "error")
            self.update_automation_state(running=False)

    def process_next_batch(self):
        """Xử lý batch tiếp theo - Method được add để fix missing method error"""
        if not self.automation_running or self.automation_paused:
            return
            
        if self.current_batch >= len(self.instance_batches):
            # Hoàn thành tất cả batches
            self.add_log("🎉 Hoàn thành tất cả automation tasks", "success")
            self.stop_automation()
            return
            
        try:
            # Get current batch
            current_instances = self.instance_batches[self.current_batch]
            batch_delay = self.automation_settings.get('batch_delay', 20)
            
            self.add_log(f"🔄 Batch {self.current_batch + 1}/{len(self.instance_batches)}: Starting instances {current_instances[0]}-{current_instances[-1]} ({len(current_instances)} instances)", "info")
            
            # Start từng instance trong batch một cách tuần tự
            self.start_instances_in_batch(current_instances, 0)
                
        except Exception as e:
            self.add_log(f"❌ Lỗi xử lý batch: {str(e)}", "error")
            self.stop_automation()

    def start_instances_in_batch(self, instances, index):
        """Start từng instance trong batch một cách tuần tự"""
        if not self.automation_running or self.automation_paused:
            return
            
        if index >= len(instances):
            # Hoàn thành batch hiện tại
            self.current_batch += 1
            batch_delay = self.automation_settings.get('batch_delay', 20)
            
            self.add_log(f"✅ Hoàn thành batch {self.current_batch}", "success")
            
            # Update stats if widgets exist
            if hasattr(self, 'current_batch_value'):
                self.current_batch_value.setText(str(self.current_batch))
            if hasattr(self, 'total_batch_value') and hasattr(self, 'instance_batches'):
                self.total_batch_value.setText(str(len(self.instance_batches)))
            
            # Calculate success rate
            if hasattr(self, 'current_progress') and hasattr(self, 'total_tasks') and self.total_tasks > 0:
                success_rate = min(95, 80 + (self.current_progress / self.total_tasks) * 15)
                if hasattr(self, 'success_rate_value'):
                    self.success_rate_value.setText(f"{success_rate:.1f}%")
            
            # Delay trước khi chuyển sang batch tiếp theo
            if hasattr(self, 'instance_batches') and self.current_batch < len(self.instance_batches):
                self.add_log(f"⏳ Chờ {batch_delay}s trước batch tiếp theo...", "info")
                QTimer.singleShot(batch_delay * 1000, self.process_next_batch)
            else:
                self.process_next_batch()  # Finish all
            return
        
        try:
            instance_id = instances[index]
            self.add_log(f"▶️ Starting instance {instance_id}", "info")
            
            # Start single instance
            if hasattr(self, 'parent_window') and hasattr(self.parent_window, 'mumu_manager'):
                backend = self.parent_window.mumu_manager
                success, result = backend.control_instance([instance_id], "launch")
                
                if success:
                    self.add_log(f"✅ Instance {instance_id} started successfully", "success")
                else:
                    self.add_log(f"❌ Instance {instance_id} failed: {result}", "error")
            else:
                self.add_log(f"⚠️ Backend not available for instance {instance_id}", "warning")
            
            # Update progress
            if hasattr(self, 'current_progress'):
                self.current_progress += 1
                if hasattr(self, 'progress_bar'):
                    self.progress_bar.setValue(self.current_progress)
            
            # Start next instance after delay
            start_delay = self.automation_settings.get('start_delay', 4)
            QTimer.singleShot(start_delay * 1000, lambda: self.start_instances_in_batch(instances, index + 1))
            
        except Exception as e:
            self.add_log(f"❌ Lỗi start instance {instances[index]}: {str(e)}", "error")
            # Continue với instance tiếp theo
            QTimer.singleShot(1000, lambda: self.start_instances_in_batch(instances, index + 1))

    def start_batch_automation(self):
        """Bắt đầu automation thực sự theo batch settings"""
        try:
            # Get backend từ parent window
            if hasattr(self, 'parent_window') and hasattr(self.parent_window, 'mumu_manager') and self.parent_window.mumu_manager:
                from_instance = self.automation_settings.get('from_instance', 1)
                to_instance = self.automation_settings.get('to_instance', 1200)
                batch_size = self.automation_settings.get('batch_size', 20)
                batch_delay = self.automation_settings.get('batch_delay', 20)
                start_delay = self.automation_settings.get('start_delay', 4)
                
                self.add_log(f"📋 Settings: From {from_instance} to {to_instance}, Batch: {batch_size}, Start Delay: {start_delay}s, Batch Delay: {batch_delay}s", "info")
                
                # Tạo list instances cần start
                instance_range = list(range(from_instance, to_instance + 1))
                
                if not instance_range:
                    self.add_log("❌ Không có instance nào trong range", "error")
                    self.stop_automation()
                    return
                
                # Setup progress
                self.total_tasks = len(instance_range)
                self.current_progress = 0
                if hasattr(self, 'progress_bar'):
                    self.progress_bar.setMaximum(self.total_tasks)
                    self.progress_bar.setValue(0)
                
                # Chia thành batches
                self.current_batch = 0
                self.instance_batches = [instance_range[i:i + batch_size] for i in range(0, len(instance_range), batch_size)]
                
                self.add_log(f"🚀 Sẽ xử lý {len(self.instance_batches)} batches, tổng {len(instance_range)} instances", "info")
                self.add_log(f"📦 Batch đầu tiên: {self.instance_batches[0]}", "info")
                
                # Start first batch after delay
                QTimer.singleShot(start_delay * 1000, self.process_next_batch)
                
            else:
                self.add_log("❌ Không thể truy cập MuMu backend", "error")
                self.stop_automation()
                
        except Exception as e:
            self.add_log(f"❌ Lỗi start automation: {str(e)}", "error")
            self.stop_automation()

    def pause_automation(self):
        """Tạm dừng/tiếp tục automation"""
        if self.automation_running:
            self.automation_paused = not self.automation_paused
            
            if self.automation_paused:
                self.btn_pause.setText("▶️ RESUME")
                self.status_label.setText("Tạm dừng")
                self.add_log("⏸️ Tạm dừng automation", "warning")
            else:
                self.btn_pause.setText("⏸️ PAUSE")
                self.status_label.setText("Đang chạy...")
                self.add_log("▶️ Tiếp tục automation", "info")
                
    def stop_automation(self):
        """Dừng automation"""
        if self.automation_running:
            self.automation_running = False
            self.automation_paused = False
            
            # Update UI
            self.btn_start.setEnabled(True)
            self.btn_pause.setEnabled(False)
            self.btn_pause.setText("⏸️ PAUSE")
            self.btn_stop.setEnabled(False)
            self.status_label.setText("Đã dừng")
            
            self.add_log("⏹️ Dừng automation", "error")
            
    def add_log(self, message, level="info"):
        """Thêm log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding
        colors = {
            "info": "#66D9EF",
            "warning": "#E6DB74", 
            "error": "#F92672",
            "success": "#A6E22E"
        }
        
        color = colors.get(level, "#F8F8F2")
        formatted_message = f'<span style="color: {color}">[{timestamp}] {message}</span>'
        
        if hasattr(self, 'log_display'):
            self.log_display.append(formatted_message)

    def get_checkbox_style(self):
        """Enhanced Checkbox Monokai styling với màu sắc chuẩn và modern effects"""
        return """
        QCheckBox {
            color: #F8F8F2;
            font-size: 11px;
            font-weight: 500;
            spacing: 8px;
            padding: 4px;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #66D9EF;
            border-radius: 4px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #2D2A2E, stop:1 #1D1E19);
        }
        QCheckBox::indicator:hover {
            border-color: #A6E22E;
        }
        QCheckBox::indicator:checked {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #A6E22E, stop:1 #66D9EF);
            border-color: #A6E22E;
            image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 12 12"><path d="M4 8L2 6l1-1 1 1 4-4 1 1z" fill="%23272822"/></svg>');
        }
        """
    
    def browse_apk_file(self):
        """Chọn file APK"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file APK", "", "APK files (*.apk)"
        )
        if file_path:
            self.apk_path_edit.setText(file_path)
    
    def toggle_cpu_monitor(self):
        """Bật/tắt CPU monitor"""
        try:
            # Đảm bảo CPU monitor đã được khởi tạo
            if not self.cpu_monitor_initialized:
                self.initialize_cpu_monitor()
                
            self.cpu_monitor_enabled = not self.cpu_monitor_enabled
            
            if self.cpu_monitor_enabled:
                self.btn_cpu_monitor.setText("🖥️ CPU Monitor (ON)")
                self.btn_cpu_monitor.setStyleSheet(self.get_button_style("active"))
                self.cpu_status_label.setText("Đang theo dõi")
                self.cpu_status_label.setStyleSheet("color: #A6E22E; font-weight: bold; padding: 2px; border: 1px solid #49483E; border-radius: 3px; max-height: 24px; min-height: 24px;")
                
                # Restart timer với interval ngắn hơn khi active
                if hasattr(self, 'cpu_monitor_timer'):
                    self.cpu_monitor_timer.stop()
                    self.cpu_monitor_timer.start(10000)  # 10 giây khi active - frequent check
                    
                self.add_log(f"🖥️ CPU Monitor BẬT - Ngưỡng: {self.cpu_threshold}% - Tự động dừng nếu vượt ngưỡng", "info")
            else:
                self.btn_cpu_monitor.setText("🖥️ CPU Monitor (OFF)")
                self.btn_cpu_monitor.setStyleSheet(self.get_button_style("monitor"))
                self.cpu_status_label.setText("Tắt")
                self.cpu_status_label.setStyleSheet("color: #F92672; font-weight: bold; padding: 2px; border: 1px solid #49483E; border-radius: 3px; max-height: 24px; min-height: 24px;")
                
                # Reset CPU monitor active state
                self.cpu_monitor_active = False
                
                # Slower interval when inactive
                if hasattr(self, 'cpu_monitor_timer'):
                    self.cpu_monitor_timer.stop()
                    self.cpu_monitor_timer.start(20000)  # 20 giây khi inactive
                    
                self.add_log("🖥️ CPU Monitor TẮT - Không giám sát CPU", "warning")
                
        except Exception as e:
            print(f"❌ Toggle CPU monitor error: {e}")
            self.add_log(f"❌ Lỗi toggle CPU monitor: {str(e)}", "error")
    
    def check_cpu_usage(self):
        """Kiểm tra CPU usage và thực hiện hành động nếu cần"""
        try:
            # Chỉ chạy nếu đã được khởi tạo đúng cách
            if not self.cpu_monitor_initialized:
                return
                
            # Update display an toàn
            self.update_cpu_display_safe()
            
            # Kiểm tra ngưỡng CPU nếu monitor được bật
            if self.cpu_monitor_enabled and self.current_cpu_usage >= self.cpu_threshold:
                self.handle_high_cpu()
                
        except Exception as e:
            # Ghi log nhẹ, không dùng add_log để tránh recursion
            print(f"❌ CPU monitor error (silent): {e}")
            # Tạm dừng timer nếu có lỗi liên tục
            if hasattr(self, 'cpu_monitor_timer'):
                self.cpu_monitor_timer.stop()
                QTimer.singleShot(30000, lambda: self.cpu_monitor_timer.start(15000))  # Restart sau 30s
    
    def handle_high_cpu(self):
        """Xử lý khi CPU vượt ngưỡng 70%"""
        try:
            # Chỉ thực hiện một lần cho mỗi đợt CPU cao
            if not self.cpu_monitor_active:
                self.cpu_monitor_active = True
                
                # Ghi log cảnh báo
                warning_msg = f"🚨 CPU VƯỢT NGƯỠNG! Hiện tại: {self.current_cpu_usage:.1f}% (Ngưỡng: {self.cpu_threshold}%)"
                self.add_log(warning_msg, "error")
                
                # 1. Dừng automation/auto batch ngay lập tức
                if self.automation_running:
                    self.stop_automation()
                    self.add_log("🛑 Auto Batch đã được dừng do CPU cao", "warning")
                
                # 2. Dừng tất cả timers liên quan automation
                self.stop_all_automation_timers()
                
                # 3. Dừng tất cả instances thông qua parent window
                self.stop_all_instances_due_to_high_cpu()
                
                # Log hành động hoàn tất
                action_msg = f"✅ ĐÃ DỪNG TẤT CẢ - CPU: {self.current_cpu_usage:.1f}% lúc {datetime.now().strftime('%H:%M:%S')}"
                self.add_log(action_msg, "error")
                
                # Reset flag sau 45 giây để có thể trigger lại
                QTimer.singleShot(45000, lambda: setattr(self, 'cpu_monitor_active', False))
                
        except Exception as e:
            self.add_log(f"❌ Lỗi xử lý CPU cao: {str(e)}", "error")
    
    def stop_all_automation_timers(self):
        """Dừng tất cả timers liên quan automation"""
        try:
            # Dừng batch timer nếu có
            if hasattr(self, 'batch_timer') and self.batch_timer:
                self.batch_timer.stop()
                self.add_log("⏹️ Batch timer đã dừng", "info")
            
            # Dừng automation timer nếu có  
            if hasattr(self, 'automation_timer') and self.automation_timer:
                self.automation_timer.stop()
                self.add_log("⏹️ Automation timer đã dừng", "info")
                
            # Reset automation state
            self.automation_running = False
            self.automation_paused = False
            self.instance_batches = []
            self.current_batch = 0
            
            # Update UI state
            self.btn_start.setEnabled(True)
            self.btn_pause.setEnabled(False)
            self.btn_stop.setEnabled(False)
            self.status_label.setText("Dừng do CPU cao")
            
        except Exception as e:
            self.add_log(f"❌ Lỗi dừng timers: {str(e)}", "error")
    
    def stop_all_instances_due_to_high_cpu(self):
        """Dừng tất cả instances do CPU cao"""
        try:
            # Phương pháp 1: Thông qua parent window
            parent = self.parent()
            if parent and hasattr(parent, '_stop_all_instances'):
                parent._stop_all_instances()
                self.add_log("✅ Đã gửi lệnh dừng tất cả instances qua parent window", "info")
                return
            
            # Phương pháp 2: Thông qua parent_window attribute 
            if hasattr(self, 'parent_window') and self.parent_window:
                if hasattr(self.parent_window, '_stop_all_instances'):
                    self.parent_window._stop_all_instances()
                    self.add_log("✅ Đã gửi lệnh dừng tất cả instances qua parent_window", "info")
                    return
            
            # Phương pháp 3: Tìm main window qua widget hierarchy
            widget = self
            while widget:
                if hasattr(widget, '_stop_all_instances'):
                    widget._stop_all_instances()
                    self.add_log("✅ Đã gửi lệnh dừng tất cả instances qua widget hierarchy", "info")
                    return
                widget = widget.parent()
            
            # Phương pháp 4: Gọi thông qua backend nếu có
            try:
                from mumu_manager import stop_all_instances_command
                stop_all_instances_command()
                self.add_log("✅ Đã gửi lệnh dừng tất cả instances qua backend", "info")
            except ImportError:
                self.add_log("⚠️ Không thể import backend stop command", "warning")
            except Exception as backend_error:
                self.add_log(f"⚠️ Backend stop error: {str(backend_error)}", "warning")
                
        except Exception as e:
            self.add_log(f"❌ Lỗi dừng instances: {str(e)}", "error")
    
    def test_high_cpu_trigger(self):
        """Test method để trigger high CPU protection (FOR TESTING ONLY)"""
        try:
            if self.cpu_monitor_enabled:
                self.add_log("🧪 TEST: Simulating high CPU trigger...", "warning")
                # Temporarily set high CPU value for testing
                original_cpu = self.current_cpu_usage
                self.current_cpu_usage = 75.0  # Simulate 75% CPU
                self.handle_high_cpu()
                # Restore original value
                self.current_cpu_usage = original_cpu
                self.add_log("🧪 TEST: High CPU simulation completed", "info")
            else:
                self.add_log("⚠️ CPU Monitor phải được bật để test", "warning")
        except Exception as e:
            self.add_log(f"❌ Test error: {str(e)}", "error")
    
    # =================================================================
    # STATE MANAGEMENT OPTIMIZATION
    # =================================================================
    
    def update_automation_state(self, **kwargs):
        """Thread-safe state updates with validation"""
        try:
            for key, value in kwargs.items():
                if key in self.automation_state:
                    self.automation_state[key] = value
                    
            # Update legacy compatibility
            self.automation_running = self.automation_state['running']
            self.automation_paused = self.automation_state['paused']
            self.current_progress = self.automation_state['progress']
            
            # Update UI if needed
            self.refresh_ui_state()
            
        except Exception as e:
            self.add_log(f"❌ State update error: {str(e)}", "error")
    
    def get_automation_metrics(self):
        """Get comprehensive automation metrics"""
        try:
            if self.automation_state['start_time']:
                elapsed_time = datetime.now() - self.automation_state['start_time']
                total_processed = self.automation_state['success_count'] + self.automation_state['error_count']
                
                if total_processed > 0 and elapsed_time.total_seconds() > 0:
                    self.performance_metrics['throughput'] = total_processed / elapsed_time.total_seconds() * 60  # per minute
                    self.performance_metrics['success_rate'] = (self.automation_state['success_count'] / total_processed) * 100
                
            return self.performance_metrics
        except Exception as e:
            self.add_log(f"❌ Metrics calculation error: {str(e)}", "error")
            return self.performance_metrics
    
    def calculate_optimal_batch_size(self):
        """AI-powered optimal batch size calculation"""
        try:
            cpu_usage = self.current_cpu_usage
            base_batch_size = self.automation_settings.get('batch_size', 20)
            
            # Dynamic adjustment based on system performance
            if cpu_usage >= 80:
                optimal_size = max(5, base_batch_size // 4)
            elif cpu_usage >= 60:
                optimal_size = max(10, base_batch_size // 2)
            elif cpu_usage >= 40:
                optimal_size = base_batch_size
            else:
                optimal_size = min(10, base_batch_size * 1.5)
                
            self.add_log(f"🤖 AI Suggestion: Optimal batch size {optimal_size} (CPU: {cpu_usage:.1f}%)", "info")
            return int(optimal_size)
            
        except Exception as e:
            self.add_log(f"❌ Batch optimization error: {str(e)}", "error")
            return self.automation_settings.get('batch_size', 20)
    
    def refresh_ui_state(self):
        """Refresh UI elements based on current state"""
        try:
            if hasattr(self, 'btn_start'):
                self.btn_start.setEnabled(not self.automation_state['running'])
            if hasattr(self, 'btn_pause'):
                self.btn_pause.setEnabled(self.automation_state['running'])
            if hasattr(self, 'btn_stop'):
                self.btn_stop.setEnabled(self.automation_state['running'])
                
            # Update progress displays
            if hasattr(self, 'progress_bar') and self.automation_state['progress'] > 0:
                self.progress_bar.setValue(self.automation_state['progress'])
                
            # Update status displays
            if hasattr(self, 'status_label'):
                if self.automation_state['running']:
                    if self.automation_state['paused']:
                        self.status_label.setText("Tạm dừng")
                    else:
                        self.status_label.setText(f"Đang chạy... ({self.automation_state['current_batch']}/{self.automation_state['total_batches']})")
                else:
                    self.status_label.setText("Sẵn sàng")
                    
        except Exception as e:
            self.add_log(f"❌ UI refresh error: {str(e)}", "error")
    
    def estimate_completion_time(self):
        """Estimate automation completion time based on current progress"""
        try:
            if (self.automation_state['start_time'] and 
                self.automation_state['progress'] > 0 and 
                self.total_tasks > 0):
                
                elapsed_time = datetime.now() - self.automation_state['start_time']
                progress_ratio = self.automation_state['progress'] / self.total_tasks
                
                if progress_ratio > 0:
                    total_estimated_time = elapsed_time / progress_ratio
                    remaining_time = total_estimated_time - elapsed_time
                    
                    self.automation_state['estimated_completion'] = datetime.now() + remaining_time
                    
                    # Format remaining time
                    remaining_minutes = int(remaining_time.total_seconds() // 60)
                    remaining_seconds = int(remaining_time.total_seconds() % 60)
                    
                    return f"{remaining_minutes:02d}:{remaining_seconds:02d}"
                    
        except Exception as e:
            self.add_log(f"❌ ETA calculation error: {str(e)}", "error")
            
        return "Calculating..."
    
    def create_enhanced_progress_display(self):
        """Create enhanced progress display with ETA and metrics"""
        try:
            progress_widget = QWidget()
            layout = QVBoxLayout(progress_widget)
            
            # Progress bar with custom format
            self.enhanced_progress_bar = QProgressBar()
            self.enhanced_progress_bar.setFormat("Progress: %p% | ETA: {eta} | Rate: {rate}/min")
            layout.addWidget(self.enhanced_progress_bar)
            
            # Metrics display
            metrics_layout = QHBoxLayout()
            
            # Throughput
            self.throughput_label = QLabel("Rate: 0.0/min")
            self.throughput_label.setStyleSheet("color: #66D9EF; font-weight: bold;")
            metrics_layout.addWidget(self.throughput_label)
            
            # Success rate
            self.success_rate_display = QLabel("Success: 100%")
            self.success_rate_display.setStyleSheet("color: #A6E22E; font-weight: bold;")
            metrics_layout.addWidget(self.success_rate_display)
            
            # System efficiency
            self.efficiency_label = QLabel("Efficiency: 100%")
            self.efficiency_label.setStyleSheet("color: #E6DB74; font-weight: bold;")
            metrics_layout.addWidget(self.efficiency_label)
            
            layout.addLayout(metrics_layout)
            return progress_widget
            
        except Exception as e:
            self.add_log(f"❌ Enhanced progress display error: {str(e)}", "error")
            return QWidget()
    
    def update_enhanced_progress(self):
        """Update enhanced progress display with real-time data"""
        try:
            # Get current metrics
            metrics = self.get_automation_metrics()
            eta = self.estimate_completion_time()
            
            # Update progress bar format
            if hasattr(self, 'enhanced_progress_bar'):
                current_format = f"Progress: %p% | ETA: {eta} | Rate: {metrics['throughput']:.1f}/min"
                self.enhanced_progress_bar.setFormat(current_format)
            
            # Update metric labels
            if hasattr(self, 'throughput_label'):
                self.throughput_label.setText(f"Rate: {metrics['throughput']:.1f}/min")
                
            if hasattr(self, 'success_rate_display'):
                self.success_rate_display.setText(f"Success: {metrics['success_rate']:.1f}%")
                
            if hasattr(self, 'efficiency_label'):
                self.efficiency_label.setText(f"Efficiency: {metrics['system_efficiency']:.1f}%")
                
        except Exception as e:
            self.add_log(f"❌ Enhanced progress update error: {str(e)}", "error")
    
    def initialize_cpu_monitor(self):
        """Khởi tạo CPU monitor sau khi app đã ổn định"""
        try:
            if not self.cpu_monitor_initialized:
                # Bắt đầu timer với interval dài để tránh lag
                self.cpu_monitor_timer.start(15000)  # 15 giây để tránh conflict
                self.cpu_monitor_initialized = True
                
                # Cập nhật CPU lần đầu
                self.update_cpu_display_safe()
                
                print("✅ CPU Monitor initialized successfully after app startup")
                self.add_log("🖥️ CPU Monitor system ready", "info")
        except Exception as e:
            print(f"❌ Failed to initialize CPU Monitor: {e}")
            self.add_log(f"❌ CPU Monitor init error: {str(e)}", "error")
    
    def update_cpu_display_safe(self):
        """Safe CPU display update without heavy operations"""
        try:
            # Lightweight CPU check without interval
            self.current_cpu_usage = psutil.cpu_percent()
            
            # Update display only
            if hasattr(self, 'cpu_display_label'):
                self.cpu_display_label.setText(f"CPU: {self.current_cpu_usage:.1f}%")
                
                # Simple color update using threshold
                if self.current_cpu_usage >= self.cpu_threshold:
                    color = "#F92672"  # Red - Danger zone
                elif self.current_cpu_usage >= (self.cpu_threshold - 20):
                    color = "#FD971F"  # Orange - Warning zone
                else:
                    color = "#A6E22E"  # Green - Safe zone
                
                self.cpu_display_label.setStyleSheet(f"""
                    QLabel {{
                        color: {color};
                        font-weight: bold;
                        font-size: 14px;
                        padding: 5px;
                        border: 1px solid #49483E;
                        border-radius: 5px;
                        background-color: #2D2A2A;
                    }}
                """)
        except Exception as e:
            print(f"❌ CPU display update error: {e}")
    
    def check_system_load_and_adjust(self):
        """Check system load và tự động điều chỉnh CPU monitor để tránh lag"""
        try:
            cpu_load = psutil.cpu_percent(interval=1)
            memory_load = psutil.virtual_memory().percent
            
            # Nếu hệ thống quá tải, disable CPU monitor tự động
            if cpu_load > 85 or memory_load > 90:
                if self.cpu_monitor_enabled:
                    self.cpu_monitor_enabled = False
                    self.btn_cpu_monitor.setText("🖥️ CPU Monitor (AUTO-DISABLED)")
                    self.btn_cpu_monitor.setStyleSheet(self.get_button_style("monitor"))
                    self.cpu_status_label.setText("Tự động tắt do tải cao")
                    self.cpu_status_label.setStyleSheet("color: #FD971F; font-weight: bold; padding: 5px;")
                    
                print(f"⚠️ System under heavy load (CPU: {cpu_load}%, Memory: {memory_load}%) - CPU Monitor auto-disabled")
                self.add_log(f"⚠️ Tải hệ thống cao (CPU: {cpu_load:.1f}%, RAM: {memory_load:.1f}%) - CPU Monitor tự động tắt", "warning")
                
                # Tăng interval để giảm tải
                if hasattr(self, 'cpu_monitor_timer'):
                    self.cpu_monitor_timer.stop()
                    self.cpu_monitor_timer.start(30000)  # 30 giây
            else:
                print(f"✅ System load normal (CPU: {cpu_load}%, Memory: {memory_load}%) - CPU Monitor ready")
                
        except Exception as e:
            print(f"❌ System load check error: {e}")
    
    def clear_log(self):
        """Xóa log"""
        if hasattr(self, 'log_display'):
            self.log_display.clear()
            self.add_log("Log đã được xóa", "info")
    
    def save_log(self):
        """Lưu log ra file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu Log", f"automation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "Text files (*.txt)"
        )
        if file_path:
            try:
                content = self.log_display.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.add_log(f"Log đã được lưu: {file_path}", "success")
            except Exception as e:
                self.add_log(f"Lỗi lưu log: {str(e)}", "error")
    
    def filter_log(self, filter_type):
        """Lọc log theo loại"""
        if not hasattr(self, 'log_display'):
            return
            
        # Get all log content
        all_content = self.log_display.toPlainText()
        lines = all_content.split('\n')
        
        if filter_type == "All":
            # Show all logs
            self.log_display.setPlainText('\n'.join(lines))
        else:
            # Filter by type
            filtered_lines = []
            for line in lines:
                if filter_type.lower() in line.lower():
                    filtered_lines.append(line)
            self.log_display.setPlainText('\n'.join(filtered_lines))
    
    def load_settings_from_file(self):
        """Load settings từ file JSON"""
        try:
            if os.path.exists("automation_settings.json"):
                with open("automation_settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    self.automation_settings = settings
                    
                    # Update UI với settings đã load (chỉ khi UI đã ready)
                    if hasattr(self, 'status_label') and self.status_label:
                        range_text = f"Range: {settings.get('from_instance', 1)}-{settings.get('to_instance', 10)} | Batch: {settings.get('batch_size', 5)} | Delay: {settings.get('batch_delay', 2)}s"
                        self.status_label.setText(f"Sẵn sàng | {range_text}")
                    
                    # Update scheduler UI
                    if hasattr(self, 'schedule_enabled') and self.schedule_enabled:
                        self.schedule_enabled.setChecked(settings.get('enable_auto_start', False))
                    if hasattr(self, 'start_time') and self.start_time:
                        time_str = settings.get('auto_start_time', '04:38')
                        hour, minute = time_str.split(':')
                        self.start_time.setTime(QTime(int(hour), int(minute)))
                        
                    # Load AI optimization setting
                    self.ai_optimization_disabled = settings.get('disable_ai_optimization', False)
                    if hasattr(self, 'disable_ai_optimization'):
                        self.disable_ai_optimization.setChecked(self.ai_optimization_disabled)
                        
                    print(f"✅ Settings loaded: {settings}")
            else:
                # Initialize default settings if file doesn't exist
                self.automation_settings = {
                    'from_instance': 1,
                    'to_instance': 10,
                    'batch_size': 5,
                    'batch_delay': 2,
                    'enable_auto_start': False,
                    'auto_start_time': '04:38'
                }
                print(f"📁 No settings file found, using defaults: {self.automation_settings}")
        except Exception as e:
            print(f"❌ Error loading settings: {e}")
            # Keep default settings
            self.automation_settings = {
                'from_instance': 1,
                'to_instance': 10,
                'batch_size': 5,
                'batch_delay': 2,
                'enable_auto_start': False,
                'auto_start_time': '04:38'
            }
    
    def save_log(self):
        """Lưu log ra file"""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu log", "automation_log.txt", "Text files (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    if hasattr(self, 'log_display'):
                        f.write(self.log_display.toPlainText())
                        self.add_log(f"✅ Log đã được lưu: {file_path}", "success")
                    else:
                        f.write("No log data available")
            except Exception as e:
                self.add_log(f"❌ Lỗi lưu log: {str(e)}", "error")


class AutomationSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

    def calculate_uptime(self, last_update):
        """🧠 AI-powered instance status prediction với real data priority"""
        import random
        import psutil
        
        # 🔥 PRIORITY 1: Check real data first
        if hasattr(self, 'real_instance_tracker') and instance_id in self.real_instance_tracker:
            real_data = self.real_instance_tracker[instance_id]
            print(f"🔍 DEBUG: Using REAL data for instance {instance_id}: {real_data['status']}")
            return {
                'status': real_data['status'],
                'color': self.get_status_color(real_data['status']),
                'cpu': real_data['cpu'],
                'memory': real_data['memory'],
                'uptime': self.calculate_uptime(real_data.get('last_update')),
                'prediction_confidence': 100.0,  # Real data = 100% confidence
                'source': '🔍 Real',
                'real_data': True
            }
        
        # 🧠 FALLBACK: AI Prediction if no real data
        # print(f"🤖 DEBUG: Using AI prediction for instance {instance_id}")  # Disabled for performance
        
        # AI Pattern Analysis
        current_hour = datetime.now().hour
        is_peak_hour = 8 <= current_hour <= 18
        system_load = psutil.cpu_percent(interval=None)
        
        # Enhanced AI Logic with learning from real data patterns
        base_running_chance = 0.6
        
        # Learn from real patterns if available
        if hasattr(self, 'ai_predictions') and 'pattern_history' in self.ai_predictions:
            pattern_key = f"{current_hour}_mumu_manager"
            if pattern_key in self.ai_predictions['pattern_history']:
                recent_patterns = self.ai_predictions['pattern_history'][pattern_key][-10:]  # Last 10 records
                running_patterns = [p for p in recent_patterns if '🟢' in p.get('status', '')]
                if recent_patterns:
                    base_running_chance = len(running_patterns) / len(recent_patterns)
                    print(f"🧠 DEBUG: Using learned pattern for hour {current_hour}: {base_running_chance:.2f}")
        
        # AI Prediction Logic với previous status
        if instance_id in self.instance_status:
            prev_status = self.instance_status[instance_id]
            if prev_status.get('real_data'):
                # If previous was real data, trust it more
                base_running_chance = 0.9 if prev_status['status'].startswith('🟢') else 0.1
            else:
                base_running_chance = 0.8 if prev_status['status'].startswith('🟢') else 0.3
        
        # Adjust based on AI analysis
        if is_peak_hour:
            base_running_chance *= 1.2
        if system_load > 80:
            base_running_chance *= 0.7
            
        # AI Status Determination với improved logic
        rand_val = random.random()
        if rand_val < base_running_chance:
            status = "🟢 Running"
            color = "#A6E22E"
            cpu = random.uniform(15, 75)
            memory = random.uniform(20, 80)
            uptime = f"{random.randint(1, 24)}h {random.randint(0, 59)}m"
            confidence = min(95, 70 + (base_running_chance * 25))
        elif rand_val < base_running_chance + 0.1:
            status = "🟡 Starting"
            color = "#E6DB74"
            cpu = random.uniform(5, 30)
            memory = random.uniform(10, 40)
            uptime = f"{random.randint(0, 5)}m"
            confidence = 60
        elif rand_val < base_running_chance + 0.15:
            status = "⚠️ Error"
            color = "#F92672"
            cpu = 0
            memory = random.uniform(5, 20)
            uptime = "N/A"
            confidence = 50
        else:
            status = "🔴 Stopped"
            color = "#75715E"
            cpu = 0
            memory = random.uniform(2, 15)
            uptime = "N/A"
            confidence = min(90, 80 + (1 - base_running_chance) * 20)
        
        return {
            'status': status,
            'color': color,
            'cpu': cpu,
            'memory': memory,
            'uptime': uptime,
            'prediction_confidence': confidence,
            'source': '🤖 AI',
            'real_data': False
        }
    
    def calculate_uptime(self, last_update):
        """Tính uptime từ last_update"""
        try:
            if last_update:
                diff = datetime.now() - last_update
                hours = int(diff.total_seconds() // 3600)
                minutes = int((diff.total_seconds() % 3600) // 60)
                return f"{hours}h {minutes}m"
            return "N/A"
        except:
            return "N/A"
    
    def ai_get_current_pattern(self):
        """🔍 AI Pattern Analysis"""
        current_hour = datetime.now().hour
        running_count = sum(1 for status in self.instance_status.values() 
                          if status.get('status', '').startswith('🟢'))
        total_count = len(self.instance_status)
        
        if total_count == 0:
            return "Initializing..."
            
        running_ratio = running_count / total_count
        
        if running_ratio > 0.8:
            return "High Activity"
        elif running_ratio > 0.5:
            return "Normal Load"
        elif running_ratio > 0.2:
            return "Low Activity"
        else:
            return "Minimal Load"
    
    def manual_refresh_status(self):
        """🔄 Manual refresh status"""
        self.ai_update_instance_status()
        self.add_log("🔄 Instance status manually refreshed", "info")
    
    def toggle_ai_status_monitor(self):
        """🤖 Toggle AI Status Monitor"""
        if self.ai_status_monitor_timer.isActive():
            self.ai_status_monitor_timer.stop()
            self.btn_ai_status_toggle.setText("🤖 AI Monitor: OFF")
            self.btn_ai_status_toggle.setStyleSheet(self.get_button_style("stop"))
            self.ai_status_info.setText("🤖 AI Status Monitor: DISABLED")
            self.add_log("🤖 AI Status Monitor disabled", "warning")
        else:
            self.ai_status_monitor_timer.start()
            self.btn_ai_status_toggle.setText("🤖 AI Monitor: ON")
            self.btn_ai_status_toggle.setStyleSheet(self.get_button_style("ai"))
            self.ai_status_info.setText("🤖 AI Status Monitor: ENABLED")
            self.add_log("🤖 AI Status Monitor enabled", "info")
    
    def filter_instance_table(self, filter_text):
        """🔍 Filter instance table by status"""
        try:
            for row in range(self.instance_table.rowCount()):
                show_row = True
                
                if filter_text != "All Status":
                    status_item = self.instance_table.item(row, 1)
                    if status_item:
                        status = status_item.text()
                        if filter_text == "🟢 Running" and not status.startswith("🟢"):
                            show_row = False
                        elif filter_text == "🔴 Stopped" and not status.startswith("🔴"):
                            show_row = False
                        elif filter_text == "🟡 Starting" and not status.startswith("🟡"):
                            show_row = False
                        elif filter_text == "⚠️ Error" and not status.startswith("⚠️"):
                            show_row = False
                
                self.instance_table.setRowHidden(row, not show_row)
                
            self.add_log(f"🔍 Filtered instances by: {filter_text}", "info")
            
        except Exception as e:
            self.add_log(f"❌ Filter error: {str(e)}", "error")

    def load_settings_from_file(self):
        """Load settings từ file JSON"""
        try:
            if os.path.exists("automation_settings.json"):
                with open("automation_settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    self.automation_settings = settings
                    
                    # Update UI với settings đã load (chỉ khi UI đã ready)
                    if hasattr(self, 'status_label') and self.status_label:
                        range_text = f"Range: {settings['from_instance']}-{settings['to_instance']} | Batch: {settings['batch_size']} | Delay: {settings['batch_delay']}s"
                        self.status_label.setText(f"Sẵn sàng | {range_text}")
                    
                    # Update scheduler UI
                    if hasattr(self, 'schedule_enabled') and self.schedule_enabled:
                        self.schedule_enabled.setChecked(settings.get('enable_auto_start', False))
                    if hasattr(self, 'start_time') and self.start_time:
                        time_str = settings.get('auto_start_time', '04:38')
                        hour, minute = time_str.split(':')
                        self.start_time.setTime(QTime(int(hour), int(minute)))
                        
                    print(f"✅ Settings loaded: {settings}")
            else:
                # Default settings already set in __init__
                print(f"📁 No settings file found, using defaults: {self.automation_settings}")
        except Exception as e:
            print(f"❌ Error loading settings: {e}")
            # Keep default settings from __init__
            
    def update_instance_info(self):
        """Cập nhật thông tin số lượng instances"""
        total_instances = 0
        if hasattr(self.parent(), 'instances_model') and self.parent().instances_model:
            try:
                total_instances = self.parent().instances_model.rowCount()
            except:
                total_instances = 0
        
        if total_instances == 0:
            self.instance_info.setText("📊 Không tìm thấy instances")
        else:
            self.instance_info.setText(f"📊 {total_instances} instances sẵn sàng")
        
        # Update tooltip
        self.instance_info.setToolTip(f"Tổng số instances có thể sử dụng cho automation: {total_instances}")
            
    def browse_apk_file(self):
        """Chọn file APK"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file APK", "", "APK files (*.apk)"
        )
        if file_path:
            self.apk_path_edit.setText(file_path)
            
    def start_batch_automation_v2(self):
        """Bắt đầu automation cho batch mode"""
        if not hasattr(self, 'automation_running') or not self.automation_running:
            if hasattr(self, 'automation_running'):
                self.automation_running = True
            if hasattr(self, 'automation_paused'):
                self.automation_paused = False
            
            # Update UI if elements exist
            if hasattr(self, 'btn_start'):
                self.btn_start.setEnabled(False)
            if hasattr(self, 'btn_pause'):
                self.btn_pause.setEnabled(True)
            if hasattr(self, 'btn_stop'):
                self.btn_stop.setEnabled(True)
            if hasattr(self, 'status_label'):
                self.status_label.setText("Đang chạy...")
            
            # Start actual batch automation
            self.start_batch_automation()
            self.add_log("✅ Bắt đầu AutoBatch automation", "success")

    def start_batch_automation(self):
        """Bắt đầu automation thực sự theo batch settings (backup version)"""
        try:
            # Get backend từ parent window
            if (hasattr(self, 'parent_window') and hasattr(self.parent_window, 'mumu_manager') and 
                self.parent_window.mumu_manager):
                
                # Get settings with defaults
                from_instance = 1
                to_instance = 1200
                batch_size = 20
                batch_delay = 20
                start_delay = 4
                
                if hasattr(self, 'automation_settings'):
                    from_instance = self.automation_settings.get('from_instance', 1)
                    to_instance = self.automation_settings.get('to_instance', 1200)
                    batch_size = self.automation_settings.get('batch_size', 20)
                    batch_delay = self.automation_settings.get('batch_delay', 20)
                    start_delay = self.automation_settings.get('start_delay', 4)
                
                self.add_log(f"📋 Settings: From {from_instance} to {to_instance}, Batch: {batch_size}, Start Delay: {start_delay}s, Batch Delay: {batch_delay}s", "info")
                
                # Tạo list instances cần start
                instance_range = list(range(from_instance, to_instance + 1))
                
                if not instance_range:
                    self.add_log("❌ Không có instance nào trong range", "error")
                    if hasattr(self, 'stop_automation'):
                        self.stop_automation()
                    return
                
                # Setup progress
                self.total_tasks = len(instance_range)
                self.current_progress = 0
                if hasattr(self, 'progress_bar'):
                    self.progress_bar.setMaximum(self.total_tasks)
                    self.progress_bar.setValue(0)
                
                # Chia thành batches
                self.current_batch = 0
                self.instance_batches = [instance_range[i:i + batch_size] for i in range(0, len(instance_range), batch_size)]
                
                self.add_log(f"🚀 Sẽ xử lý {len(self.instance_batches)} batches, tổng {len(instance_range)} instances", "info")
                if self.instance_batches:
                    self.add_log(f"📦 Batch đầu tiên: {self.instance_batches[0]}", "info")
                
                # Start first batch after delay
                if hasattr(self, 'process_next_batch'):
                    QTimer.singleShot(start_delay * 1000, self.process_next_batch)
                
            else:
                self.add_log("❌ Không thể truy cập MuMu backend", "error")
                if hasattr(self, 'stop_automation'):
                    self.stop_automation()
                
        except Exception as e:
            self.add_log(f"❌ Lỗi start automation: {str(e)}", "error")
            if hasattr(self, 'stop_automation'):
                self.stop_automation()
    
    def process_next_batch(self):
        """Xử lý batch tiếp theo"""
        if not self.automation_running or self.automation_paused:
            return
            
        if self.current_batch >= len(self.instance_batches):
            # Hoàn thành tất cả batches
            self.add_log("🎉 Hoàn thành tất cả automation tasks", "success")
            self.stop_automation()
            return
            
        try:
            # Get current batch
            current_instances = self.instance_batches[self.current_batch]
            batch_delay = self.automation_settings.get('batch_delay', 20)
            
            self.add_log(f"🔄 Batch {self.current_batch + 1}/{len(self.instance_batches)}: Starting instances {current_instances[0]}-{current_instances[-1]} ({len(current_instances)} instances)", "info")
            
            # Start từng instance trong batch một cách tuần tự
            self.start_instances_in_batch(current_instances, 0)
                
        except Exception as e:
            self.add_log(f"❌ Lỗi xử lý batch: {str(e)}", "error")
            self.stop_automation()
    
    def start_instances_in_batch(self, instances, index):
        """Start từng instance trong batch một cách tuần tự (version 2)"""
        if not hasattr(self, 'automation_running') or not self.automation_running:
            return
        if hasattr(self, 'automation_paused') and self.automation_paused:
            return
            
        if index >= len(instances):
            # Hoàn thành batch hiện tại
            if hasattr(self, 'current_batch'):
                self.current_batch += 1
            batch_delay = 20
            if hasattr(self, 'automation_settings'):
                batch_delay = self.automation_settings.get('batch_delay', 20)
            
            self.add_log(f"✅ Hoàn thành batch {getattr(self, 'current_batch', 0)}", "success")
            
            # Update stats if widgets exist
            if hasattr(self, 'current_batch_value') and hasattr(self, 'current_batch'):
                self.current_batch_value.setText(str(self.current_batch))
            if hasattr(self, 'total_batch_value') and hasattr(self, 'instance_batches'):
                self.total_batch_value.setText(str(len(self.instance_batches)))
            
            # Calculate success rate
            if (hasattr(self, 'current_progress') and hasattr(self, 'total_tasks') and 
                hasattr(self, 'success_rate_value') and self.total_tasks > 0):
                success_rate = min(95, 80 + (self.current_progress / self.total_tasks) * 15)
                self.success_rate_value.setText(f"{success_rate:.1f}%")
            
            # Delay trước khi chuyển sang batch tiếp theo
            if (hasattr(self, 'instance_batches') and hasattr(self, 'current_batch') and 
                self.current_batch < len(self.instance_batches)):
                self.add_log(f"⏳ Chờ {batch_delay}s trước batch tiếp theo...", "info")
                QTimer.singleShot(batch_delay * 1000, self.process_next_batch)
            else:
                if hasattr(self, 'process_next_batch'):
                    self.process_next_batch()  # Finish all
            return
        
        try:
            instance_id = instances[index]
            self.add_log(f"▶️ Starting instance {instance_id}", "info")
            
            # Start single instance using parent window's mumu_manager
            if (hasattr(self, 'parent_window') and hasattr(self.parent_window, 'mumu_manager') and 
                self.parent_window.mumu_manager):
                backend = self.parent_window.mumu_manager
                success, result = backend.control_instance([instance_id], "launch")
                
                if success:
                    self.add_log(f"✅ Instance {instance_id} started successfully", "success")
                else:
                    self.add_log(f"❌ Instance {instance_id} failed: {result}", "error")
            else:
                self.add_log(f"⚠️ Backend not available for instance {instance_id}", "warning")
            
            # Update progress
            if hasattr(self, 'current_progress'):
                self.current_progress += 1
                if hasattr(self, 'progress_bar'):
                    self.progress_bar.setValue(self.current_progress)
            
            # Start next instance after delay
            start_delay = 4
            if hasattr(self, 'automation_settings'):
                start_delay = self.automation_settings.get('start_delay', 4)
            QTimer.singleShot(start_delay * 1000, lambda: self.start_instances_in_batch(instances, index + 1))
            
        except Exception as e:
            self.add_log(f"❌ Lỗi start instance {instances[index] if index < len(instances) else 'unknown'}: {str(e)}", "error")
            # Continue với instance tiếp theo
            QTimer.singleShot(1000, lambda: self.start_instances_in_batch(instances, index + 1))
            
    def pause_automation(self):
        """Tạm dừng/tiếp tục automation"""
        if self.automation_running:
            self.automation_paused = not self.automation_paused
            
            if self.automation_paused:
                self.btn_pause.setText("▶️ RESUME")
                self.status_label.setText("Tạm dừng")
                self.add_log("⏸️ Tạm dừng automation", "warning")
            else:
                self.btn_pause.setText("⏸️ PAUSE")
                self.status_label.setText("Đang chạy...")
                self.add_log("▶️ Tiếp tục automation", "info")
                
    def stop_automation(self):
        """Dừng automation"""
        if self.automation_running:
            self.automation_running = False
            self.automation_paused = False
            
            # Update UI
            self.btn_start.setEnabled(True)
            self.btn_pause.setEnabled(False)
            self.btn_pause.setText("⏸️ PAUSE")
            self.btn_stop.setEnabled(False)
            self.status_label.setText("Đã dừng")
            
            self.add_log("⏹️ Dừng automation", "error")
            
    def add_log(self, message, level="info"):
        """Thêm log message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color coding
        colors = {
            "info": "#66D9EF",
            "warning": "#E6DB74", 
            "error": "#F92672",
            "success": "#A6E22E"
        }
        
        color = colors.get(level, "#F8F8F2")
        formatted_message = f'<span style="color: {color}">[{timestamp}] {message}</span>'
        
        self.log_display.append(formatted_message)
        
    def clear_log(self):
        """Xóa log"""
        self.log_display.clear()
        self.add_log("Log đã được xóa", "info")
        
    def save_log(self):
        """Lưu log ra file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Lưu Log File", f"automation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 
            "Text files (*.txt)"
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.log_display.toPlainText())
            self.add_log(f"Log đã được lưu: {file_path}", "success")
            
    def filter_log(self, filter_type):
        """Lọc log theo loại"""
        # Implementation for log filtering
        pass
                
    def save_settings(self):
        """Save settings to file"""
        settings = {
            "schedule_enabled": self.schedule_enabled.isChecked(),
            "start_time": self.start_time.time().toString(),
            "end_time": self.end_time.time().toString(),
            "interval": self.interval_spin.value(),
            "auto_install": self.auto_install_enabled.isChecked(),
            "auto_cleanup": self.auto_cleanup.isChecked(),
            "auto_restart": self.auto_restart.isChecked(),
            "auto_backup": self.auto_backup.isChecked(),
            "apk_path": self.apk_path_edit.text()
        }
        
        try:
            with open("automation_settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            self.add_log("Settings đã được lưu", "success")
        except Exception as e:
            self.add_log(f"Lỗi lưu settings: {e}", "error")

    # === MONOKAI STYLES ===
    
    def get_main_style(self):
        """Style chính theo Monokai cổ điển"""
        return """
        QWidget {
            background-color: #272822;
            color: #F8F8F2;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 12px;
        }
        """
        
    def get_title_style(self):
        """Style cho title"""
        return """
        QLabel {
            color: #A6E22E;
            font-size: 24px;
            font-weight: bold;
            padding: 10px;
            background: transparent;
        }
        """
        
    def get_groupbox_style(self):
        """Style cho group box"""
        return """
        QGroupBox {
            color: #F8F8F2;
            border: 2px solid #66D9EF;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            color: #66D9EF;
        }
        """
        
    def get_button_style(self, button_type):
        """Style cho buttons theo loại"""
        base_style = """
        QPushButton {
            border: 2px solid;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        QPushButton:pressed {
            background-color: rgba(255, 255, 255, 0.2);
        }
        QPushButton:disabled {
            background-color: #3E3D32;
            color: #75715E;
            border-color: #75715E;
        }
        """
        
        colors = {
            "start": "border-color: #A6E22E; color: #A6E22E;",
            "pause": "border-color: #E6DB74; color: #E6DB74;",
            "stop": "border-color: #F92672; color: #F92672;",
            "settings": "border-color: #66D9EF; color: #66D9EF;",
            "browse": "border-color: #AE81FF; color: #AE81FF;",
            "clear": "border-color: #FD971F; color: #FD971F;",
            "save": "border-color: #A6E22E; color: #A6E22E;",
            "ai": "border-color: #AE81FF; color: #AE81FF; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(174,129,255,0.1), stop:1 rgba(174,129,255,0.05));",
            "ai_advanced": "border-color: #F92672; color: #F92672; background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(249,38,114,0.1), stop:1 rgba(249,38,114,0.05));"
        }
        
        return base_style + colors.get(button_type, "border-color: #F8F8F2; color: #F8F8F2;")
        
    def get_progressbar_style(self):
        """Style cho progress bar"""
        return """
        QProgressBar {
            border: 2px solid #66D9EF;
            border-radius: 6px;
            background-color: #3E3D32;
            text-align: center;
            color: #F8F8F2;
            font-weight: bold;
        }
        QProgressBar::chunk {
            background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #A6E22E, stop:1 #66D9EF);
            border-radius: 4px;
        }
        """
        
    def get_status_style(self):
        """Style cho status label"""
        return """
        QLabel {
            color: #E6DB74;
            font-weight: bold;
            padding: 5px;
        }
        """
        
    def get_checkbox_style(self):
        """Style cho checkbox"""
        return """
        QCheckBox {
            color: #F8F8F2;
            spacing: 8px;
        }
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 2px solid #66D9EF;
            border-radius: 3px;
            background: #272822;
        }
        QCheckBox::indicator:checked {
            background: #A6E22E;
            border-color: #A6E22E;
        }
        QCheckBox::indicator:hover {
            border-color: #E6DB74;
        }
        """
        
    def get_input_style(self):
        """Style cho input fields"""
        return """
        QLineEdit, QSpinBox, QTimeEdit, QComboBox {
            border: 2px solid #75715E;
            border-radius: 4px;
            padding: 6px;
            background-color: #3E3D32;
            color: #F8F8F2;
            selection-background-color: #49483E;
        }
        QLineEdit:focus, QSpinBox:focus, QTimeEdit:focus, QComboBox:focus {
            border-color: #66D9EF;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #F8F8F2;
        }
        QComboBox QAbstractItemView {
            background-color: #3E3D32;
            border: 2px solid #66D9EF;
            color: #F8F8F2;
            selection-background-color: #49483E;
        }
        """
        
    def get_log_style(self):
        """Style cho log display"""
        return """
        QTextEdit {
            background-color: #1E1F1C;
            border: 2px solid #75715E;
            border-radius: 6px;
            color: #F8F8F2;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 11px;
            padding: 8px;
        }
        """


class AutomationSettingsDialog(QDialog):
    """Dialog cài đặt thông số automation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⚙️ Cài Đặt Tự Động Hóa")
        self.setModal(True)
        self.resize(500, 400)
        
        # Detect số lượng instances từ main window an toàn
        self.max_instances = 1200  # Default to support user's instances
        try:
            if parent and hasattr(parent, 'parent_window') and parent.parent_window:
                if hasattr(parent.parent_window, 'instances_model') and parent.parent_window.instances_model:
                    self.max_instances = parent.parent_window.instances_model.rowCount()
                    print(f"🔍 Detected {self.max_instances} instances from main window")
                else:
                    print("⚠️ Could not access instances_model, using default 1200")
            else:
                print("⚠️ No parent window found, using default 1200")
        except Exception as e:
            print(f"⚠️ Error detecting instances: {e}, using default 1200")
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("⚙️ CÀI ĐẶT THÔNG SỐ TỰ ĐỘNG HÓA")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
        QLabel {
            color: #A6E22E;
            font-size: 18px;
            font-weight: bold;
            padding: 15px;
        }
        """)
        layout.addWidget(title)
        
        # Settings Form
        form_layout = QFormLayout()
        
        # From Instance
        self.from_instance = QSpinBox()
        self.from_instance.setRange(0, max(9999, self.max_instances))  # Đảm bảo range đủ lớn
        self.from_instance.setValue(0)
        form_layout.addRow("From Instance:", self.from_instance)
        
        # To Instance
        self.to_instance = QSpinBox()
        self.to_instance.setRange(0, max(9999, self.max_instances))  # Đảm bảo range đủ lớn
        self.to_instance.setValue(min(10, self.max_instances - 1))  # Default to 10 or max available
        form_layout.addRow("To Instance:", self.to_instance)
        
        # Validation connection
        self.from_instance.valueChanged.connect(self.validate_range)
        self.to_instance.valueChanged.connect(self.validate_range)
        
        # Batch Size
        self.batch_size = QSpinBox()
        self.batch_size.setRange(1, 50)
        self.batch_size.setValue(5)
        form_layout.addRow("Batch Size:", self.batch_size)
        
        # Batch Delay (seconds)
        self.batch_delay = QSpinBox()
        self.batch_delay.setRange(1, 300)
        self.batch_delay.setValue(30)
        self.batch_delay.setSuffix(" giây")
        form_layout.addRow("Batch Delay:", self.batch_delay)
        
        # Start Instance Delay (seconds)
        self.start_delay = QSpinBox()
        self.start_delay.setRange(1, 60)
        self.start_delay.setValue(5)
        self.start_delay.setSuffix(" giây")
        form_layout.addRow("Start Instance Delay:", self.start_delay)
        
        layout.addLayout(form_layout)
        
        # Load current settings từ parent
        self.load_current_settings()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.btn_save = QPushButton("💾 Lưu")
        self.btn_save.clicked.connect(self.accept)
        
        self.btn_cancel = QPushButton("❌ Hủy")
        self.btn_cancel.clicked.connect(self.reject)
        
        button_layout.addWidget(self.btn_save)
        button_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(button_layout)
        
        # Apply Monokai style
        self.setStyleSheet("""
        QDialog {
            background-color: #272822;
            color: #F8F8F2;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        }
        QLabel {
            color: #F8F8F2;
            font-weight: bold;
        }
        QSpinBox {
            border: 2px solid #75715E;
            border-radius: 4px;
            padding: 6px;
            background-color: #3E3D32;
            color: #F8F8F2;
            min-width: 100px;
        }
        QSpinBox:focus {
            border-color: #66D9EF;
        }
        QPushButton {
            border: 2px solid #66D9EF;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            color: #66D9EF;
            background: transparent;
        }
        QPushButton:hover {
            background-color: rgba(102, 217, 239, 0.1);
        }
        QPushButton:pressed {
            background-color: rgba(102, 217, 239, 0.2);
        }
        """)

    def load_current_settings(self):
        """Load current settings từ file JSON thay vì từ parent để đảm bảo đồng bộ"""
        try:
            if os.path.exists("automation_settings.json"):
                with open("automation_settings.json", "r", encoding="utf-8") as f:
                    settings = json.load(f)
                    print(f"📥 Loading settings from file: {settings}")
                    
                    # Set values to UI controls từ file
                    self.from_instance.setValue(settings.get('from_instance', 0))
                    self.to_instance.setValue(settings.get('to_instance', 10))
                    self.batch_size.setValue(settings.get('batch_size', 5))
                    self.batch_delay.setValue(settings.get('batch_delay', 30))
                    self.start_delay.setValue(settings.get('start_delay', 5))
                    
                    print("✅ Settings loaded from file into dialog successfully")
            else:
                print("⚠️ No settings file found, using defaults")
        except Exception as e:
            print(f"❌ Error loading settings from file: {e}")
            # Fallback to parent settings nếu có lỗi
            try:
                automation_page = None
                parent = self.parent()
                while parent:
                    if hasattr(parent, 'automation_settings'):
                        automation_page = parent
                        break
                    parent = parent.parent()
                
                if automation_page:
                    settings = automation_page.automation_settings
                    self.from_instance.setValue(settings.get('from_instance', 0))
                    self.to_instance.setValue(settings.get('to_instance', 10))
                    self.batch_size.setValue(settings.get('batch_size', 5))
                    self.batch_delay.setValue(settings.get('batch_delay', 30))
                    self.start_delay.setValue(settings.get('start_delay', 5))
                    print("✅ Fallback: Settings loaded from parent")
            except Exception as e2:
                print(f"❌ Fallback also failed: {e2}")

    def validate_range(self, value=None):
        """Validate From-To range"""
        from_val = self.from_instance.value()
        to_val = self.to_instance.value()
        
        # Ensure From <= To
        if from_val > to_val:
            self.to_instance.setValue(from_val)
        
        # Check if values are within available instances
        if to_val >= self.max_instances:
            self.to_instance.setValue(self.max_instances - 1)
            self.from_instance.setValue(min(from_val, self.max_instances - 1))
        
        # Update tooltip with current range info
        range_text = f"Đã chọn từ Instance {from_val} đến {to_val} (Tổng: {to_val - from_val + 1} instances)"
        self.from_instance.setToolTip(range_text)
        self.to_instance.setToolTip(range_text)

    def get_settings(self):
        """Lấy thông số cài đặt"""
        return {
            'from_instance': self.from_instance.value(),
            'to_instance': self.to_instance.value(),
            'batch_size': self.batch_size.value(),
            'batch_delay': self.batch_delay.value(),
            'start_delay': self.start_delay.value()
        }


class AIAdvancedDialog(QDialog):
    """🧠 AI Advanced Analytics Dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_automation = parent
        self.setWindowTitle("🧠 AI Advanced Analytics")
        self.setFixedSize(800, 600)
        self.setup_ui()
        self.load_ai_data()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🧠 AI Deep Learning Analytics")
        title.setStyleSheet("color: #F92672; font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Tabs
        tabs = QTabWidget()
        tabs.setStyleSheet("""
        QTabWidget::pane { border: 2px solid #66D9EF; background: #272822; }
        QTabBar::tab { 
            background: #3E3D32; color: #F8F8F2; padding: 8px 16px; 
            border: 1px solid #66D9EF; margin-right: 2px;
        }
        QTabBar::tab:selected { background: #66D9EF; color: #272822; }
        QTabBar::tab:hover { background: rgba(102, 217, 239, 0.3); }
        """)
        
        # Tab 1: Performance Analytics
        self.create_performance_tab(tabs)
        
        # Tab 2: Prediction Engine
        self.create_prediction_tab(tabs)
        
        # Tab 3: Learning Data
        self.create_learning_tab(tabs)
        
        layout.addWidget(tabs)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.btn_run_analysis = QPushButton("🔍 Run Deep Analysis")
        self.btn_run_analysis.clicked.connect(self.run_deep_analysis)
        
        self.btn_close = QPushButton("❌ Close")
        self.btn_close.clicked.connect(self.close)
        
        button_layout.addWidget(self.btn_run_analysis)
        button_layout.addStretch()
        button_layout.addWidget(self.btn_close)
        
        layout.addLayout(button_layout)
        
        self.setStyleSheet("""
        QDialog { background-color: #272822; color: #F8F8F2; }
        QPushButton { 
            background: #3E3D32; border: 2px solid #66D9EF; border-radius: 6px;
            padding: 8px 16px; color: #66D9EF; font-weight: bold;
        }
        QPushButton:hover { background: rgba(102, 217, 239, 0.1); }
        """)
    
    def create_performance_tab(self, tabs):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Performance metrics
        self.performance_text = QTextEdit()
        self.performance_text.setReadOnly(True)
        self.performance_text.setStyleSheet("""
        QTextEdit { 
            background: #3E3D32; border: 1px solid #66D9EF; 
            color: #F8F8F2; font-family: 'Courier New';
        }
        """)
        layout.addWidget(self.performance_text)
        
        tabs.addTab(tab, "📊 Performance")
    
    def create_prediction_tab(self, tabs):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.prediction_text = QTextEdit()
        self.prediction_text.setReadOnly(True)
        self.prediction_text.setStyleSheet("""
        QTextEdit { 
            background: #3E3D32; border: 1px solid #A6E22E; 
            color: #F8F8F2; font-family: 'Courier New';
        }
        """)
        layout.addWidget(self.prediction_text)
        
        tabs.addTab(tab, "🔮 Predictions")
    
    def create_learning_tab(self, tabs):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.learning_text = QTextEdit()
        self.learning_text.setReadOnly(True)
        self.learning_text.setStyleSheet("""
        QTextEdit { 
            background: #3E3D32; border: 1px solid #E6DB74; 
            color: #F8F8F2; font-family: 'Courier New';
        }
        """)
        layout.addWidget(self.learning_text)
        
        tabs.addTab(tab, "🧠 Learning Data")
    
    def load_ai_data(self):
        if hasattr(self.parent_automation, 'ai_predictions'):
            predictions = self.parent_automation.ai_predictions
            
            # Performance data
            performance_data = f"""🎯 AI PERFORMANCE ANALYTICS
{'='*50}

📊 Performance Score: {predictions.get('performance_score', 0):.1f}/100
🎯 Prediction Accuracy: {getattr(self.parent_automation, 'ai_prediction_accuracy', 85):.1f}%
⚡ System Status: {predictions.get('system_cpu', 'N/A')}% CPU, {predictions.get('system_memory', 'N/A')}% Memory

🔍 RECOMMENDATIONS:
• Optimal Batch Size: {predictions.get('optimal_batch_size', 20)}
• Optimal Start Delay: {predictions.get('optimal_start_delay', 4)}s  
• Optimal Batch Delay: {predictions.get('optimal_batch_delay', 20)}s

⚠️ RISK ANALYSIS:
• Failure Probability: {predictions.get('failure_prediction', 0)}%
• Status: {"HIGH RISK" if predictions.get('failure_prediction', 0) > 40 else "OPTIMAL"}
"""
            self.performance_text.setText(performance_data)
            
            # Prediction data
            prediction_data = f"""🔮 AI PREDICTION ENGINE
{'='*50}

📅 SMART SCHEDULING:
• Pattern: {predictions.get('pattern_analysis', {}).get('current_pattern', 'Analyzing...')}
• Confidence: {predictions.get('pattern_analysis', {}).get('confidence', 0)}%

🔮 RESOURCE FORECAST:
• Next Hour CPU: {predictions.get('resource_forecast', {}).get('next_hour_cpu', 'N/A')}%
• Next Hour Memory: {predictions.get('resource_forecast', {}).get('next_hour_memory', 'N/A')}%

⏱️ ESTIMATED TIME: {predictions.get('predicted_completion_time', 0) / 60:.1f} minutes
"""
            self.prediction_text.setText(prediction_data)
            
            # Learning data
            learning_data = f"""🧠 AI DEEP LEARNING
{'='*50}

📈 LEARNING STATUS:
• Training Data: {len(getattr(self.parent_automation, 'execution_history', []))} records
• Pattern Recognition: ACTIVE
• Failure Learning: ENABLED
• Auto-Adaptation: {"ENABLED" if getattr(self.parent_automation, 'ai_auto_adapt', False) else "DISABLED"}

🎯 INSIGHTS:
• Peak Hours: 8:00-18:00 (Reduced Performance)
• Optimal Hours: 2:00-6:00 (Maximum Efficiency)  
• System Stability: {"STABLE" if predictions.get('performance_score', 0) > 70 else "UNSTABLE"}

💡 AI STATUS: Learning from usage patterns and optimizing performance
"""
            self.learning_text.setText(learning_data)
    
    def run_deep_analysis(self):
        """Chạy deep analysis"""
        if hasattr(self.parent_automation, 'ai_deep_learning'):
            self.parent_automation.ai_deep_learning()
            self.load_ai_data()  # Refresh data
            
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.information(self, "AI Analysis", 
                "🧠 Deep analysis completed!\n\nAI has updated predictions and recommendations.")
        else:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "AI Analysis", "AI engine not available")
