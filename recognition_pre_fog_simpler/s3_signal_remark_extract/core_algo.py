
import numpy as np
import abc
from scipy import stats,fftpack



# 特征对照列表
# (最大值，最小值，绝对平均值，峰峰值，均方根，均值，标准差，偏态，峭度，方差，
#  波形因子，波峰因子，变异系数，偏态系数，余隙因子，脉冲因子，能量因子，
#  平均频率，中心频率，频率均方根，频率标准差)
features_info={"F01":"最大值","F02":"最小值","F03":"绝对平均值","F04":"峰峰值",
              "F05":"均方根","F06":"均值","F07":"标准差","F08":"偏态",
              "F09":"峭度","F10":"方差","F11":"波形因子","F12":"波峰因子",
              "F13":"变异系数","F14":"偏态系数","F15":"余隙因子","F16":"脉冲因子",
              "F17":"脉冲因子","F18":"平均频率","F19":"平均频率","F20":"中心频率",
              "F21":"频率均方根","F22":"频率标准差"}


# 接口/抽象类4定义各种具体的特征提取器
class FeatureExtractor(metaclass=abc.ABCMeta):
    def run(self, series):
        pass


# 时域特征计算 ##
# (最大值，最小值，绝对平均值，峰峰值，均方根，均值，标准差，偏态，峭度，方差，
#  波形因子，波峰因子，变异系数，偏态系数，余隙因子，脉冲因子，能量因子，
# 所有的具体特征提取器都是无状态的，不会进行状态维护 #


