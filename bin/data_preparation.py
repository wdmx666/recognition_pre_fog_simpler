# coding=utf-8

import click
import os,sys
sys.path.append(os.path.abspath(os.path.pardir))
sys.path.append(os.path.abspath("."))

from recognition_pre_fog.etl_video.scheduler import VideoETLSource
from recognition_pre_fog.etl_signal.scheduler import SignalETLSource
from recognition_pre_fog.feature.scheduler import SignalFeatureSource


@click.group()
def cli():
    pass


@click.command()
def etl_signal():
    my_source = SignalETLSource()
    print("Open %s!" % my_source.__class__.__name__)
    print("===========================^!^================================")
    my_source.open()


@click.command()
def etl_video():
    my_source = VideoETLSource()
    print("Open %s!" % my_source.__class__.__name__)
    print("===========================^!^================================")
    my_source.open()

@click.command()
def feature():
    my_source = SignalFeatureSource()
    print("Open %s!" % my_source.__class__.__name__)
    print("===========================^!^================================")
    my_source.open()


cli.add_command(etl_signal)
cli.add_command(etl_video)
cli.add_command(feature)

if __name__ == "__main__":
    print("Start the APP!")
    #cli()
    #etl_signal()
    #etl_video()
    feature()

