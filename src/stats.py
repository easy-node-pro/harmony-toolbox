from toolbox.library import load_var_file
from toolbox.toolbox import menu_topper_regular
from toolbox.config import easy_env

if __name__ == "__main__":
    load_var_file(easy_env.dotenv_file)
    menu_topper_regular()