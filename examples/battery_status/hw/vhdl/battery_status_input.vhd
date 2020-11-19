-- Copyright 2018-2019 Delft University of Technology
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
--     http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.
--
-- This file was generated by Fletchgen. Modify this file at your own risk.

library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

library work;
use work.Array_pkg.all;

entity battery_status_input is
  generic (
    INDEX_WIDTH                    : integer := 32;
    TAG_WIDTH                      : integer := 1;
    INPUT_INPUT_BUS_ADDR_WIDTH     : integer := 64;
    INPUT_INPUT_BUS_DATA_WIDTH     : integer := 512;
    INPUT_INPUT_BUS_LEN_WIDTH      : integer := 8;
    INPUT_INPUT_BUS_BURST_STEP_LEN : integer := 1;
    INPUT_INPUT_BUS_BURST_MAX_LEN  : integer := 16
  );
  port (
    bcd_clk                    : in std_logic;
    bcd_reset                  : in std_logic;
    kcd_clk                    : in std_logic;
    kcd_reset                  : in std_logic;
    input_input_valid          : out std_logic;
    input_input_ready          : in std_logic;
    input_input_dvalid         : out std_logic;
    input_input_last           : out std_logic;
    input_input                : out std_logic_vector(63 downto 0);
    input_input_count          : out std_logic_vector(3 downto 0);
    input_input_bus_rreq_valid : out std_logic;
    input_input_bus_rreq_ready : in std_logic;
    input_input_bus_rreq_addr  : out std_logic_vector(INPUT_INPUT_BUS_ADDR_WIDTH - 1 downto 0);
    input_input_bus_rreq_len   : out std_logic_vector(INPUT_INPUT_BUS_LEN_WIDTH - 1 downto 0);
    input_input_bus_rdat_valid : in std_logic;
    input_input_bus_rdat_ready : out std_logic;
    input_input_bus_rdat_data  : in std_logic_vector(INPUT_INPUT_BUS_DATA_WIDTH - 1 downto 0);
    input_input_bus_rdat_last  : in std_logic;
    input_input_cmd_valid      : in std_logic;
    input_input_cmd_ready      : out std_logic;
    input_input_cmd_firstIdx   : in std_logic_vector(INDEX_WIDTH - 1 downto 0);
    input_input_cmd_lastIdx    : in std_logic_vector(INDEX_WIDTH - 1 downto 0);
    input_input_cmd_ctrl       : in std_logic_vector(INPUT_INPUT_BUS_ADDR_WIDTH - 1 downto 0);
    input_input_cmd_tag        : in std_logic_vector(TAG_WIDTH - 1 downto 0);
    input_input_unl_valid      : out std_logic;
    input_input_unl_ready      : in std_logic;
    input_input_unl_tag        : out std_logic_vector(TAG_WIDTH - 1 downto 0)
  );
end entity;

architecture Implementation of battery_status_input is
  -- signal input_inst_bcd_clk        : std_logic;
  signal input_inst_bcd_reset      : std_logic;

  -- signal input_inst_kcd_clk        : std_logic;
  signal input_inst_kcd_reset      : std_logic;

  signal input_inst_cmd_valid      : std_logic;
  signal input_inst_cmd_ready      : std_logic;
  signal input_inst_cmd_firstIdx   : std_logic_vector(INDEX_WIDTH - 1 downto 0);
  signal input_inst_cmd_lastIdx    : std_logic_vector(INDEX_WIDTH - 1 downto 0);
  signal input_inst_cmd_ctrl       : std_logic_vector(INPUT_INPUT_BUS_ADDR_WIDTH - 1 downto 0);
  signal input_inst_cmd_tag        : std_logic_vector(TAG_WIDTH - 1 downto 0);

  signal input_inst_unl_valid      : std_logic;
  signal input_inst_unl_ready      : std_logic;
  signal input_inst_unl_tag        : std_logic_vector(TAG_WIDTH - 1 downto 0);

  signal input_inst_bus_rreq_valid : std_logic;
  signal input_inst_bus_rreq_ready : std_logic;
  signal input_inst_bus_rreq_addr  : std_logic_vector(INPUT_INPUT_BUS_ADDR_WIDTH - 1 downto 0);
  signal input_inst_bus_rreq_len   : std_logic_vector(INPUT_INPUT_BUS_LEN_WIDTH - 1 downto 0);
  signal input_inst_bus_rdat_valid : std_logic;
  signal input_inst_bus_rdat_ready : std_logic;
  signal input_inst_bus_rdat_data  : std_logic_vector(INPUT_INPUT_BUS_DATA_WIDTH - 1 downto 0);
  signal input_inst_bus_rdat_last  : std_logic;

  signal input_inst_out_valid      : std_logic_vector(0 downto 0);
  signal input_inst_out_ready      : std_logic_vector(0 downto 0);
  signal input_inst_out_data       : std_logic_vector(67 downto 0);
  signal input_inst_out_dvalid     : std_logic_vector(0 downto 0);
  signal input_inst_out_last       : std_logic_vector(0 downto 0);

