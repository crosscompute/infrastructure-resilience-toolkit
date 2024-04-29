#!/usr/bin/env python
# coding: utf-8

# # Size Transformers and Conductors Given Lengths
# 
# Objective
# - Minimize cost.
# 
# Constraints
# - Each distribution transformer has a maximum capacity in kVA.
# - Each service drop must be within a certain percentage of the target voltage.

# In[1]:


# TODO: Use phase_count, motor_horsepower, target_in_volts to get current_in_amps
# TODO: Use phase_count, power_in_watts, target_in_volts to get current_in_amps
# TODO: Normalize calculation units to use base scientific units
# TODO: Convert table units to calculation units based on column name
# TODO: Check that input variables have required fields
# TODO: Match transformer secondary voltage to service drop voltage
# TODO: Support DC circuit calculations
# TODO: Estimate cost in waybill


# In[2]:


from os import getenv
from pathlib import Path

input_folder = Path(getenv('INPUT_FOLDER', 'batches/standard/input'))
output_folder = Path(getenv('OUTPUT_FOLDER', 'batches/standard/output'))
output_folder.mkdir(parents=True, exist_ok=True)


# In[3]:


import json

with (input_folder / 'variables.dictionary').open('rt') as f:
    variables_dictionary = json.load(f)
variables_dictionary


# In[4]:


import pandas as pd


# In[5]:


maximum_voltage_drop_percent = variables_dictionary['maximum_voltage_drop_percent']
temperature_in_celsius = variables_dictionary['temperature_in_celsius']
# is_alternating_current = True


# In[6]:


transformer_types_table = pd.read_csv(input_folder / 'transformer-types.csv')
transformer_types_table.sort_values(['cost_in_dollars', 'size_in_kva'], inplace=True)
transformer_types_table[:2]


# In[7]:


conductor_types_table = pd.read_csv(input_folder / 'conductor-types.csv')
conductor_types_table.sort_values(['cost_in_dollars_per_foot', 'size_in_mm2'], inplace=True)
conductor_types_table[:2]


# In[8]:


with open(input_folder / 'service-drops.txt', 'rt') as f:
    service_drops_text = f.read().strip()
print(service_drops_text)


# In[9]:


service_drop_dictionaries = []
service_drop_dictionary = {}
for line in service_drops_text.splitlines():
    line = line.strip()
    if line.startswith('#'):
        continue
    if not line:
        if service_drop_dictionary:
            service_drop_dictionaries.append(service_drop_dictionary)
        service_drop_dictionary = {}
        continue
    key, value = line.split('=')
    key = key.strip()
    value = value.strip()
    try:
        float_value = float(value)
    except ValueError:
        pass
    else:
        try:
            integer_value = int(value)
        except ValueError:
            value = float_value
        else:
            value = integer_value if float_value == integer_value else float_value
    service_drop_dictionary[key] = value
if service_drop_dictionary:
    service_drop_dictionaries.append(service_drop_dictionary)    
service_drop_dictionaries


# ## Check that service drops do not exceed the maximum capacity of their transformer

# In[10]:


# Group service drops by transformer
from collections import defaultdict
service_drop_dictionaries_by_transformer_name = defaultdict(list)
for d in service_drop_dictionaries:
    service_drop_dictionaries_by_transformer_name[d['transformer_name']].append(d)
service_drop_dictionaries_by_transformer_name = dict(service_drop_dictionaries_by_transformer_name)    
service_drop_dictionaries_by_transformer_name


# In[11]:


transformer_dictionaries = []
for transformer_name in service_drop_dictionaries_by_transformer_name:
    minimum_power_in_kva = 0
    phase_counts = []
    service_drop_names = []
    for service_drop_dictionary in service_drop_dictionaries_by_transformer_name[transformer_name]:
        minimum_transformer_size_in_kva = service_drop_dictionary[
            'maximum_power_in_kilowatts'] / service_drop_dictionary['minimum_cosine_phi']
        minimum_power_in_kva += minimum_transformer_size_in_kva
        phase_counts.append(service_drop_dictionary['phase_count'])
        service_drop_names.append(service_drop_dictionary['service_drop_name'])
    phase_counts = set(phase_counts)        
    assert len(phase_counts) == 1
    phase_count = list(phase_counts)[0]
    transformer_type_dictionary = dict(transformer_types_table[(
        transformer_types_table['phase_count'] == phase_count
    ) & (
        transformer_types_table['size_in_kva'] >= minimum_power_in_kva
    )].iloc[0])
    transformer_dictionaries.append({
        'transformer_name': transformer_name,
        'transformer_type_nickname': transformer_type_dictionary['nickname'],
        'phase_count': phase_count,
        'minimum_size_in_kva': minimum_power_in_kva,
        'size_in_kva': transformer_type_dictionary['size_in_kva'],
        'service_drop_names': service_drop_names})
