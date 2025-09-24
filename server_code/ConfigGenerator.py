import anvil.server

"""
3MS Configuration Generator Script

Currently supports:
- URL-downloaded configurations
- File-downloaded configurations
- Main MCU configuration
- MMU MCU configuration
- Multi-MMU MCU configuration
- Per-stepper TMC driver selection
- Configurations with or without TMC drivers
"""

import io
import requests
import configparser

config = ''

def format_pin(pin, mcu):
    if not mcu: return pin
    prefixes = ''
    if '!' in pin: prefixes += '!'
    if '~' in pin: prefixes += '~'
    if '^' in pin: prefixes += '^'
    pin = pin.replace('!','').replace('~','').replace('^','')
    return f'{prefixes}{mcu}:{pin}'

def read_config_from_url(url):
    try:
      resp = requests.get(url)
      if resp.status_code != 200: return
      return resp.text
    except:
      return
  

def read_config_from_file(file):
    try:
      config = file.get_bytes().decode()
      return config
    except:
      return

def preprocess_config(config):
    updated_config = []
    in_section = False
    is_commented = False
    for line in config.splitlines():
        is_commented = False
        if line.startswith('#'):
            is_commented = True
            line = line[1:]
        if line.startswith('['):
            in_section = True
        if line.strip() == '' and in_section:
            in_section = False
        if is_commented and not in_section:
            line = f'#{line}'
        if in_section:
            updated_config.append(line)
        else:
            updated_config.append('\n')
    
    return '\n'.join(updated_config)

def get_parser(config):
    parser = configparser.RawConfigParser(strict=False, comment_prefixes=(';', '#'))
    parser.read_string(config)
    return parser

def extract_steppers(parser, rotation_distance=25, microsteps=16):
    sections = parser.sections()
    stepper_sections = {}
    for section in sections:
      step_pin = parser.get(section, 'step_pin', fallback=None)
      dir_pin = parser.get(section, 'dir_pin', fallback=None)
      en_pin = parser.get(section, 'enable_pin', fallback=None)
      if step_pin and dir_pin and en_pin:
          stepper_sections[section] = {
              'stepper_conf': {
                  'step_pin': step_pin,
                  'dir_pin': dir_pin,
                  'enable_pin': en_pin,
                  'rotation_distance': rotation_distance,
                  'microsteps': parser.get(section, 'microsteps', fallback=microsteps),
              },
          }
    return stepper_sections

def extract_tmc(parser, steppers):
    for section in parser.sections():
        if section.split()[-1] in steppers:
            if 'tmc' in section:
                tmc_options = {}
                for option in parser.options(section):
                    tmc_options[option] = parser.get(section, option)
                
                tmc_options['interpolate'] = parser.get(section, 'interpolate', fallback='True')
                tmc_options['sense_resistor'] = parser.get(section, 'sense_resistor', fallback='0.110')

                steppers[section.split()[-1]][section.split()[0]] = tmc_options
    return steppers

def format_all_pins(steppers, mcu_name, tmc_selections=None):
    for name, data in steppers.items():
            data['stepper_conf']['step_pin'] = format_pin(data['stepper_conf']['step_pin'], mcu_name)
            data['stepper_conf']['dir_pin'] = format_pin(data['stepper_conf']['dir_pin'], mcu_name)
            data['stepper_conf']['enable_pin'] = format_pin(data['stepper_conf']['enable_pin'], mcu_name)
            
            if tmc_selections:
                for opt, val in data[tmc_selections[name]].items():
                    if 'pin' in opt:
                        data[tmc_selections[name]][opt] = format_pin(val, mcu_name)
    return steppers

