# optimizations/smart_templates.py - Smart Instance Templates & Automation

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

@dataclass
class InstanceTemplate:
    """Smart instance template with all configurations."""
    id: str
    name: str
    description: str
    created_date: str
    # Performance settings
    cpu_count: int
    memory_gb: float
    graphics_mode: str  # 'directx', 'opengl', 'vk'
    frame_rate: int
    # System settings
    android_version: str
    resolution: str
    dpi: int
    orientation: str
    # Network settings
    network_type: str
    bridge_mode: bool
    # Apps and data
    pre_installed_apps: List[Dict[str, str]]
    shared_folders: List[Dict[str, str]]
    # Advanced features
    automation_scripts: List[Dict[str, str]]
    startup_actions: List[str]
    custom_settings: Dict[str, Any]

class SmartTemplateManager:
    """Advanced template management system."""
    
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = templates_dir
        self.ensure_templates_dir()
        self.built_in_templates = self._load_built_in_templates()
        
    def ensure_templates_dir(self):
        """Ensure templates directory exists."""
        os.makedirs(self.templates_dir, exist_ok=True)
        
    # === TEMPLATE CREATION ===
    
    def create_template_from_instance(self, instance_index: int, mumu_manager, 
                                    name: str, description: str = "") -> InstanceTemplate:
        """Create template from existing instance."""
        # Get current instance settings
        settings = mumu_manager.get_all_settings(instance_index)
        instance_info = mumu_manager.get_enhanced_instance_info(instance_index)
        
        template = InstanceTemplate(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            created_date=datetime.now().isoformat(),
            cpu_count=int(settings.get('performance_cpu.custom', 4)),
            memory_gb=float(settings.get('performance_mem.custom', 6.0)),
            graphics_mode=settings.get('renderer_mode', 'vk'),
            frame_rate=int(settings.get('max_frame_rate', 60)),
            android_version=settings.get('android_version', '9'),
            resolution=settings.get('resolution', '1920x1080'),
            dpi=int(settings.get('dpi', 320)),
            orientation=settings.get('orientation', 'portrait'),
            network_type=settings.get('network_type', 'nat'),
            bridge_mode=settings.get('bridge_mode', False),
            pre_installed_apps=[],
            shared_folders=[],
            automation_scripts=[],
            startup_actions=[],
            custom_settings=settings
        )
        
        self.save_template(template)
        return template

    def create_smart_gaming_template(self, game_name: str, game_package: str) -> InstanceTemplate:
        """Create optimized gaming template."""
        return InstanceTemplate(
            id=str(uuid.uuid4()),
            name=f"Gaming - {game_name}",
            description=f"Optimized template for {game_name}",
            created_date=datetime.now().isoformat(),
            cpu_count=4,
            memory_gb=8.0,
            graphics_mode='vk',
            frame_rate=60,
            android_version='9',
            resolution='1920x1080',
            dpi=320,
            orientation='landscape',
            network_type='nat',
            bridge_mode=False,
            pre_installed_apps=[{
                'name': game_name,
                'package': game_package,
                'auto_install': True
            }],
            shared_folders=[],
            automation_scripts=[{
                'name': 'game_optimizer',
                'description': 'Auto-optimize for gaming',
                'script': self._generate_gaming_script()
            }],
            startup_actions=[
                'clear_cache',
                'optimize_performance',
                'launch_game'
            ],
            custom_settings={
                'performance_mode': 'high',
                'dynamic_adjust_frame_rate': 'false',
                'renderer_mode': 'vk',
                'vsync': 'false',
                'anti_aliasing': 'msaa_4x'
            }
        )

    def create_development_template(self) -> InstanceTemplate:
        """Create template optimized for app development."""
        return InstanceTemplate(
            id=str(uuid.uuid4()),
            name="Development Environment",
            description="Optimized for Android app development and testing",
            created_date=datetime.now().isoformat(),
            cpu_count=6,
            memory_gb=10.0,
            graphics_mode='opengl',
            frame_rate=30,
            android_version='11',
            resolution='1440x2560',
            dpi=420,
            orientation='portrait',
            network_type='bridge',
            bridge_mode=True,
            pre_installed_apps=[
                {'name': 'Android Studio Tools', 'package': 'com.android.tools', 'auto_install': True},
                {'name': 'ADB Shell', 'package': 'com.cgutman.androidremotedebugger', 'auto_install': True}
            ],
            shared_folders=[
                {'host_path': 'C:\\Development\\Projects', 'guest_path': '/sdcard/projects'},
                {'host_path': 'C:\\Development\\APKs', 'guest_path': '/sdcard/apks'}
            ],
            automation_scripts=[{
                'name': 'dev_setup',
                'description': 'Setup development environment',
                'script': self._generate_dev_script()
            }],
            startup_actions=[
                'enable_developer_options',
                'enable_usb_debugging',
                'setup_adb_connection',
                'mount_shared_folders'
            ],
            custom_settings={
                'developer_options': 'true',
                'usb_debugging': 'true',
                'stay_awake': 'true',
                'show_touches': 'true',
                'animator_duration_scale': '0.5'
            }
        )

    # === TEMPLATE MANAGEMENT ===
    
    def save_template(self, template: InstanceTemplate):
        """Save template to file."""
        file_path = os.path.join(self.templates_dir, f"{template.id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(template), f, ensure_ascii=False, indent=2)

    def load_template(self, template_id: str) -> Optional[InstanceTemplate]:
        """Load template from file."""
        file_path = os.path.join(self.templates_dir, f"{template_id}.json")
        if not os.path.exists(file_path):
            return None
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        return InstanceTemplate(**data)

    def list_templates(self) -> List[InstanceTemplate]:
        """List all available templates."""
        templates = []
        
        # Load custom templates
        for file_name in os.listdir(self.templates_dir):
            if file_name.endswith('.json'):
                template_id = file_name[:-5]
                template = self.load_template(template_id)
                if template:
                    templates.append(template)
        
        # Add built-in templates
        templates.extend(self.built_in_templates)
        
        return sorted(templates, key=lambda t: t.created_date, reverse=True)

    def delete_template(self, template_id: str) -> bool:
        """Delete template."""
        file_path = os.path.join(self.templates_dir, f"{template_id}.json")
        try:
            os.remove(file_path)
            return True
        except:
            return False

    # === TEMPLATE APPLICATION ===
    
    async def apply_template_to_instance(self, template: InstanceTemplate, 
                                       instance_index: int, mumu_manager) -> bool:
        """Apply template settings to instance."""
        try:
            # Apply basic settings
            settings = template.custom_settings.copy()
            settings.update({
                'performance_cpu.custom': str(template.cpu_count),
                'performance_mem.custom': str(template.memory_gb),
                'renderer_mode': template.graphics_mode,
                'max_frame_rate': str(template.frame_rate),
                'resolution': template.resolution,
                'dpi': str(template.dpi),
                'orientation': template.orientation
            })
            
            result = await mumu_manager.bulk_apply_settings([instance_index], settings)
            if not result.get(instance_index, False):
                return False
            
            # Install pre-configured apps
            for app in template.pre_installed_apps:
                if app.get('auto_install') and 'apk_path' in app:
                    await mumu_manager.bulk_install_apk([instance_index], app['apk_path'])
            
            # Execute startup actions
            for action in template.startup_actions:
                await self._execute_startup_action(action, instance_index, mumu_manager)
            
            # Run automation scripts
            for script in template.automation_scripts:
                await self._execute_automation_script(script, instance_index, mumu_manager)
            
            return True
            
        except Exception as e:
            print(f"Error applying template: {e}")
            return False

    async def create_instance_from_template(self, template: InstanceTemplate, 
                                          instance_name: str, mumu_manager) -> Optional[int]:
        """Create new instance from template."""
        try:
            # Create new instance
            result = await mumu_manager._run_command_async([
                'control', 'create', 
                '-name', instance_name,
                '-cpu', str(template.cpu_count),
                '-mem', str(int(template.memory_gb * 1024)),
                '-resolution', template.resolution
            ])
            
            if not result['success']:
                return None
            
            # Get new instance index (assuming it's returned or we find it)
            instances = await mumu_manager._run_command_async(['info', '-v', 'all'])
            # Parse and find the new instance...
            
            # Apply template settings
            # await self.apply_template_to_instance(template, new_index, mumu_manager)
            
            return None  # Return actual index when found
            
        except Exception as e:
            print(f"Error creating instance from template: {e}")
            return None

    # === BUILT-IN TEMPLATES ===
    
    def _load_built_in_templates(self) -> List[InstanceTemplate]:
        """Load built-in templates."""
        templates = []
        
        # High Performance Gaming
        templates.append(InstanceTemplate(
            id="builtin_gaming_high",
            name="🎮 High Performance Gaming",
            description="Maximum performance for demanding games",
            created_date="2024-01-01T00:00:00",
            cpu_count=6,
            memory_gb=12.0,
            graphics_mode='vk',
            frame_rate=60,
            android_version='9',
            resolution='1920x1080',
            dpi=320,
            orientation='landscape',
            network_type='nat',
            bridge_mode=False,
            pre_installed_apps=[],
            shared_folders=[],
            automation_scripts=[],
            startup_actions=['optimize_performance', 'clear_cache'],
            custom_settings={
                'performance_mode': 'high',
                'renderer_mode': 'vk',
                'vsync': 'false',
                'dynamic_adjust_frame_rate': 'false'
            }
        ))
        
        # Lightweight Testing
        templates.append(InstanceTemplate(
            id="builtin_testing_light",
            name="🧪 Lightweight Testing",
            description="Resource-efficient for app testing",
            created_date="2024-01-01T00:00:00",
            cpu_count=2,
            memory_gb=4.0,
            graphics_mode='opengl',
            frame_rate=30,
            android_version='11',
            resolution='1080x1920',
            dpi=420,
            orientation='portrait',
            network_type='nat',
            bridge_mode=False,
            pre_installed_apps=[],
            shared_folders=[],
            automation_scripts=[],
            startup_actions=['enable_developer_options'],
            custom_settings={
                'performance_mode': 'low',
                'developer_options': 'true',
                'stay_awake': 'true'
            }
        ))
        
        return templates

    # === AUTOMATION SCRIPTS ===
    
    def _generate_gaming_script(self) -> str:
        """Generate gaming optimization script."""
        return """
        # Gaming Optimization Script
        echo "Optimizing for gaming..."
        
        # Clear system cache
        pm clear com.android.providers.media
        
        # Disable animations
        settings put global window_animation_scale 0
        settings put global transition_animation_scale 0
        settings put global animator_duration_scale 0
        
        # Set performance mode
        echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor
        
        # Clear background apps
        am kill-all
        
        echo "Gaming optimization complete!"
        """

    def _generate_dev_script(self) -> str:
        """Generate development setup script."""
        return """
        # Development Environment Setup
        echo "Setting up development environment..."
        
        # Enable developer options
        settings put global development_settings_enabled 1
        
        # Enable USB debugging
        settings put global adb_enabled 1
        
        # Show touches
        settings put system show_touches 1
        
        # Set animation scales
        settings put global window_animation_scale 0.5
        settings put global transition_animation_scale 0.5
        settings put global animator_duration_scale 0.5
        
        echo "Development environment ready!"
        """

    async def _execute_startup_action(self, action: str, instance_index: int, mumu_manager):
        """Execute a startup action."""
        actions = {
            'clear_cache': ['control', '-v', str(instance_index), 'adb', 'shell', 'pm', 'clear-cache-all'],
            'optimize_performance': ['control', '-v', str(instance_index), 'optimize'],
            'enable_developer_options': ['control', '-v', str(instance_index), 'adb', 'shell', 'settings', 'put', 'global', 'development_settings_enabled', '1'],
            'enable_usb_debugging': ['control', '-v', str(instance_index), 'adb', 'shell', 'settings', 'put', 'global', 'adb_enabled', '1']
        }
        
        if action in actions:
            await mumu_manager._run_command_async(actions[action])

    async def _execute_automation_script(self, script: Dict[str, str], 
                                       instance_index: int, mumu_manager):
        """Execute an automation script."""
        # For simplicity, execute as shell commands
        script_content = script.get('script', '')
        if script_content:
            await mumu_manager._run_command_async([
                'control', '-v', str(instance_index), 'adb', 'shell', 'sh', '-c', script_content
            ])

# === EXPORT ===

__all__ = [
    'InstanceTemplate',
    'SmartTemplateManager'
]
