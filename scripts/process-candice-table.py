#!/usr/bin/env python3
"""===============================================================================

        FILE: scripts/process-candice-table.py

       USAGE: ./scripts/process-candice-table.py

 DESCRIPTION: 

     OPTIONS: ---
REQUIREMENTS: ---
        BUGS: ---
       NOTES: ---
      AUTHOR: Alex Leontiev (alozz1991@gmail.com)
ORGANIZATION: 
     VERSION: ---
     CREATED: 2020-12-01T17:11:28.959407
    REVISION: ---

==============================================================================="""

import click
import pandas as pd
import functools
import sys


@click.command()
@click.argument("fn", type=click.Path())
def process_candice_table(fn):
    df = pd.read_csv(fn, sep="\t")
    df = df.loc[:, ["status", "back", "candice"]]
    df = df[[(not pd.isna(r["back"])) or (not pd.isna(r["candice"]))
             for r in df.to_dict(orient="records")]]
    df = df[[s not in ["done","skip"] for s in df.status]]
    df = df.drop(columns=["status"])
    for r in df.to_dict(orient="records"):
        for fn in ["back","candice"]:
            assert r[fn]!="", r[fn]
    sys.stdout.write(df.to_csv(sep="\t", index=None))


if __name__ == "__main__":
    process_candice_table()
