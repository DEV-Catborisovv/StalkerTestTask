# -*- coding: utf-8 -*-

from collections import defaultdict, Counter
from models.player import Player

class LogProcessor:
    def __init__(self, inventory_reader, money_reader, combined_writer, output_writer):
        self.inventory_reader = inventory_reader
        self.money_reader = money_reader
        self.combined_writer = combined_writer
        self.output_writer = output_writer
        
        self.players = {}
        self.item_logs = []
        self.money_logs = []
        self.item_occurrence = Counter()
        self.first_item_mentions = []
        self.last_item_mentions = []
    
    def process_logs(self, inventory_logs, money_logs):
        self.item_logs = inventory_logs
        self.money_logs = money_logs
        
        for timestamp, action_type, player_id, items, line_num in self.item_logs:
            if player_id not in self.players:
                self.players[player_id] = Player(player_id)
                
            player = self.players[player_id]
            
            for item_type_id, amount in items:
                self.item_occurrence[item_type_id] += 1
                self.first_item_mentions.append((item_type_id, timestamp))
                self.last_item_mentions.append((item_type_id, timestamp))
                
                if action_type == 'ITEM_ADD':
                    player.add_item(item_type_id, amount, timestamp)
                elif action_type == 'ITEM_REMOVE':
                    player.remove_item(item_type_id, amount, timestamp)
        
        for timestamp, action_type, player_id, amount, reason, line_num in self.money_logs:
            if player_id not in self.players:
                self.players[player_id] = Player(player_id)
                
            player = self.players[player_id]
            
            if action_type == 'MONEY_ADD':
                player.add_money(amount, timestamp)
            elif action_type == 'MONEY_REMOVE':
                player.remove_money(amount, timestamp)
    
    def create_combined_logs(self):
        all_logs = []
        
        for timestamp, action_type, player_id, items, line_num in self.item_logs:
            items_str = ' '.join(['(%s, %s)' % (item_id, amount) for item_id, amount in items])
            log_entry = "%s %s | %s %s" % (
                self.combined_writer.format_timestamp(timestamp), 
                player_id, 
                action_type, 
                items_str
            )
            all_logs.append((timestamp, log_entry, 'inventory', line_num))
        
        for timestamp, action_type, player_id, amount, reason, line_num in self.money_logs:
            log_entry = "%s %s | %s | %s | %s" % (
                self.combined_writer.format_timestamp(timestamp),
                player_id,
                action_type,
                amount,
                reason
            )
            all_logs.append((timestamp, log_entry, 'money', line_num))
        
        all_logs.sort(key=lambda x: (x[0], 0 if x[2] == 'inventory' else 1, x[3]))
        
        return all_logs
    
    def generate_statistics(self):
        top_items = self.item_occurrence.most_common(10)
        
        sorted_players = sorted(self.players.values(), key=lambda p: p.money, reverse=True)[:10]
        top_players = []
        for player in sorted_players:
            first_date = self.combined_writer.format_timestamp(player.first_mention) if player.first_mention else "N/A"
            last_date = self.combined_writer.format_timestamp(player.last_mention) if player.last_mention else "N/A"
            top_players.append((player.player_id, player.money, first_date, last_date))
        
        seen_items = set()
        first_items = []
        for item_id, timestamp in self.first_item_mentions:
            if item_id not in seen_items:
                seen_items.add(item_id)
                first_items.append((item_id, timestamp))
                if len(first_items) >= 10:
                    break

        seen_items = set()
        last_items = []
        for item_id, timestamp in reversed(self.last_item_mentions):
            if item_id not in seen_items:
                seen_items.add(item_id)
                last_items.append((item_id, timestamp))
                if len(last_items) >= 10:
                    break
        last_items.reverse()
        
        return {
            'top_items': top_items,
            'top_players': top_players,
            'first_items': first_items,
            'last_items': last_items
        }
    
    def interactive_mode(self):
        print("\nИнтерактивный режим")
        print("Для выхода введите 'exit'")
        
        while True:
            try:
                user_input = raw_input("\nВведите item_type_id для поиска: ").strip()
                if user_input.lower() == 'exit':
                    break
                
                item_type_id = int(user_input)
                self._query_item_info(item_type_id)
                
            except ValueError:
                print("Пожалуйста, введите корректный числовой item_type_id")
            except KeyboardInterrupt:
                break
            except Exception as e:
                print("Произошла ошибка: %s" % str(e))
    
    def _query_item_info(self, item_type_id):
        total_count = 0
        players_with_item = 0
        player_counts = []
        
        for player in self.players.values():
            count = player.get_item_count(item_type_id)
            if count > 0:
                total_count += count
                players_with_item += 1
                player_counts.append((player.player_id, count))
        
        player_counts.sort(key=lambda x: x[1], reverse=True)
        top_10_players = player_counts[:10]
        
        print("\nИнфо о предмете %s:" % item_type_id)
        print("Предмет: %s" % item_type_id)
        print("Всего в игре: %s" % total_count)
        print("Количество игроков, у которых есть: %s" % players_with_item)
        print("Топ 10 игроков по количеству")
        print("Имя игрока, количество предметов")
        for player_id, count in top_10_players:
            print("%s, %s" % (player_id, count))