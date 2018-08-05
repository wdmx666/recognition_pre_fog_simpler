# coding=utf-8

import os,sys
sys.path.append(os.path.abspath(os.path.pardir))
sys.path.append(os.path.abspath("."))
from recognition_pre_fog.model.processors import FeatureStatusMergeProcessor
from recognition_pre_fog.model.sample_maker_pipe import DataArrayMaker2
from recognition_pre_fog.model.model_train import train_model
from recognition_pre_fog.etl_signal.scheduler import SignalETLSource



import click

@click.group()
def cli():
    pass

@click.command()
def feature_status_merge_processor():
    my_source = FeatureStatusMergeProcessor()
    print("Open %s!"% my_source.__class__.__name__)
    print("===========================^!^================================")
    my_source.process()

# @click.command()
# def data_array_maker():
#     DataArrayMaker.process()
#     click.echo('Terminated DataArrayMaker.process')

@click.command()
def data_array_maker2():
    DataArrayMaker2.process()
    click.echo('Terminated DataArrayMaker2.process')



@click.command()
def train():
    train_model()
    click.echo('Terminated DataArrayMaker.process')


@click.command()
def etl_signal():
    my_source = SignalETLSource()
    print("Open %s!" % my_source.__class__.__name__)
    print("===========================^!^================================")
    my_source.open()

cli.add_command(feature_status_merge_processor)
cli.add_command(data_array_maker2)
cli.add_command(train)


if __name__ == "__main__":
    print("Start the APP!")
    cli()

