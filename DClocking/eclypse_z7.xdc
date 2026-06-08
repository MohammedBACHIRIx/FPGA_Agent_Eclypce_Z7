## Eclypse Z7 Zmod ADC and DAC constraints
# System Clock
set_property -dict { PACKAGE_PIN D18   IOSTANDARD LVCMOS33 } [get_ports { sys_clk_125M }];
create_clock -add -name sys_clk_pin -period 8.00 -waveform {0 4} [get_ports { sys_clk_125M }];

# SYZYGY A (e.g. Zmod ADC)
# SYZYGY B (e.g. Zmod DAC)
# (Stub file for Eclypse Z7 porting)
