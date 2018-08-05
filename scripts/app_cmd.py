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
    pass
    print("=========主线程（进程）运行完毕===%s==============",function.__class__.__name__)

@click.command()
def train_test():
    pass
    print("=========主线程（进程）运行完毕===%s==============",function.__class__.__name__)

cli.add_command(etl_signal)
cli.add_command(etl_video)
cli.add_command(remark_extract_signal)
cli.add_command(re_etl_feature)
cli.add_command(re_etl_feature)
cli.add_command(train_test)






if __name__ == "__main__":
    print("Start the APP!")
    #cli()
    #etl_signal()
    #etl_video()
    remark_extract_signal()
    #re_etl_feature()
    #train_test()

