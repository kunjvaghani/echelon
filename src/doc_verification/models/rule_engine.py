"""
RULE ENGINE: Content Mismatch Detection
========================================
Compares OCR output with user-provided data
"""

import re
from typing import Dict, Optional
from datetime import datetime, date

try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    def relativedelta(dt1, dt2):
        """Fallback relativedelta"""
        class RD:
            def __init__(self, y):
                self.years = y
        return RD((dt1 - dt2).days // 365)

try:
    from ..config import RULE_CONFIG, ID_PATTERNS
except ImportError:
    from doc_verification.config import RULE_CONFIG, ID_PATTERNS

try:
    from fuzzywuzzy import fuzz
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False


class RuleEngine:
    """Logic-based validation engine for document verification"""
    
    def __init__(self):
        self.config = RULE_CONFIG
    
    def _levenshtein_ratio(self, s1: str, s2: str) -> float:
        """
        Calculate Levenshtein ratio for string similarity.
        Returns 0.0 to 1.0 (1.0 = identical).
        """
        if not s1 or not s2:
            return 0.0
            
        rows = len(s1) + 1
        cols = len(s2) + 1
        distance = [[0 for _ in range(cols)] for _ in range(rows)]

        for i in range(1, rows):
            distance[i][0] = i
        for k in range(1, cols):
            distance[0][k] = k

        for col in range(1, cols):
            for row in range(1, rows):
                if s1[row - 1] == s2[col - 1]:
                    cost = 0
                else:
                    cost = 1
                distance[row][col] = min(distance[row - 1][col] + 1,      # deletion
                                         distance[row][col - 1] + 1,      # insertion
                                         distance[row - 1][col - 1] + cost) # substitution

        max_len = max(len(s1), len(s2))
        if max_len == 0:
            return 1.0
            
        return 1.0 - (distance[rows - 1][cols - 1] / max_len)

    def compare_names(self, ocr_name: Optional[str], user_name: str) -> Dict:
        """Compare names using robust fuzzy matching"""
        if not ocr_name:
            return {
                'score': 0.0,
                'match': False,
                'message': 'Could not extract name from document',
                'mismatch_score': 1.0
            }
        
        ocr_normalized = self._normalize_name(ocr_name)
        user_normalized = self._normalize_name(user_name)
        
        # 1. Exact Match Check
        if ocr_normalized == user_normalized:
             return {
                'score': 1.0,
                'match': True,
                'message': 'Names match exactly',
                'mismatch_score': 0.0
            }

        # 2. Token Set Ratio (Handles "Kunj Vaghani" vs "Vaghani Kunj")
        ocr_tokens = set(ocr_normalized.split())
        user_tokens = set(user_normalized.split())
        
        common_tokens = ocr_tokens.intersection(user_tokens)
        token_overlap = len(common_tokens) / max(len(ocr_tokens), len(user_tokens))
        
        # 3. Levenshtein Distance (Handles typos like "Kunj" vs "Kunj.")
        lev_ratio = self._levenshtein_ratio(ocr_normalized, user_normalized)
        
        # Combined Score
        # We give more weight to Levenshtein if token overlap is low (typos)
        # But if token overlap is high, it's good.
        
        similarity = max(token_overlap, lev_ratio)
        
        # Boost for partial contain (e.g. "Kunj" in "Kunj Vaghani")
        if (len(ocr_normalized) > 3 and ocr_normalized in user_normalized) or \
           (len(user_normalized) > 3 and user_normalized in ocr_normalized):
            similarity = max(similarity, 0.95)
        
        threshold = self.config['name_match_threshold']
        is_match = similarity >= threshold
        mismatch_score = 1.0 - similarity
        
        return {
            'score': round(similarity, 3),
            'match': is_match,
            'ocr_name': ocr_name,
            'user_name': user_name,
            'message': f'Match Score: {similarity:.0%}' if is_match else f'Mismatch: {similarity:.0%}',
            'mismatch_score': round(mismatch_score, 3)
        }
    
    def _normalize_name(self, name: str) -> str:
        """Normalize name for comparison"""
        return ' '.join(name.upper().split())
    
    def validate_dob(self, ocr_dob: Optional[str], user_dob: str) -> Dict:
        """Validate Date of Birth"""
        result = {
            'match': False,
            'age_valid': False,
            'ocr_dob': ocr_dob,
            'user_dob': user_dob,
            'age': None,
            'mismatch_score': 1.0,
            'messages': []
        }
        
        # Try parsing user_dob in multiple formats
        user_date = None
        for date_format in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y']:
            try:
                user_date = datetime.strptime(user_dob, date_format).date()
                break
            except (ValueError, TypeError):
                continue
        
        if user_date is None:
            result['messages'].append('Invalid user DOB format')
            return result
        
        today = date.today()
        try:
            age = relativedelta(today, user_date).years
        except:
            age = (today - user_date).days // 365
        
        result['age'] = age
        
        min_age = self.config['min_age']
        max_age = self.config['max_age']
        
        if age < min_age:
            result['messages'].append(f'User is under minimum age ({min_age})')
            result['age_valid'] = False
        elif age > max_age:
            result['messages'].append(f'Invalid age: over {max_age}')
            result['age_valid'] = False
        else:
            result['age_valid'] = True
        
        if not ocr_dob:
            result['messages'].append('Could not extract DOB from document')
            result['mismatch_score'] = 0.5
            return result
        
        # Try parsing ocr_dob in multiple formats
        ocr_date = None
        for date_format in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y']:
            try:
                ocr_date = datetime.strptime(ocr_dob, date_format).date()
                break
            except (ValueError, TypeError):
                continue
        
        if ocr_date is None:
            result['messages'].append('Could not parse OCR DOB')
            result['mismatch_score'] = 0.5
            return result
        
        if ocr_date == user_date:
            result['match'] = True
            result['mismatch_score'] = 0.0
            result['messages'].append('DOB matches')
        else:
            diff_days = abs((ocr_date - user_date).days)
            if diff_days <= 1:
                result['match'] = True
                result['mismatch_score'] = 0.1
                result['messages'].append('DOB matches (within 1 day tolerance)')
            else:
                result['mismatch_score'] = min(diff_days / 365, 1.0)
                result['messages'].append(f'DOB mismatch: {diff_days} days difference')
        
        return result
    
    def validate_id_format(self, id_number: Optional[str], user_id: str,
                          id_type: Optional[str] = None) -> Dict:
        """Validate ID format"""
        result = {
            'score': 0.0,
            'match': False,
            'message': '',
            'mismatch_score': 1.0
        }
        
        if not id_number:
            result['message'] = 'Could not extract ID from document'
            return result
        
        id_number_clean = id_number.replace(' ', '').replace('-', '').upper()
        user_id_clean = user_id.replace(' ', '').replace('-', '').upper()
        
        if id_number_clean == user_id_clean:
            result['score'] = 1.0
            result['match'] = True
            result['mismatch_score'] = 0.0
            result['message'] = 'ID matches exactly'
        else:
            common_chars = sum(1 for a, b in zip(id_number_clean, user_id_clean) if a == b)
            max_len = max(len(id_number_clean), len(user_id_clean))
            similarity = common_chars / max_len if max_len > 0 else 0.0
            
            result['score'] = round(similarity, 3)
            result['match'] = similarity >= 0.97
            result['mismatch_score'] = round(1.0 - similarity, 3)
            result['message'] = f'ID match: {similarity:.0%}'
        
        return result
    
    def get_mismatch_score(self, ocr_data: Dict, user_data: Dict) -> Dict:
        """Get overall mismatch score"""
        name_result = self.compare_names(ocr_data.get('name'), user_data.get('name', ''))
        dob_result = self.validate_dob(ocr_data.get('dob'), user_data.get('dob', ''))
        id_result = self.validate_id_format(ocr_data.get('id_number'), 
                                           user_data.get('id_number', ''),
                                           ocr_data.get('id_type'))
        
        name_match_percent = name_result['score'] * 100
        dob_match_percent = (1.0 - dob_result['mismatch_score']) * 100
        id_match_percent = id_result['score'] * 100
        
        if name_match_percent >= 90:
            name_decision = 'APPROVE'
        elif name_match_percent >= 80:
            name_decision = 'MANUAL_REVIEW'
        else:
            name_decision = 'REJECT'
        
        if dob_match_percent >= 97:
            dob_decision = 'APPROVE'
        elif dob_match_percent >= 80:
            dob_decision = 'MANUAL_REVIEW'
        else:
            dob_decision = 'REJECT'
        
        if id_match_percent >= 97:
            id_decision = 'APPROVE'
        elif id_match_percent >= 80:
            id_decision = 'MANUAL_REVIEW'
        else:
            id_decision = 'REJECT'
        
        if 'REJECT' in [name_decision, dob_decision, id_decision]:
            data_decision = 'REJECT'
        elif 'MANUAL_REVIEW' in [name_decision, dob_decision, id_decision]:
            data_decision = 'MANUAL_REVIEW'
        else:
            data_decision = 'APPROVE'
        
        overall_match = (name_match_percent + dob_match_percent + id_match_percent) / 300
        all_match = data_decision == 'APPROVE'
        
        flags = self._generate_flags(name_result, dob_result, id_result, 
                                    name_match_percent, dob_match_percent, id_match_percent,
                                    name_decision, dob_decision, id_decision)
        
        component_decisions = {
            'data_match': data_decision,
            'age_valid': 'APPROVE' if dob_result['age_valid'] else 'REJECT'
        }
        
        return {
            'mismatch_score': round(1.0 - overall_match, 3),
            'percentages': {
                'name_percent': round(name_match_percent, 1),
                'dob_percent': round(dob_match_percent, 1),
                'id_percent': round(id_match_percent, 1)
            },
            'field_decisions': {
                'name': name_decision,
                'dob': dob_decision,
                'id': id_decision
            },
            'all_match': all_match,
            'age_valid': dob_result['age_valid'],
            'component_decisions': component_decisions,
            'details': {
                'name': name_result,
                'dob': dob_result,
                'id': id_result
            },
            'flags': flags
        }
    
    def _generate_flags(self, name_result: Dict, dob_result: Dict, id_result: Dict,
                       name_pct: float, dob_pct: float, id_pct: float,
                       name_dec: str, dob_dec: str, id_dec: str) -> list:
        """Generate human-readable flags"""
        flags = []
        
        if name_dec == 'REJECT':
            flags.append(f'❌ Name match {name_pct:.0f}% - Below 80% (REJECT)')
        elif name_dec == 'MANUAL_REVIEW':
            flags.append(f'⚠️ Name match {name_pct:.0f}% - 80-90% (review)')
        else:
            flags.append(f'✅ Name match {name_pct:.0f}% - >= 90% (Excellent)')
        
        if dob_dec == 'REJECT':
            flags.append(f'❌ DOB match {dob_pct:.0f}% - <= 80% (REJECT)')
        elif dob_dec == 'MANUAL_REVIEW':
            flags.append(f'⚠️ DOB match {dob_pct:.0f}% - 80-97% (review)')
        else:
            flags.append(f'✅ DOB match {dob_pct:.0f}% - >= 97% (Excellent)')
        
        if id_dec == 'REJECT':
            flags.append(f'❌ ID match {id_pct:.0f}% - <= 80% (REJECT)')
        elif id_dec == 'MANUAL_REVIEW':
            flags.append(f'⚠️ ID match {id_pct:.0f}% - 80-97% (review)')
        else:
            flags.append(f'✅ ID match {id_pct:.0f}% - >= 97% (Excellent)')
        
        if not dob_result['age_valid']:
            flags.append('❌ Age validation failed')
        
        return flags


def validate_document_content(ocr_data: Dict, user_data: Dict) -> Dict:
    """Validate document content against user data"""
    engine = RuleEngine()
    return engine.get_mismatch_score(ocr_data, user_data)