begin
  input_inst : ArrayReader
  generic map(
    BUS_ADDR_WIDTH     => INPUT_INPUT_BUS_ADDR_WIDTH,
    BUS_DATA_WIDTH     => INPUT_INPUT_BUS_DATA_WIDTH,
    BUS_LEN_WIDTH      => INPUT_INPUT_BUS_LEN_WIDTH,
    BUS_BURST_STEP_LEN => INPUT_INPUT_BUS_BURST_STEP_LEN,
    BUS_BURST_MAX_LEN  => INPUT_INPUT_BUS_BURST_MAX_LEN,
    INDEX_WIDTH        => INDEX_WIDTH,
    CFG                => "prim(8;epc=8)",
    CMD_TAG_ENABLE     => true,
    CMD_TAG_WIDTH      => TAG_WIDTH
  )
  port map(
    bcd_clk        => bcd_clk,
    bcd_reset      => input_inst_bcd_reset,
    kcd_clk        => kcd_clk,
    kcd_reset      => input_inst_kcd_reset,
    cmd_valid      => input_inst_cmd_valid,
    cmd_ready      => input_inst_cmd_ready,
    cmd_firstIdx   => input_inst_cmd_firstIdx,
    cmd_lastIdx    => input_inst_cmd_lastIdx,
    cmd_ctrl       => input_inst_cmd_ctrl,
    cmd_tag        => input_inst_cmd_tag,
    unl_valid      => input_inst_unl_valid,
    unl_ready      => input_inst_unl_ready,
    unl_tag        => input_inst_unl_tag,
    bus_rreq_valid => input_inst_bus_rreq_valid,
    bus_rreq_ready => input_inst_bus_rreq_ready,
    bus_rreq_addr  => input_inst_bus_rreq_addr,
    bus_rreq_len   => input_inst_bus_rreq_len,
    bus_rdat_valid => input_inst_bus_rdat_valid,
    bus_rdat_ready => input_inst_bus_rdat_ready,
    bus_rdat_data  => input_inst_bus_rdat_data,
    bus_rdat_last  => input_inst_bus_rdat_last,
    out_valid      => input_inst_out_valid,
    out_ready      => input_inst_out_ready,
    out_data       => input_inst_out_data,
    out_dvalid     => input_inst_out_dvalid,
    out_last       => input_inst_out_last
  );

  input_input_valid          <= input_inst_out_valid(0);
  input_inst_out_ready(0)    <= input_input_ready;
  input_input_dvalid         <= input_inst_out_dvalid(0);
  input_input_last           <= input_inst_out_last(0);
  input_input                <= input_inst_out_data(63 downto 0);
  input_input_count          <= input_inst_out_data(67 downto 64);

  input_input_bus_rreq_valid <= input_inst_bus_rreq_valid;
  input_inst_bus_rreq_ready  <= input_input_bus_rreq_ready;
  input_input_bus_rreq_addr  <= input_inst_bus_rreq_addr;
  input_input_bus_rreq_len   <= input_inst_bus_rreq_len;
  input_inst_bus_rdat_valid  <= input_input_bus_rdat_valid;
  input_input_bus_rdat_ready <= input_inst_bus_rdat_ready;
  input_inst_bus_rdat_data   <= input_input_bus_rdat_data;
  input_inst_bus_rdat_last   <= input_input_bus_rdat_last;

  input_input_unl_valid      <= input_inst_unl_valid;
  input_inst_unl_ready       <= input_input_unl_ready;
  input_input_unl_tag        <= input_inst_unl_tag;

  -- input_inst_bcd_clk         <= bcd_clk;
  input_inst_bcd_reset       <= bcd_reset;

  -- input_inst_kcd_clk         <= kcd_clk;
  input_inst_kcd_reset       <= kcd_reset;

  input_inst_cmd_valid       <= input_input_cmd_valid;
  input_input_cmd_ready      <= input_inst_cmd_ready;
  input_inst_cmd_firstIdx    <= input_input_cmd_firstIdx;
  input_inst_cmd_lastIdx     <= input_input_cmd_lastIdx;
  input_inst_cmd_ctrl        <= input_input_cmd_ctrl;
  input_inst_cmd_tag         <= input_input_cmd_tag;

end architecture;