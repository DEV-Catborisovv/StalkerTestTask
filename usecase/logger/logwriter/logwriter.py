# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class LogWriter(object):
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def write_logs(self, logs, filename):
        pass
    
    def format_timestamp(self, dt):
        return dt.strftime('[%y-%m-%d %H:%M:%S]')

class CombinedLogWriter(LogWriter):
    def write_logs(self, logs, filename):
        with open(filename, 'w') as f:
            for timestamp, log_entry, log_type, line_num in logs:
                f.write(log_entry + '\n')

class OutputWriter(LogWriter):
    def write_logs(self, logs, filename):
        pass
    
    def write_output(self, stats, filename):
        with open(filename, 'w') as f:
            self._write_top_items(f, stats.get('top_items', []))
            self._write_top_players(f, stats.get('top_players', []))
            self._write_first_items(f, stats.get('first_items', []))
            self._write_last_items(f, stats.get('last_items', []))
    
    def _write_top_items(self, file_obj, top_items):
        file_obj.write("Топ 10 предметов по количеству встречаемости в логах:\n")
        file_obj.write("Название предмета, количество\n")
        for item_id, count in top_items:
            file_obj.write("%s, %s\n" % (item_id, count))
        file_obj.write("\n")
    
    def _write_top_players(self, file_obj, top_players):
        file_obj.write("Топ 10 игроков по количеству денег:\n")
        file_obj.write("Имя игрока, количество денег, дата первого упоминания, дата последнего упоминания\n")
        for player in top_players:
            player_id, money, first_date, last_date = player
            file_obj.write("%s, %s, %s, %s\n" % (player_id, money, first_date, last_date))
        file_obj.write("\n")
    
    def _write_first_items(self, file_obj, first_items):
        file_obj.write("Первые 10 предметов в исходном порядке:\n")
        file_obj.write("Название, дата\n")
        for item_id, timestamp in first_items:
            file_obj.write("%s, %s\n" % (item_id, self.format_timestamp(timestamp)))
        file_obj.write("\n")
    
    def _write_last_items(self, file_obj, last_items):
        file_obj.write("Последние 10 предметов в исходном порядке:\n")
        file_obj.write("Название, дата\n")
        for item_id, timestamp in last_items:
            file_obj.write("%s, %s\n" % (item_id, self.format_timestamp(timestamp)))