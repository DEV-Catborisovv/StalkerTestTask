# -*- coding: utf-8 -*-

from collections import defaultdict

class Player:
    def __init__(self, player_id):
        self.player_id = player_id
        self.money = 0
        self.inventory = defaultdict(int)
        self.first_mention = None
        self.last_mention = None
        
    def add_money(self, amount, timestamp):
        self.money += amount
        self._update_timestamps(timestamp)
        
    def remove_money(self, amount, timestamp):
        self.money -= amount
        self._update_timestamps(timestamp)
        
    def add_item(self, item_type_id, amount, timestamp):
        self.inventory[item_type_id] += amount
        self._update_timestamps(timestamp)
        
    def remove_item(self, item_type_id, amount, timestamp):
        self.inventory[item_type_id] -= amount
        if self.inventory[item_type_id] < 0:
            self.inventory[item_type_id] = 0
        self._update_timestamps(timestamp)
        
    def _update_timestamps(self, timestamp):
        if self.first_mention is None or timestamp < self.first_mention:
            self.first_mention = timestamp
        if self.last_mention is None or timestamp > self.last_mention:
            self.last_mention = timestamp
            
    def get_item_count(self, item_type_id):
        return self.inventory.get(item_type_id, 0)