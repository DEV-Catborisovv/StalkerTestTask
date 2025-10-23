# -*- coding: utf-8 -*-

import re
import datetime
from abc import ABCMeta, abstractmethod

from usecase.logger.logreader.re_patterns import INVENTORY_LOG_PATTERN

class LogReader:
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def read_logs(self, filename):
        pass
    
    def parse_timestamp(self, timestamp_str):
        # убираем квадратные скобки если они есть
        timestamp_str = timestamp_str.strip('[]')
        
        try:
            # пробуем распарсить как timestamp
            timestamp_int = int(timestamp_str)
            return datetime.datetime.fromtimestamp(timestamp_int)
        except ValueError:
            # если не число пробуем стандартные форматы даты
            try:
                return datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            except:
                return datetime.datetime.strptime(timestamp_str, '%y-%m-%d %H:%M:%S')
        
class InventoryLogReader(LogReader):
    def read_logs(self, filename):
        logs = []
        
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                match = re.match(INVENTORY_LOG_PATTERN, line)
                if match:
                    timestamp_str, action_type, player_id, items_str = match.groups()
                    timestamp = self.parse_timestamp(timestamp_str)
                    player_id = int(player_id)
                    
                    items = self._parse_items(items_str)
                    logs.append((timestamp, action_type, player_id, items, line_num))
                else:
                    print("Не удалось прочитать лог инвентаря: %s" % line)

        return logs
    
    def _parse_items(self, items_str):
        items = []
        # убираем скобки если они есть
        items_str = items_str.strip('()')
        item_pairs = items_str.split(', ')
        for i in range(0, len(item_pairs), 2):
            if i + 1 < len(item_pairs):
                item_type_id = int(item_pairs[i])
                amount = int(item_pairs[i + 1])
                items.append((item_type_id, amount))
        return items

class MoneyLogReader(LogReader):
    def read_logs(self, filename):
        logs = []
        
        with open(filename, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                    
                parts = line.split('|')
                if len(parts) >= 4:
                    timestamp_str = parts[0].strip()
                    player_id = int(parts[1].strip())
                    action_type = parts[2].strip()
                    amount_reason = parts[3].strip()
                    
                    timestamp = self.parse_timestamp(timestamp_str)
                    amount, reason = self._parse_amount_reason(amount_reason)
                    
                    logs.append((timestamp, action_type, player_id, amount, reason, line_num))
                else:
                    print("Не удалось прочитать лог баланса: %s" % line)
        
        return logs
    
    def _parse_amount_reason(self, amount_reason_str):
        amount_reason_parts = amount_reason_str.split(',')
        if len(amount_reason_parts) >= 2:
            amount = int(amount_reason_parts[0].strip())
            reason = ','.join(amount_reason_parts[1:]).strip()
            return amount, reason
        else:
            print("Не удалось спарсить сумму / причину: %s" % amount_reason_str)
            return 0, "unknown"