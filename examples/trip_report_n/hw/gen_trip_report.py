import os
import argparse
from string import Template

import pyarrow as pa
from pyfletchgen.lib import fletchgen

import vhdmmio

parser = argparse.ArgumentParser(description="Generate a kernel with N parser instances.")
parser.add_argument("parsers", type=int, help="Number of parser instances.")
args = parser.parse_args()

assert 16 >= args.parsers > 0

parsers = args.parsers

KERNEL_NAME = 'trip_report'

VHDMMIO_YAML = """
metadata:
  name: mmio
entity:
  bus-flatten:  yes
  bus-prefix:   mmio_
  clock-name:   kcd_clk
  reset-name:   kcd_reset
features:
  bus-width:    64
  optimize:     yes
interface:
  flatten:      yes
fields:
  - address: 0b0---
    name: AFU_DHF
    behavior: constant
    value: 17293826967149215744 # [63:60]: 1 && [40]: 1
  - address: 0b1---
    name: AFU_ID_L
    behavior: constant
    value: {afuidint} # check trip-report.json
  - address: 0b10---
    name: AFU_ID_H
    behavior: constant
    value: 11287216594519869704 # check trip_report.json
  - address: 0b11---
    name: DFH_RSVD0
    behavior: constant
    value: 0
  - address: 0b100---
    name: DFH_RSVD1
    behavior: constant
    value: 0
{fletchgen}
"""

OPAE_JSON = """{{
  "version": 1,
  "afu-image": {{
    "power": 0,
    "clock-frequency-high": "auto",
    "clock-frequency-low": "auto",
    "afu-top-interface": {{
      "name": "ofs_plat_afu"
    }},
    "accelerator-clusters": [
      {{
        "name": "trip-report",
        "total-contexts": 1,
        "accelerator-type-uuid": "9ca43fb0-c340-4908-b79b-5c89b4ef5e{n:02X}"
      }}
    ]
  }}
}}
"""


def emphasize(s):
    """Like print(), but emphasizes the line using ANSI escape sequences."""
    print('\n\033[1m{}\033[0m'.format(s))


def input_schema(idx):
    return pa.schema([
        pa.field("input", pa.uint8(), False).with_metadata({b"fletcher_epc": b"8"})
    ]).with_metadata({
        b"fletcher_mode": b"read",
        b"fletcher_name": "input_{:02}".format(idx).encode('ascii')
    })


output_schema = pa.schema([pa.field("timestamp", pa.utf8(), False).with_metadata({
    b'fletcher_epc': b'1'
}),
    pa.field("tag", pa.uint64(), False),
    pa.field("timezone", pa.uint64(), False),
    pa.field("vin", pa.uint64(), False),
    pa.field("odometer", pa.uint64(), False),
    pa.field("hypermiling", pa.uint8(), False),
    pa.field("avgspeed", pa.uint64(), False),
    pa.field("sec_in_band", pa.list_(pa.field("item", pa.uint64(), False)), False),
    pa.field("miles_in_time_range", pa.list_(pa.field("item", pa.uint64(), False)), False),
    pa.field("const_speed_miles_in_band", pa.list_(pa.field("item", pa.uint64(), False)), False),
    pa.field("vary_speed_miles_in_band", pa.list_(pa.field("item", pa.uint64(), False)), False),
    pa.field("sec_decel", pa.list_(pa.field("item", pa.uint64(), False)), False),
    pa.field("sec_accel", pa.list_(pa.field("item", pa.uint64(), False)), False),
    pa.field("braking", pa.list_(pa.field("item", pa.uint64(), False)), False),
    pa.field("accel", pa.list_(pa.field("item", pa.uint64(), False)), False),
    pa.field("orientation", pa.uint8(), False),
    pa.field("small_speed_var", pa.list_(pa.field("item", pa.uint64(), False)), False),
    pa.field("large_speed_var", pa.list_(pa.field("item", pa.uint64(), False)), False),
    pa.field("accel_decel", pa.uint64(), False),
    pa.field("speed_changes", pa.uint64(), False)

]).with_metadata({
    b'fletcher_mode': b'write',
    b'fletcher_name': b'output'
})


def generate_schema_files(num_parsers):
    files = []
    file_out = "schemas/out_.as"
    pa.output_stream(file_out).write(output_schema.serialize())
    files.append(file_out)
    for i in range(0, num_parsers):
        file_in = "schemas/in_{:02}.as".format(i)
        schema_in = input_schema(i)
        pa.output_stream(file_in).write(schema_in.serialize())
        files.append(file_in)
    return files


emphasize("Generating schemas...")

# prepare output folder for schemas
if not os.path.exists('schemas'):
    os.makedirs('schemas')

schema_files = generate_schema_files(args.parsers)

# prepare registers
registers = [['c:32:parser_{:02}_tag'.format(i)]
             for i in range(0, args.parsers)]
registers = [item for sublist in registers for item in sublist]  # flatten list

emphasize("Running fletchgen...")

