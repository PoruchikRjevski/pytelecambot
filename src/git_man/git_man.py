import git_man.cmd_executor as c_e
import git_man.git_defs as g_d

from logger import *


__all__ = ['get_commits_num']


def get_commits_num():
        cmd = g_d.GIT_CMD.format(g_d.A_REV_LIST
                                 + g_d.A_ALL
                                 + g_d.A_COUNT)

        out = c_e.run_cmd(cmd)

        try:
            out_int = int(out)
        except ValueError:
            out_err("bad repo")
            return ""
        else:
            out_log("change build version: {:s}".format(out))

        return out