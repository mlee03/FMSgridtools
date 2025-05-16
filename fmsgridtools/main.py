import click
import datetime
import fmsgridtools

@click.group()
def main():
    click.echo("starting fmsgridtools")

@main.group()
def remap():
    click.echo("starting remap")

@main.group()
def make_topog():
    click.echo("starting make_topog")

@main.group():
def make_mosaic():
    click.echo("starting make_mosaic")

@main.group()
def make_hgrid():
    click.echo("starting make_hgrid")

remap.add_command(fmsgridtools.re_map.conservative_method)
make_topog.add_command(fmsgridtools.topog.realistic)

if __name__ == "__main__":
    main()
    
