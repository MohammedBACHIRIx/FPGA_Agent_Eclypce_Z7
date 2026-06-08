library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity EclypseZ7_adapter is
    port (
        sys_clk_250M    :   in  std_logic;
        sys_clk_125M    :   in  std_logic;
        sys_rst         :   in  std_logic;
        jesd204_rst     :   in  std_logic;
        adc_a_data      :   out std_logic_vector(15 downto 0);
        adc_b_data      :   out std_logic_vector(15 downto 0);
        dac_a_data      :   in  std_logic_vector(15 downto 0);
        dac_b_data      :   in  std_logic_vector(15 downto 0);
        spi_ss          :   in  std_logic_vector(0 to 3);
        spi_sck         :   in  std_logic;
        spi_mosi        :   in  std_logic;
        spi_miso        :   out std_logic;
        spi_io_tri      :   in  std_logic;
        
        -- SYZYGY ports for Zmod
        syzygy_a_p      :   inout std_logic_vector(15 downto 0);
        syzygy_a_n      :   inout std_logic_vector(15 downto 0);
        syzygy_b_p      :   inout std_logic_vector(15 downto 0);
        syzygy_b_n      :   inout std_logic_vector(15 downto 0)
    );
end EclypseZ7_adapter;

architecture Behavioral of EclypseZ7_adapter is
begin
    -- Stub implementation for Eclypse Z7 Zmod ADC/DAC
    adc_a_data <= (others => '0');
    adc_b_data <= (others => '0');
    spi_miso <= '0';
end Behavioral;
