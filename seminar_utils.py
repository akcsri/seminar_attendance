"""
Utility functions for handling structured seminar information.
Since database schema changes are prohibited, we store structured data
in the existing topic field and parse it as needed.
"""

import json
import re
from datetime import datetime
from typing import Dict, Optional, Any


def parse_seminar_topic(topic: str) -> Dict[str, Any]:
    """
    Parse structured information from the topic field.
    
    Supports both JSON format and structured text format.
    
    Args:
        topic: Topic field content (JSON or structured text)
        
    Returns:
        Dictionary with parsed information including:
        - description: Main seminar description
        - open_time: Opening time (if available)
        - end_time: End time (if available) 
        - speaker_bio: Speaker biography (if available)
    """
    if not topic:
        return {
            'description': '',
            'open_time': '',
            'end_time': '',
            'speaker_bio': ''
        }
    
    # Try to parse as JSON first
    try:
        parsed = json.loads(topic)
        if isinstance(parsed, dict):
            return {
                'description': parsed.get('description', ''),
                'open_time': parsed.get('open_time', ''),
                'end_time': parsed.get('end_time', ''),
                'speaker_bio': parsed.get('speaker_bio', '')
            }
    except (json.JSONDecodeError, ValueError):
        pass
    
    # Parse structured text format
    result = {
        'description': '',
        'open_time': '',
        'end_time': '',
        'speaker_bio': ''
    }
    
    # Extract sections using regex patterns
    
    # Extract description (概要 section)
    desc_match = re.search(r'【概要】\s*\n?(.*?)(?:\n【|$)', topic, re.DOTALL)
    if desc_match:
        result['description'] = desc_match.group(1).strip()
    
    # Extract speaker bio (講師経歴 section)
    bio_match = re.search(r'【講師経歴】\s*\n?(.*?)(?:\n【|$)', topic, re.DOTALL)
    if bio_match:
        result['speaker_bio'] = bio_match.group(1).strip()
    
    # Extract times from 時間 section
    time_match = re.search(r'【時間】\s*\n?(.*?)(?:\n【|$)', topic, re.DOTALL)
    if time_match:
        time_section = time_match.group(1)
        
        # Extract opening time
        open_match = re.search(r'開場:\s*(\d{1,2}:\d{2})', time_section)
        if open_match:
            result['open_time'] = open_match.group(1)
        
        # Extract end time
        end_match = re.search(r'終了:\s*(\d{1,2}:\d{2})', time_section)
        if end_match:
            result['end_time'] = end_match.group(1)
    
    # If no structured sections found, use entire topic as description
    if not any(result.values()):
        result['description'] = topic.strip()
    
    return result


def create_structured_topic(description: str = '', open_time: str = '', 
                          end_time: str = '', speaker_bio: str = '') -> str:
    """
    Create structured topic text from individual components.
    
    This generates a structured format that can be parsed by parse_seminar_topic.
    
    Args:
        description: Main seminar description
        open_time: Opening time (e.g., "18:00")
        end_time: End time (e.g., "20:00")
        speaker_bio: Speaker biography
        
    Returns:
        Structured topic string
    """
    parts = []
    
    if description:
        parts.append(f"【概要】\n{description}")
    
    if speaker_bio:
        parts.append(f"【講師経歴】\n{speaker_bio}")
    
    if open_time or end_time:
        time_parts = []
        if open_time:
            time_parts.append(f"開場: {open_time}")
        if end_time:
            time_parts.append(f"終了: {end_time}")
        
        if time_parts:
            parts.append(f"【時間】\n{' | '.join(time_parts)}")
    
    return '\n\n'.join(parts)


def create_structured_topic_json(description: str = '', open_time: str = '', 
                                end_time: str = '', speaker_bio: str = '') -> str:
    """
    Create structured topic as JSON format.
    
    Args:
        description: Main seminar description
        open_time: Opening time (e.g., "18:00")
        end_time: End time (e.g., "20:00")
        speaker_bio: Speaker biography
        
    Returns:
        JSON string containing structured topic information
    """
    data = {
        'description': description,
        'open_time': open_time,
        'end_time': end_time,
        'speaker_bio': speaker_bio
    }
    
    return json.dumps(data, ensure_ascii=False, indent=2)


def validate_time_format(time_str: str) -> bool:
    """
    Validate time format (HH:MM).
    
    Args:
        time_str: Time string to validate
        
    Returns:
        True if valid time format, False otherwise
    """
    if not time_str:
        return True  # Empty is valid
    
    pattern = r'^\d{1,2}:\d{2}$'
    if not re.match(pattern, time_str):
        return False
    
    try:
        # Try to parse as time
        datetime.strptime(time_str, '%H:%M')
        return True
    except ValueError:
        return False


def get_formatted_seminar_info(seminar) -> Dict[str, str]:
    """
    Get formatted seminar information including parsed topic data.
    
    Args:
        seminar: Seminar model instance
        
    Returns:
        Dictionary with all seminar information including parsed topic fields
    """
    if not seminar:
        return {}
    
    parsed_topic = parse_seminar_topic(seminar.topic or '')
    
    result = {
        'id': str(seminar.id) if seminar.id else '',
        'title': seminar.title or '',
        'date': seminar.date.strftime('%Y年%m月%d日 %H:%M') if seminar.date else '',
        'date_short': seminar.date.strftime('%m/%d %H:%M') if seminar.date else '',
        'venue': seminar.venue or '',
        'speaker': seminar.speaker or '',
        'contact': seminar.contact or '',
        'topic_raw': seminar.topic or '',
        **parsed_topic  # Add parsed fields: description, open_time, end_time, speaker_bio
    }
    
    return result