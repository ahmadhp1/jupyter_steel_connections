import json
import math


def round_to_nearest_number(value, target):
    remainder = value % target
    return value + (target - remainder)


class ISection:
    def __init__(self, h, bf, tf, tw, z, fy, fu):
        self.h = float(h)
        self.bf = float(bf)
        self.tf = float(tf)
        self.tw = float(tw)
        self.z = float(z)
        self.fy = float(fy)
        self.fu = float(fu)


class TubeSection:
    def __init__(self, d, t, z, fy, fu):
        self.d = d
        self.t = t
        self.z = z
        self.fy = fy
        self.fu = fu


class DesignInput:
    def __init__(self, type, beam, column, beam_lenght, dead_load, live_load, load_width):
        self.type = type
        self.beam = beam
        self.column = column
        self.beam_lenght = beam_lenght
        self.dead_load = dead_load  # Kn/m
        self.live_load = live_load  # Kn/m
        self.load_width = load_width


def read_input_json():
    json_path = input("Enter path to the JSON file: ")

    if json_path == "":
        json_path = "./test.json"

    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error reading file:", json_path)
        return None
    except json.JSONDecodeError as e:
        print("Error parsing JSON:", e)
        return None

    config = []
    for item in data:
        beamData = item["beam"]
        columnData = item["column"]

        beam = ISection(
            beamData["h"],
            beamData["bf"],
            beamData["tf"],
            beamData["tw"],
            beamData["z"],
            beamData["fy"],
            beamData["fu"])

        column = TubeSection(
            columnData["d"],
            columnData["t"],
            columnData["z"],
            columnData["fy"],
            columnData["fu"])

        config.append(
            DesignInput(
                item["type"],
                beam,
                column,
                item["beamLenght"],
                item["deadLoad"],
                item["liveLoad"],
                item["loadWidth"],
            )
        )

    return config


def calc_tpb(mu, db, initial_value, bpb, fy, tolerance=0.001):
    tpb = mu * 10**6 / (1 * (db + initial_value) * bpb * fy)
    return round_to_nearest_number(tpb, 5)


def load_comb(dead, live):
    return 1.2 * dead + live


def calculateWelding(thickness):
    if thickness <= 6:
        return 3
    elif thickness <= 12:
        return 5
    elif thickness <= 20:
        return 6
    else:
        return 8


def main():
    design_input = read_input_json()

    if design_input is None:
        return

    input = design_input[0]

    db = input.beam.h + 2*input.beam.tf
    lp = db + 10
    sh = lp / 1000  # M
    lh = input.beam_lenght - input.column.d/1000 - 2 * sh  # M

    qu = load_comb(input.dead_load, input.live_load)
    qu *= input.load_width  # Kn/m
    pu = 205.0  # kn

    ry = 1.15
    max_cpr = 1.2

    actual_cpr = (input.beam.fy + input.beam.fu) / 2 * input.beam.fy
    cpr = min(actual_cpr, max_cpr)
    mpr = cpr * ry * (input.beam.z / math.pow(10, 6)) * \
        input.beam.fy
    vpr = (2 * mpr) / lh + (qu * lh + pu) / 2
    vu = vpr + qu * sh
    mu = mpr + vpr * sh + (qu * math.pow(sh, 2))

    bpb = input.beam.bf + 50
    tpb = calc_tpb(mu, db, 40, bpb, input.beam.fy)
    aMin = calculateWelding(input.beam.tf)
    aMax = min(input.beam.tf, input.column.t) - 2

    Lw = (mu * 10**6) / (db*140*aMax)
    lpb = (Lw / 2) + 20
    lpb = round_to_nearest_number(lpb, 25)

    print("Required BottomPlate Thickness (Tpb):", tpb, "mm")
    print("Required BottomPlate Welding Size Between:", aMin, aMax, "mm")
    print("Required BottomPlate Lenght:", lpb, "mm")
    print("Shear Force (Vu):", vu, "kN")


main()
