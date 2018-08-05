# coding=utf8

import click
import os,sys
sys.path.append(os.path.abspath(os.path.pardir))
sys.path.append(os.path.abspath("."))
from recognition_pre_fog.result_evaluation.app_object_manager import ObjectMaker as ResultEvalObjectMaker
from recognition_pre_fog.select_feature_para.app_object_manager import ObjectMaker as SelectFeatureObjectMaker


@click.group()
def cli():
    pass


@click.command()
def event_para():
    return ResultEvalObjectMaker().make().get_bean("EventParameterScheduler").run(None)

    print("===========================^!^================================")


@click.command()
def select_features():
    return SelectFeatureObjectMaker().make().get_bean("SelectFeatureScheduler").run(None)

    print("===========================^!^================================")

cli.add_command(event_para)


if __name__ == "__main__":
    print("Start the APP!")
    #cli()
    #event_para()
    select_features()
