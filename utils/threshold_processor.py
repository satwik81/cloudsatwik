"""
Threshold processor for filtering data based on configured rules
"""

import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List


class ThresholdProcessor:
    """Processes data based on threshold rules"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def apply_rule(self, data: pd.DataFrame, rule: Dict[str, Any]) -> pd.DataFrame:
        """Apply a threshold rule to filter data"""
        if data.empty:
            return data
        
        try:
            # Handle simple threshold rules
            if 'threshold_field' in rule:
                return self._apply_simple_threshold(data, rule)
            
            # Handle complex condition rules
            elif 'conditions' in rule:
                return self._apply_conditions(data, rule)
            
            else:
                self.logger.warning(f"Rule '{rule.get('name', 'unknown')}' has no threshold_field or conditions")
                return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"Error applying rule '{rule.get('name', 'unknown')}': {e}")
            return pd.DataFrame()
    
    def _apply_simple_threshold(self, data: pd.DataFrame, rule: Dict[str, Any]) -> pd.DataFrame:
        """Apply a simple threshold rule"""
        field = rule['threshold_field']
        threshold_type = rule['threshold_type']
        threshold_value = rule['threshold_value']
        
        if field not in data.columns:
            self.logger.warning(f"Field '{field}' not found in data")
            return pd.DataFrame()
        
        # Apply threshold based on type
        if threshold_type == 'greater_than':
            return data[data[field] > threshold_value]
        elif threshold_type == 'less_than':
            return data[data[field] < threshold_value]
        elif threshold_type == 'greater_than_or_equal':
            return data[data[field] >= threshold_value]
        elif threshold_type == 'less_than_or_equal':
            return data[data[field] <= threshold_value]
        elif threshold_type == 'equals':
            return data[data[field] == threshold_value]
        elif threshold_type == 'not_equals':
            return data[data[field] != threshold_value]
        elif threshold_type == 'within_hours':
            return self._filter_by_time(data, field, threshold_value)
        else:
            self.logger.error(f"Unknown threshold type: {threshold_type}")
            return pd.DataFrame()
    
    def _apply_conditions(self, data: pd.DataFrame, rule: Dict[str, Any]) -> pd.DataFrame:
        """Apply multiple conditions (AND logic)"""
        filtered_data = data.copy()
        
        for condition in rule['conditions']:
            field = condition['field']
            operator = condition['operator']
            value = condition['value']
            
            if field not in filtered_data.columns:
                self.logger.warning(f"Field '{field}' not found in data")
                continue
            
            # Apply condition
            if operator == 'greater_than':
                filtered_data = filtered_data[filtered_data[field] > value]
            elif operator == 'less_than':
                filtered_data = filtered_data[filtered_data[field] < value]
            elif operator == 'greater_than_or_equal':
                filtered_data = filtered_data[filtered_data[field] >= value]
            elif operator == 'less_than_or_equal':
                filtered_data = filtered_data[filtered_data[field] <= value]
            elif operator == 'equals':
                filtered_data = filtered_data[filtered_data[field] == value]
            elif operator == 'not_equals':
                filtered_data = filtered_data[filtered_data[field] != value]
            elif operator == 'contains':
                filtered_data = filtered_data[filtered_data[field].astype(str).str.contains(str(value), na=False)]
            elif operator == 'in':
                if isinstance(value, list):
                    filtered_data = filtered_data[filtered_data[field].isin(value)]
                else:
                    self.logger.warning(f"'in' operator requires a list value, got {type(value)}")
            else:
                self.logger.error(f"Unknown operator: {operator}")
        
        return filtered_data
    
    def _filter_by_time(self, data: pd.DataFrame, field: str, hours: int) -> pd.DataFrame:
        """Filter data within specified hours from now"""
        try:
            # Convert field to datetime if it's not already
            if not pd.api.types.is_datetime64_any_dtype(data[field]):
                data[field] = pd.to_datetime(data[field])
            
            # Calculate cutoff time
            cutoff_time = datetime.now() - timedelta(hours=hours)
            
            # Filter data
            return data[data[field] >= cutoff_time]
            
        except Exception as e:
            self.logger.error(f"Error filtering by time: {e}")
            return pd.DataFrame()