def generate_mmu_hardware(steppers, tmc_selections=None):
    writer = configparser.RawConfigParser(strict=False, comment_prefixes=(';', '#'), delimiters=(':',))
    
    i = 0
    for stepper, data in steppers.items():
        stepper_name = f'stepper_mmu_gear_{i}' if i > 0 else 'stepper_mmu_gear'
        writer.add_section(stepper_name)
        for key, val in data['stepper_conf'].items():
            writer.set(stepper_name, key, val)
        
        if tmc_selections:
            tmc_section = f'{tmc_selections[stepper]} {stepper_name}'
            writer.add_section(tmc_section)
            for key, val in data[tmc_selections[stepper]].items():
                writer.set(tmc_section, key, val)
        
        i += 1
    
    return writer

@anvil.server.callable
def get_config(method, url, file):
  if method == 'url':
    config = f'[cfggen_source]\nsource: url\nurl: {url}\n\n' + read_config_from_url(url)
  elif method == 'file':
    config = '\n\n\n' + read_config_from_file(file)
  try:
    config = preprocess_config(config)
  except:
    pass
  return config.strip()

@anvil.server.callable
def check_parsing(config):
  try:
    get_parser(preprocess_config(config))
    return True, None
  except Exception as e:
    return False, str(e)

@anvil.server.callable
def get_stepper_options(config):
  config = preprocess_config(config)
  parser = get_parser(config)
  steppers = extract_steppers(parser)
  return steppers

@anvil.server.callable
def get_tmc_options(config, steppers):
  parser = get_parser(config)
  tmc = extract_tmc(parser, steppers)
  return tmc

@anvil.server.callable
def generate_hardware_config(config, steppers, mcu_name):
  source_url = None
  temp_parser = get_parser(config)
  if temp_parser.has_section('cfggen_source'):
    if temp_parser.get('cfggen_source', 'source', fallback=None) == 'url':
      source_url = temp_parser.get('cfggen_source', 'url', fallback=None)

  soure_url_text = ''
  if source_url is not None:
    source_url_text = f'''#
# This configuration was generated from the following configuration:
# {source_url}'''
  
  tmc_options = {}
  for stepper, opts in steppers.items():
    for opt in opts:
      if 'tmc' in opt:
        tmc_options[stepper] = opt
  steppers = format_all_pins(steppers, mcu_name, tmc_options)
  s = io.StringIO()
  writer = generate_mmu_hardware(steppers, tmc_options)
  writer.write(s)
  s.seek(0)
  full_config = s.read()
  full_config = f"""# This configuration was auto-generated by the 3MS Configuration Generator.
# https://link.3dcoded.xyz/l/cfggen
{source_url_text}
# 
# To install your new configuration:
# 1. Open your local `mmu_hardware.cfg`.
# 2. Copy the below configuration
# 3. Locate the gear section in your local `mmu_hardware.cfg`. It starts with:
#     # FILAMENT DRIVE GEAR STEPPER(S)  --------------------------------------------------------------------------------------
#     #  ██████╗ ███████╗ █████╗ ██████╗ 
#     # ██╔════╝ ██╔════╝██╔══██╗██╔══██╗
#     # ██║  ███╗█████╗  ███████║██████╔╝
#     # ██║   ██║██╔══╝  ██╔══██║██╔══██╗
#     # ╚██████╔╝███████╗██║  ██║██║  ██║
#     #  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
#    
#     and ends right before:
#     # SERVOS ---------------------------------------------------------------------------------------------------------------
#     # ███████╗███████╗██████╗ ██╗   ██╗ ██████╗ ███████╗
#     # ██╔════╝██╔════╝██╔══██╗██║   ██║██╔═══██╗██╔════╝
#     # ███████╗█████╗  ██████╔╝██║   ██║██║   ██║███████╗
#     # ╚════██║██╔══╝  ██╔══██╗╚██╗ ██╔╝██║   ██║╚════██║
#     # ███████║███████╗██║  ██║ ╚████╔╝ ╚██████╔╝███████║
#     # ╚══════╝╚══════╝╚═╝  ╚═╝  ╚═══╝   ╚═════╝ ╚══════╝
#
# 4. Replace the local gear section with the text you copied.
#

{full_config}"""
  return full_config