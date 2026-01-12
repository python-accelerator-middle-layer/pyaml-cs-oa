import sys
import yaml
import at


if len(sys.argv) != 3:
    print(f"Convert to KL convrention, basically multiply the calibration factor by the magnet length")
    print(f"Usage: {sys.argv[0]} filename.yaml lattice.mat")
    quit()

ring = at.load_lattice(sys.argv[2])


def get_length(names:str):
    name_list = []
    l = 0
    # Support only list() syntax
    if names.startswith("list("):
        try:
            name_list = names[5:-1].rsplit(",")
        except Exception as err:
            strErr = f"{names}: Invalid lattice_names syntax :{str(err)}"
            print(strErr)
            quit()
    else:
        name_list = [names]

    for n in name_list:
        elts = ring.get_elements(n)
        for e in elts:
            l += e.Length

    return l


def get_names(d) -> str:
    if "lattice_names" in d:
        return d["lattice_names"]
    else:
        return d["name"]


def convert(d,path:str):

    if isinstance(d, list):
        # list can be a list of objects or a list of native types
        l = []
        for _index, e in enumerate(d):
            if isinstance(e, dict) or isinstance(e, list):
                convert(e,f"{path}/{get_names(e)}")

    elif isinstance(d, dict):
        for key, value in d.items():
            if isinstance(value, dict) or isinstance(value, list):
                convert(value,f"{path}/{str(key)}")

        if d["type"]=="pyaml.magnet.linear_model":
            names = path.split("/")[-2] # Get elements names
            length = get_length(names) # Get total length
            d["calibration_factor"] *= length


with open(sys.argv[1]) as stream:
    try:
        d = yaml.safe_load(stream)
        convert(d,"")        
        yaml.dump(d,sys.stdout,sort_keys=False)
    except yaml.YAMLError as exc:
        print(f"Failed to open {sys.argv[1]}: {str(exc)}")


