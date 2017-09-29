import subprocess

from logger import *
from time_checker import *

__all__ = ['run_cmd']

DOC_CODE = "utf-8"

def run_cmd(cmd):
    command = cmd

    # cmd_run_t = start()
    proc = subprocess.Popen([command + '\n'],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)
    (out, err) = proc.communicate()
    # stop(cmd_run_t)

    u_out = out.decode(DOC_CODE).strip()
    u_err = err.decode(DOC_CODE).strip()

    # out_log("out: {:s}".format(u_out))

    if u_err:
        out_err("err: {:s}".format(u_err))

    return u_out


def main():
    print ("do nothing from there")


if __name__ == "__main__":
    main()