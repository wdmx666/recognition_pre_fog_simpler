# ---------------------------------------------------------
# Name:        command for client start
# Description: some fundamental entry-point
# Author:      Lucas Yu
# Created:     2018-05-02
# Copyright:   (c) Zhenluo,Shenzhen,Guangdong 2018
# Licence:
# ---------------------------------------------------------

import os
import sys
sys.path.append(os.path.abspath(os.path.pardir))
sys.path.append(os.path.abspath("."))
import click

from recognition_pre_fog_simpler.s1_etl_signal.preparation import SignalETLConfig
from recognition_pre_fog_simpler.s2_etl_video.preparation import VideoETLConfig
from recognition_pre_fog_simpler.s3_signal_remark_extract.preparation import SignalRemarkExtractConfig
from recognition_pre_fog_simpler.s4_re_etl_feature.preparation import FeatureReETLConfig
from recognition_pre_fog_simpler.s8_para_evaluation.preparation import ParaSelectorConfig



@click.group()
def cli():
    pass

@click.command()
def etl_signal():
    SignalETLConfig.signalETLServer().start()
    print("=========主线程（进程）运行完毕===%s==============","signalETLServer()")


@click.command()
def etl_video():
    VideoETLConfig.videoETLServer().start()
    print("=========主线程（进程）运行完毕===%s==============",'videoETLServer()')


@click.command()
def remark_extract_signal():
    SignalRemarkExtractConfig.signalRemarkExtractServer().start()
    print("=========主线程（进程）运行完毕===%s==============",'signalRemarkExtractServer()')


@click.command()
def re_etl_feature():
    FeatureReETLConfig.featureReETLServer().start()
    print("=========主线程（进程）运行完毕===%s==============",'featureReETLServer()')

@click.command()
def select_extract_para():
    ParaSelectorConfig.extractParaSelectorServer().start()
    print("=========主线程（进程）运行完毕===%s==============", 'extractParaSelectorServer()')

@click.command()
def select_feature():
    ParaSelectorConfig.featureSelectorServer().start()
    print("=========主线程（进程）运行完毕===%s==============", 'featureSelectorServer()')


@click.command()
def select_model_hyper_para():
    ParaSelectorConfig.modelParaSelectorServer().start()
    print("=========主线程（进程）运行完毕===%s==============", 'modelParaSelectorServer()')


@click.command()
def select_event_para():
    ParaSelectorConfig.eventParaSelectorServer().start()
    print("=========主线程（进程）运行完毕===%s==============", 'eventParaSelectorServer()')

cli.add_command(etl_signal)
cli.add_command(etl_video)
cli.add_command(remark_extract_signal)
cli.add_command(re_etl_feature)
cli.add_command(select_extract_para)
cli.add_command(select_feature)
cli.add_command(select_model_hyper_para)
cli.add_command(select_event_para)


if __name__ == "__main__":
    print("Start the APP!")
    #cli()
    #etl_signal()
    #etl_video()
    #remark_extract_signal()
    #re_etl_feature()
    #select_extract_para()
    #select_feature()
    #select_model_hyper_para()
    select_event_para()

