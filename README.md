# FPGA Agent — AI-Powered FPGA Signal Processing Design

An AI-assisted visual design environment for FPGA-based signal processing systems. Built around a dual optical comb feedback locking (DClocking) engine running on Xilinx Kintex UltraScale FPGAs.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FPGA Agent (PySide6)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │  Graph Canvas │  │  AI Chat     │  │  Code Gen     │  │
│  │  (drag-drop)  │  │  (LLM agent) │  │  (VHDL output)│  │
│  └──────┬───────┘  └──────┬───────┘  └───────────────┘  │
│         │                 │                              │
│  ┌──────┴─────────────────┴──────────────────────────┐  │
│  │              Tool Executor                         │  │
│  │  create_module / connect_modules / set_parameter   │  │
│  └──────────────────────┬────────────────────────────┘  │
│                         │                               │
│  ┌──────────────────────┴────────────────────────────┐  │
│  │           Qt GUI (python control)                  │  │
│  │  MainWindow / UART / SPI / Bus / Module Registry   │  │
│  └──────────────────────┬────────────────────────────┘  │
└─────────────────────────┼───────────────────────────────┘
                          │ UART
┌─────────────────────────┼───────────────────────────────┐
│              FPGA (Kintex UltraScale)                    │
│  ┌──────────┐  ┌──────┐  ┌─────┐  ┌──────┐  ┌───────┐  │
│  │ ADC/DAC  │  │ PID  │  │ IIR │  │ Mixer│  │PDH FSM│  │
│  │ adapters │  │ctrl  │  │filter│  │      │  │       │  │
│  └──────────┘  └──────┘  └─────┘  └──────┘  └───────┘  │
│  ┌──────────┐  ┌──────┐  ┌─────┐  ┌──────────────────┐  │
│  │ Signal   │  │Trig  │  │Scaler│  │Waveform Storage  │  │
│  │ Router   │  │      │  │      │  │(DDR4 + Ethernet) │  │
│  └──────────┘  └──────┘  └─────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## Project Structure

```
FPGA_Agent/
├── DClocking/                  # Git submodule → hosinonisiki/DClocking
│   ├── FPGA_Agent/             # AI agent core
│   │   ├── main.py             # Entry point
│   │   ├── agent_core.py       # LLM interaction loop
│   │   ├── agent_chat_widget.py# Chat UI panel
│   │   ├── canvas_bridge.py    # Graph ↔ tools bridge
│   │   ├── code_generator.py   # VHDL code generation
│   │   ├── llm_client.py       # OpenAI-compatible API client
│   │   ├── tool_definitions.py # Agent tool schemas
│   │   ├── tool_executor.py    # Tool execution logic
│   │   ├── module_registry.py  # Available HW modules
│   │   ├── prompts/            # System prompts
│   │   ├── generated/          # Auto-generated schemas
│   │   └── config.json         # LLM & agent settings
│   ├── python control/         # Qt GUI & communication
│   │   ├── qt_ui_mainwindow.py # Main GUI window
│   │   ├── qt_ui_graph.py      # Signal graph widget
│   │   ├── qt_module.py        # Module control panel
│   │   ├── uart.py / spi.py    # Serial protocols
│   │   ├── bus.py              # On-chip bus abstraction
│   │   ├── module.py           # Module base classes
│   │   └── ...
│   ├── modules/                # VHDL signal processing IP
│   │   ├── pid_controller/     # PID feedback
│   │   ├── iir_filter/         # IIR biquad filter
│   │   ├── fir_filter/         # FIR filter
│   │   ├── mixer/              # Signal demodulator
│   │   ├── trigonometric/      # Sine/cosine generator
│   │   ├── accumulator/        # Phase accumulator (NCO)
│   │   ├── scaler/             # Linear scaling
│   │   ├── pdh_state_machine/  # PDH lock state machine
│   │   ├── signal_router/      # Crossbar signal switch
│   │   └── waveform_storage_upload/ # DDR4 + Ethernet capture
│   ├── io management/          # ADC/DAC board adapters
│   ├── packages/               # VHDL package files
│   ├── templates/              # Module code templates
│   └── products/               # Built bitstreams
├── QuantityEntry.py            # Standalone Tkinter quantity entry widget
└── diagram_config.json         # Diagram layout configuration
```

## Key Features

| Feature | Description |
|---------|-------------|
| **AI-Assisted Design** | Natural language → FPGA signal processing pipeline |
| **Visual Graph Editor** | Drag-and-drop module placement and wiring |
| **LLM Backend** | Supports OpenAI, DeepSeek, or any OpenAI-compatible API |
| **VHDL Code Generation** | Generates module VHDL from requirements |
| **Real Hardware Control** | UART/SPI communication with Kintex UltraScale FPGA |
| **PDH Locking** | Complete Pound-Drever-Hall feedback locking pipeline |
| **Modular IP Library** | PID, IIR, FIR, mixer, NCO, trigonometric, scaler, etc. |

## Quick Start

### Prerequisites

```bash
pip install PySide6 numpy pillow pyserial
```

### Launch the GUI + Agent

```bash
cd DClocking
python -m FPGA_Agent.main
```

### Launch the Standalone Quantity Entry

```bash
python QuantityEntry.py
```

### Configure LLM Backend

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

## Agent Usage Examples

Type these in the chat panel:

- "帮我搭建一个 PDH 锁定系统" — Build a complete PDH lock pipeline
- "创建一个 10 MHz 的正弦波发生器" — Create a sine wave generator
- "添加一个低通滤波器，截止频率 1 kHz" — Add low-pass filter
- "把 PID 的增益设置为 0.5" — Set PID gain

## Hardware Support

| FPGA Board | Adapter |
|-----------|---------|
| FH8052 | `FH8052_adapter` |
| FH9767D | `FH9767D_adapter` |
| FL9613 | `FL9613_adapter` |
| FL9627 | `FL9627_adapter` |
| FL9781 | `FL9781_adapter` |
| FL1010 | `FL1010_adapter` |
| AN9767 | `AN9767_adapter` |
| PZ-KU060-FHT | Custom wrapper |
| KU060 Custom | Custom wrapper |`n| Eclypse Z7 | `EclypseZ7_adapter` |

## Related Repositories

- [hosinonisiki/DClocking](https://github.com/hosinonisiki/DClocking) — FPGA VHDL source & Python control (submodule)
