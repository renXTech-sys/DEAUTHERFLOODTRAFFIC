# DEAUTHERFLOODTRAFFIC

For Educational Only

A Python-based CLI tool designed to test network interfaces, sockets, and VPS throughput using simultaneous high-frequency multi-threading (TX/RX storming).

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## Features

- **Simultaneous Dual-Storm:** Runs isolated TX (Upload) and RX (Download) worker threads in parallel.
- **High-Throughput Socket Buffer:** Employs custom 1 MB socket buffer configurations for maximum payload stress.
- **Live Terminal UI:** Powered by `rich` to show live Mbps, Gbps, total transferred payload, and drop rates.
- **Custom ASCII Visuals:** Integrated ASCII branding headers for menu and execution screens.

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/renXTech-sys/DEAUTHERFLOODTRAFFIC.git](https://github.com/renXTech-sys/DEAUTHERFLOODTRAFFIC.git)
   cd DEAUTHERFLOODTRAFFIC
   pip install rich
   python renx-st.py