fletchgen(
    '-i', *schema_files,
    '-n', KERNEL_NAME,
    '--regs', *registers,
    '-l', 'vhdl',
    '--mmio64',
    '--mmio-offset', str(64),
    '--static-vhdl',
    '--axi'
)

INPUT_PORTS = ""
for i in range(0, args.parsers):
    INPUT_PORTS = INPUT_PORTS + """\
    input_{idx:02}_input_valid                          : in std_logic;
    input_{idx:02}_input_ready                          : out std_logic;
    input_{idx:02}_input_dvalid                         : in std_logic;
    input_{idx:02}_input_last                           : in std_logic;
    input_{idx:02}_input                                : in std_logic_vector(63 downto 0);
    input_{idx:02}_input_count                          : in std_logic_vector(3 downto 0);
    input_{idx:02}_input_unl_valid                      : in std_logic;
    input_{idx:02}_input_unl_ready                      : out std_logic;
    input_{idx:02}_input_unl_tag                        : in std_logic_vector(TAG_WIDTH - 1 downto 0);
    input_{idx:02}_input_cmd_valid                      : out std_logic;
    input_{idx:02}_input_cmd_ready                      : in std_logic;
    input_{idx:02}_input_cmd_firstIdx                   : out std_logic_vector(INDEX_WIDTH - 1 downto 0);
    input_{idx:02}_input_cmd_lastIdx                    : out std_logic_vector(INDEX_WIDTH - 1 downto 0);
    input_{idx:02}_input_cmd_tag                        : out std_logic_vector(TAG_WIDTH - 1 downto 0);
    input_{idx:02}_firstidx                             : in  std_logic_vector(31 downto 0);
    input_{idx:02}_lastidx                              : in  std_logic_vector(31 downto 0);
    
""".format(idx=i)

TYDI_STRB = ""
for i in range(0, args.parsers):
    TYDI_STRB = TYDI_STRB + """\
    tydi_strb_{idx:02} : process (input_{idx:02}_input_dvalid, input_{idx:02}_input_count)
    begin
      in_strb(EPC * ({idx}+1)-1 downto EPC * {idx}) <= (others => '0');
      for i in EPC-1 downto 0 loop
        if unsigned(input_{idx:02}_input_count) = 0 or i < unsigned(input_{idx:02}_input_count) then
          in_strb(EPC*{idx} + i) <= input_{idx:02}_input_dvalid;
        end if;
      end loop;
    end process;
    
""".format(idx=i)

TYDI_LAST = ""
for i in range(0, args.parsers):
    TYDI_LAST = TYDI_LAST + """\
  tydi_last_{idx:02} : process (input_{idx:02}_input_last)
  begin
    in_last(EPC * 2 * ({idx}+1)-1 downto EPC * 2 * {idx}) <= (others => '0');
    -- all records are currently sent in one transfer, so there's no difference
    -- between the two dimensions going into the parser.
    in_last(EPC * 2 * ({idx}+1) - 2) <= input_{idx:02}_input_last;
    in_last(EPC * 2 * ({idx}+1) - 1) <= input_{idx:02}_input_last;
  end process;
  
""".format(idx=i)

SYNC_IN_UNL_MAP = ""
for i in range(0, args.parsers):
    SYNC_IN_UNL_MAP = SYNC_IN_UNL_MAP + """\
      in_valid({idx})             => input_{idx:02}_input_unl_valid,
""".format(idx=i)
for i in range(0, args.parsers):
    if i != args.parsers - 1:
        SYNC_IN_UNL_MAP = SYNC_IN_UNL_MAP + """\
      in_ready({idx})             => input_{idx:02}_input_unl_ready,
""".format(idx=i)
    else:
        SYNC_IN_UNL_MAP = SYNC_IN_UNL_MAP + """\
      in_ready({idx})             => input_{idx:02}_input_unl_ready
""".format(idx=i)

SYNC_IN_UNL = """\
sync_in_unl: StreamSync
    generic map (
      NUM_INPUTS              => {num_parsers},
      NUM_OUTPUTS             => 1
    )
    port map (
      clk                     => kcd_clk,
      reset                   => kcd_reset,
      
      out_valid(0)            => in_unl_valid,
      out_ready(0)            => in_unl_ready,  
{sync_in_unl_map}  
  );
""".format(num_parsers=args.parsers, sync_in_unl_map=SYNC_IN_UNL_MAP)

SYNC_IN_CMD_MAP = ""
for i in range(0, args.parsers):
    SYNC_IN_CMD_MAP = SYNC_IN_CMD_MAP + """\
      out_valid({idx})            => input_{idx:02}_input_cmd_valid,
""".format(idx=i)
for i in range(0, args.parsers):
    if i != args.parsers - 1:
        SYNC_IN_CMD_MAP = SYNC_IN_CMD_MAP + """\
      out_ready({idx})            => input_{idx:02}_input_cmd_ready,
""".format(idx=i)
    else:
        SYNC_IN_CMD_MAP = SYNC_IN_CMD_MAP + """\
      out_ready({idx})            => input_{idx:02}_input_cmd_ready
""".format(idx=i)

