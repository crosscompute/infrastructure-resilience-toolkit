from math import sqrt


def compute_voltage_drop_percent(
    is_three_phase,
    source_line_to_line_in_volts,
    current_in_amps,
    resistance_in_ohms,
    reactance_in_ohms,
    cosine_phi,
):
    k = sqrt(3) if is_three_phase else 2
    
    def get_line_to_neutral_in_volts(line_to_line_in_volts):
        return line_to_line_in_volts / k
        
    def get_line_to_line_in_volts(line_to_neutral_in_volts):
        return line_to_neutral_in_volts * k

    sine_phi = sqrt(1 - cosine_phi ** 2)
    source_line_to_neutral_in_volts = get_line_to_neutral_in_volts(source_line_to_line_in_volts)
    # 1990 IEEE Standard 241 Page 72
    target_line_to_neutral_in_volts = sqrt(source_line_to_neutral_in_volts ** 2 - (
        current_in_amps * reactance_in_ohms * cosine_phi -
        current_in_amps * resistance_in_ohms * sine_phi) ** 2
    ) - (
        current_in_amps * resistance_in_ohms * cosine_phi +
        current_in_amps * reactance_in_ohms * sine_phi)
    target_line_to_line_in_volts = get_line_to_line_in_volts(target_line_to_neutral_in_volts)
    line_to_line_drop_in_volts = source_line_to_line_in_volts - target_line_to_line_in_volts
    return 100 * line_to_line_drop_in_volts / source_line_to_line_in_volts