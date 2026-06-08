# FPGA Agent — AI-Powered FPGA Signal Processing Design (Eclypse Z7 Port)

An AI-assisted visual design environment for FPGA-based signal processing systems. Originally built for Kintex UltraScale FPGAs, **this specific fork has been natively ported to support the Digilent Eclypse Z7 (Zynq-7000 SoC)** and its SYZYGY Zmod ADC/DAC interfaces.

## Architecture

```text
┌─────────────────────────────────────────────────────────┐
│                    FPGA Agent (PySide6)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Graph Canvas│  │  AI Chat     │  │  Code Gen     │  │
│  │  (drag-drop) │  │  (LLM agent) │  │  (VHDL output)│  │
│  └──────┬───────┘  └──────┬───────┘  └───────────────┘  │
│         │                 │                             │
│  ┌──────┴─────────────────┴──────────────────────────┐  │
│  │              Tool Executor                        │  │
│  │  create_module / connect_modules / set_parameter  │  │
│  └──────────────────────┬────────────────────────────┘  │
│                         │                               │
│  ┌──────────────────────┴────────────────────────────┐  │
│  │           Qt GUI (python control)                 │  │
│  │  MainWindow / UART / SPI / Bus / Module Registry  │  │
│  └──────────────────────┬────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────┘
                          │ UART
┌─────────────────────────┼───────────────────────────────┐
│           Eclypse Z7 (Zynq-7000) / Kintex FPGA          │
│  ┌──────────┐  ┌──────┐  ┌─────┐  ┌──────┐  ┌───────┐   │
│  │ Zmod ADC/│  │ PID  │  │ IIR │  │ Mixer│  │PDH FSM│   │
│  │ DAC I/O  │  │ctrl  │  │filter│  │      │  │       │   │
│  └──────────┘  └──────┘  └─────┘  └──────┘  └───────┘   │
└─────────────────────────────────────────────────────────┘
```

## Eclypse Z7 Port Considerations

This branch integrates the **Eclypse Z7** directly into the project's architecture:
1. **DClocking Integration:** The former `DClocking` submodule has been un-linked and fully integrated directly into this repository to simplify cloning and tracking custom VHDL changes.
2. **Hardware Adapter:** The `EclypseZ7_adapter.vhdl` (located in `DClocking/io management/`) is built to bridge the internal dual-clocking signal ecosystem with the physical Zmod ADC 1410 and Zmod DAC 1411 ports.
3. **Configuration Registry:** Python backend code (`configuration_list.py`) officially registers the `EclypseZ7` chip layout to allow the LLM to successfully auto-generate the `Top.vhdl` wrapper.
4. **Constraints:** Top-level physical constraints for the SYZYGY headers are located in `DClocking/eclypse_z7.xdc`.

## Quick Start

### 1. Prerequisites

```bash
pip install PySide6 numpy pillow pyserial
```

### 2. Configure LLM Backend

Edit `DClocking/FPGA_Agent/config.json`:
```json
{
  "llm": {
    "endpoint": "https://api.deepseek.com/v1",
    "api_key": "your-api-key-here",
    "model": "deepseek-chat",
    "temperature": 0.1,
    "max_tokens": 4096
  }
}
```

### 3. Hardware COM Port Configuration (Crucial for Testing)
To successfully interface with your physical Eclypse Z7 board, ensure you update the serial COM port in `DClocking/python control/env.py` (Line 13) to match the port assigned by your OS:
```python
# Change "COM9" to your specific board port
ser = uart.MySerial("COM9", baudrate = 115200, parity = "E", timeout = 0.5)
```

### 4. Launch the GUI + Agent

```bash
cd DClocking
python -m FPGA_Agent.main
```

## Agent Usage Examples

Type these in the AI chat panel to build your system:
- "Initialize the Eclypse Z7 adapter."
- "Build a complete PDH lock pipeline"
- "Create a 10 MHz sine wave generator"
- "Add a low-pass filter with 1 kHz cutoff"

## Original Developer Credit
- This is a fork of the DClocking and FPGA_Agent framework created by [hosinonisiki](https://github.com/hosinonisiki/DClocking).