transformer_dictionaries


# ## Check that each service drop is within a certain percentage of the target voltage

# In[12]:


from infrastructure_resilience_toolkit.routines import compute_voltage_drop_percent

for service_drop_dictionary in service_drop_dictionaries:
    is_three_phase = service_drop_dictionary['phase_count'] == 3
    line_to_line_in_volts = service_drop_dictionary['line_to_line_in_volts']
    conductor_instalation_type = service_drop_dictionary['conductor_installation_type']
    conductor_length_in_feet = service_drop_dictionary['conductor_length_in_feet']
    conductor_spacing_in_inches = service_drop_dictionary['conductor_spacing_in_inches']
    current_in_amps = service_drop_dictionary['maximum_power_in_kilowatts'] / line_to_line_in_volts
    minimum_cosine_phi = service_drop_dictionary['minimum_cosine_phi']
    maximum_cosine_phi = service_drop_dictionary['maximum_cosine_phi']
    selected_conductor_types_table = conductor_types_table[(
        conductor_types_table['installation_type'] == conductor_instalation_type
    ) & (
        conductor_types_table['spacing_in_inches'] == conductor_spacing_in_inches
    ) & (        
        conductor_types_table['temperature_in_celsius'] == temperature_in_celsius
    )]
    for conductor_index, conductor_row in selected_conductor_types_table.iterrows():
        resistance_in_ohms = conductor_row['resistance_ac_in_ohms_per_kilofoot'] * conductor_length_in_feet / 1000
        reactance_in_ohms = conductor_row['reactance_inductive_in_ohm_per_kilofoot'] * conductor_length_in_feet / 1000
        ampacity_in_amps = conductor_row['ampacity_in_amps']
        voltage_drop_percents = []
        for cosine_phi in minimum_cosine_phi, maximum_cosine_phi:
            voltage_drop_percents.append(compute_voltage_drop_percent(
                is_three_phase=is_three_phase,
                source_line_to_line_in_volts=line_to_line_in_volts,
                current_in_amps=current_in_amps,
                resistance_in_ohms=resistance_in_ohms,
                reactance_in_ohms=reactance_in_ohms,
                cosine_phi=cosine_phi))
        voltage_drop_percent = max(voltage_drop_percents)
        if current_in_amps > ampacity_in_amps:
            continue
        if voltage_drop_percent <= maximum_voltage_drop_percent:
            break
    service_drop_dictionary.update({
        'conductor_type_nickname': conductor_row['nickname'],
        'size_in_awg': conductor_row['size_in_awg'],
        'size_in_kcmil': conductor_row['size_in_kcmil'],
        'size_in_mm2': conductor_row['size_in_mm2'],
        'ampacity_in_amps': ampacity_in_amps,
        'estimated_current_in_amps': current_in_amps,
        'estimated_voltage_drop_percent': voltage_drop_percent})
for d in service_drop_dictionaries:
    print(d)


# ## Save output files

# In[16]:


transformers_table = pd.DataFrame(transformer_dictionaries)
transformers_table.to_csv(output_folder / 'transformers.csv', index=False)


# In[17]:


conductors_table = pd.DataFrame(service_drop_dictionaries)
conductors_table.to_csv(output_folder / 'conductors.csv', index=False)


# In[36]:


waybill_table = pd.concat([
    transformers_table['transformer_type_nickname'].value_counts(),
    conductors_table['conductor_type_nickname'].value_counts()])
pd.DataFrame(waybill_table.reset_index()).rename(columns={
    'index': 'nickname',
    'count': 'count',
}).to_csv(output_folder / 'waybill.csv', index=False)

