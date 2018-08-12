
from recognition_pre_fog_simpler.s8_para_evaluation.preparation import FeatureParaSelectConfig


if __name__=="__main__":
    #fr = FeatureParaSelectConfig.featureRanker()
    finit = FeatureParaSelectConfig.featureSelectorData()
    finit.process()
    #print(fr.calculate(None))
    print(finit.process())