SYNC_IN_CMD = """\
sync_in_cmd: StreamSync
    generic map (
      NUM_INPUTS              => 1,
      NUM_OUTPUTS             => {num_parsers}
    )
    port map (
      clk                     => kcd_clk,
      reset                   => kcd_reset,
      
      in_valid(0)             => in_cmd_valid,
      in_ready(0)             => in_cmd_ready,
{sync_in_cmd_map}  
  );
""".format(num_parsers=args.parsers, sync_in_cmd_map=SYNC_IN_CMD_MAP)

READ_REQ_DEFAULTS = ""
for i in range(0, args.parsers):
    READ_REQ_DEFAULTS = READ_REQ_DEFAULTS + """\
  input_{idx:02}_input_cmd_firstIdx                         <= input_{idx:02}_firstidx;
  input_{idx:02}_input_cmd_lastIdx                          <= input_{idx:02}_lastidx;
  input_{idx:02}_input_cmd_tag                              <= (others => '0');
    
""".format(idx=i)

INST_IN_VALID = ""
for i in range(0, args.parsers):
    INST_IN_VALID = INST_IN_VALID + """\
    in_valid({idx})                                 => input_{idx:02}_input_valid,
""".format(idx=i)

INST_IN_READY = ""
for i in range(0, args.parsers):
    INST_IN_READY = INST_IN_READY + """\
    in_ready({idx})                                 => input_{idx:02}_input_ready,
""".format(idx=i)

INST_IN_DATA= ""
for i in range(0, args.parsers):
    INST_IN_DATA = INST_IN_DATA + """\
    in_data(8*EPC*({idx}+1)-1 downto 8*EPC*{idx})       => input_{idx:02}_input,
""".format(idx=i)

TAG_CFG= ""
for i in range(0, args.parsers):
    if i != args.parsers-1:
        TAG_CFG = TAG_CFG + """\
    tag_CFG(32*({idx}+1)-1 downto 32*{idx})             => parser_{idx:02}_tag,
""".format(idx=i)
    else:
        TAG_CFG = TAG_CFG + """\
    tag_CFG(32*({idx}+1)-1 downto 32*{idx})             => parser_{idx:02}_tag
""".format(idx=i)

MMIO=""
for i in range(0, args.parsers):
    MMIO = MMIO + """\
    parser_{idx:02}_tag                                 : in std_logic_vector(31 downto 0);
""".format(idx=i)

emphasize("Generating kernel source...")
template = open('template/kernel.tmpl')
# src = Template(template.read())
kernel = template.read().format(input_ports=INPUT_PORTS, mmio=MMIO, tydi_strb=TYDI_STRB, tydi_last=TYDI_LAST,
                                read_req_defaults=READ_REQ_DEFAULTS, sync_in_unl=SYNC_IN_UNL, sync_in_cmd=SYNC_IN_CMD,
                                in_valid=INST_IN_VALID, in_ready=INST_IN_READY, in_data=INST_IN_DATA, tag_cfg=TAG_CFG,
                                num_parsers=args.parsers)
# Write the kernel source
kernel_file = 'vhdl/{}.gen.vhd'.format(KERNEL_NAME)
with open(kernel_file, 'w') as f:
    f.write(kernel)

print("Wrote kernel source to: " + kernel_file)

emphasize("Re-running vhdmmio...")

base_afu_id = 0xb79b5c89b4ef5e00
base_afu_id += args.parsers

with open("fletchgen.mmio.yaml") as f:
    fletchgen_yaml_part = f.readlines()[18:]

vhdmmio_source = VHDMMIO_YAML.format(afuidint=base_afu_id, fletchgen=''.join(fletchgen_yaml_part))
vhdmmio_file = "{}.mmio.yml".format(KERNEL_NAME)

with open(vhdmmio_file, 'w') as f:
    f.write(vhdmmio_source)

vhdmmio.run_cli(['-V', 'vhdl', '-P', 'vhdl', vhdmmio_file])

emphasize("Generating OPAE JSON...")
opae_json_file = "{}.json".format(KERNEL_NAME)
opae_json_source = OPAE_JSON.format(n=args.parsers)

with open(opae_json_file, 'w') as f:
    f.write(opae_json_source)

emphasize("Generating OPAE source list ...")

# Create list of recordbatch readers and writers
rbrs = '\n'.join(["vhdl/trip_report_input_{:02}.gen.vhd".format(i) for i in range(0, args.parsers)])
rbws = "\nvhdl/trip_report_output.gen.vhd"

template = open('template/sources.tmpl')
opae_json_file = "{}.json".format(KERNEL_NAME)

opae_sources_source = template.read().format(rbrs=rbrs, rbws=rbws)
opae_sources_file = "sources.txt"

with open(opae_sources_file, 'w') as f:
    f.write(opae_sources_source)

