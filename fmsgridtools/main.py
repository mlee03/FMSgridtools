import click
import fmsgridtools

@click.group()
def main():
    click.echo("Starting fmsgridtools")

@main.group()
def remap():
    click.echo("Starting remap")

@main.group()
def make_topog():
    click.echo("Starting make_topog")

@main.group()
def make_mosaic():
    click.echo("Starting make_mosaic")

@main.group()
def make_hgrid():
    click.echo("Starting make_hgrid")

remap.add_command(fmsgridtools.re_map.conservative_method)

make_topog.add_command(fmsgridtools.make_topog.realistic_or_basin)

make_mosaic.add_command(fmsgridtools.make_mosaic.solo)
make_mosaic.add_command(fmsgridtools.make_mosaic.regional)
make_mosaic.add_command(fmsgridtools.make_mosaic.quick)
make_mosaic.add_command(fmsgridtools.make_mosaic.coupled)

if __name__ == "__main__":
    main()
    