class F1(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求最大值
    """
    def __init__(self):
        self.c=0
    def run(self, series):
        self.c += 1
        #series
        #print(self.c,"-->",series[0:5])
        return round(np.max(series), 2)


class F2(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求最小值
    """
    def run(self, series):
        return round(np.min(series), 2)


class F3(FeatureExtractor):
    """对于有限长度信号序列时域幅值，先求绝对值，再求均值
    """

    def run(self, series):
        return round(np.mean(np.abs(series)), 2)


class F4(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求极差
    """
    def run(self, series):
        return round(np.max(series) - np.min(series), 2)


class F5(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求均方根--平方后求平均开根号
    """
    def run(self, series):
        return round(np.sqrt(np.mean(np.square(series))), 2)


class F6(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求均值
    """
    def run(self, series):
        return round(np.mean(series), 2)


class F7(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求标准差
    """
    def run(self, series):
        return round(np.std(series), 2)


class F8(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求偏度（标准化三阶中心矩）
       三阶中心矩/三阶标准差
    """
    def run(self, series):
        return round(stats.moment(series, 3) / np.power(np.std(series), 3), 2)


class F9(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求偏度（标准化四阶中心矩）
       四阶中心矩/四阶标准差
    """
    def run(self, series):
        return round(stats.moment(series, 4) / np.power(np.std(series), 4), 2)


class F10(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求方差(二阶中心矩))
    """

    def run(self, series):
        return round(np.var(series), 2)


class F11(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求波形因子--绝对平方均值开根号/绝对均值
    """

    def run(self, series):
        return round(np.sqrt(np.mean(np.square(np.abs(series)))) / np.mean(np.abs(series)), 2)


class F12(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求波峰因子--最大值/平方均值开根号
    """

    def run(self, series):
        return round(np.max(series) / np.sqrt(np.mean(np.square(series))), 2)


class F13(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求变异系数--均值/标准差
    """

    def run(self, series):
        return round(np.mean(series) / np.std(series), 2)


class F14(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求偏态系数--信号/标准差之后三次方求均值
    """

    def run(self, series):
        return round(np.mean(np.power(series / np.std(series), 3)), 2)


class F15(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求峭度系数--信号/标准差之后四次方求均值
    """

    def run(self, series):
        return round(np.mean(np.power(series / np.std(series), 4)), 2)


class F16(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求余隙因子--最大值/平方和均值
    """

    def run(self, series):
        return round(np.max(series) / np.mean(np.square(series)), 2)


class F17(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求脉冲因子--最大值/绝对均值
    """

    def run(self, series):
        return round(np.max(series) / np.mean(np.abs(series)), 2)


class F18(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求能量因子--最大值/绝对均值
    """

    def __cycle_shit(self, series, k):
        return np.append(series[-1:], series[:-1])

    def __delta_x(self, sr):
        return np.square(sr[0]) - sr[1] * sr[2]

    def run(self, series):
        data = np.vstack((series, self.__cycle_shit(series, 1), self.__cycle_shit(series, -1)))
        delta_x = np.apply_along_axis(self.__delta_x, 0, data)
        return round(stats.moment(delta_x, 4) / np.square(stats.moment(delta_x, 2)), 2)


#  平均频率，中心频率，频率均方根，频率标准差 ,首先对时域信号进行傅里叶变换
class Signal2FourierDomain(object):
    def __init__(self, cache, fs=100):
        self.cache = cache
        self.fs = fs
        self.run_times = 0

    def transform(self,series):
        self.run_times += 1
        keys = self.cache.keys()
        if self.run_times in keys:
            if self.run_times%100==0:
                """print("使用FFT缓存结果- %s - "%self.run_times)"""
            return self.cache.get(self.run_times)
        else:
            self.cache[self.run_times] = self.__real_transform(series)
            return self.cache.get(self.run_times)

    def __real_transform(self, series):
        # Number of sample points
        N = len(series)
        # sample spacing
        T = 1.0 / self.fs
        x = np.linspace(0.0, N * T, N)
        yf = fftpack.fft(series)
        xf = np.linspace(0.0, 1.0 / (2.0 * T), N // 2)
        result_data = (xf, 2.0 / N * np.abs(yf[0:N // 2]))

        return result_data


# 所有的具体特征提取器都是无状态的，不会进行状态维护 #
# 频域特征计算
class F19(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求平均功率
    """
    def __init__(self):
        self.transformer = None
        self.run_times=0

    def set_pre_transformer(self, transformer):
        self.transformer = transformer
        return self

    def run(self, series):
        self.run_times += 1
        if self.run_times%100 == 0:
            """print("the F19 data %s: "%self.run_times,series[0:5])"""
        result_data = self.transformer.transform(series)
        return round(np.mean(result_data[1]), 2)


class F20(FeatureExtractor):
    def __init__(self):
        self.transformer = None

    def set_pre_transformer(self, transformer):
        self.transformer = transformer
        return self

    def run(self, series):
        result_data = self.transformer.transform(series)
        return round(np.dot(result_data[0], result_data[1]) / np.sum(result_data[1]), 2)


class F21(FeatureExtractor):
    def __init__(self):
        self.transformer = None

    def set_pre_transformer(self, transformer):
        self.transformer = transformer
        return self

    def run(self, series):
        result_data = self.transformer.transform(series)
        return round(np.sqrt(np.dot(np.square(result_data[0]), result_data[1]) / np.sum(result_data[1])), 2)


class F22(FeatureExtractor):
    def __init__(self):
        self.transformer = None

    def set_pre_transformer(self, transformer):
        self.transformer = transformer
        return self

    def run(self, series):
        result_data = self.transformer.transform(series)
        # print(result_data)
        fc = np.dot(result_data[0], result_data[1]) / np.sum(result_data[1])
        # print(result_data[0].__class__)
        # print(np.square(result_data[0]-fc,2))
        return round(np.sqrt(np.dot(np.square(result_data[0] - fc), result_data[1]) / np.sum(result_data[1])), 2)


class F23(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求脉冲因子--最大值/绝对均值
    """
    def run(self, series):
        return round(series[-1]-series[-4], 2)


class F24(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求脉冲因子--最大值/绝对均值
    """
    def run(self, series):
        return round(series[-1]-series[-6], 2)


class F25(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求脉冲因子--最大值/绝对均值
    """
    def run(self, series):
        return round(series[-1]-series[-10], 2)


class F26(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求脉冲因子--最大值/绝对均值
    """
    def run(self, series):
        return round(series[-1]-series[-20], 2)


class F27(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求脉冲因子--最大值/绝对均值
    """
    def run(self, series):
        return round(series[-1]-series[-40], 2)


class F28(FeatureExtractor):
    """对于有限长度信号序列时域幅值，求脉冲因子--最大值/绝对均值
    """
    def run(self, series):
        return round(series[-1]-series[-100], 2)