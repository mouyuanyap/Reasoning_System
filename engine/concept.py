from engine.base_classes import *

BooleanIndividual, BooleanConcept = create_individual_concept('Boolean', 'Base')
NumberIndividual, NumberConcept = create_individual_concept('Number', 'Base')
VarcharIndividual, VarcharConcept = create_individual_concept('Varchar', 'Base')
DateIndividual, DateConcept = create_individual_concept('Date', 'Base')
CurrencyIndividual, CurrencyConcept = create_individual_concept('Currency', 'Base')


IndustryClassIndividual, IndustryClassConcept = create_individual_concept('IndustryClass', 'Base')
IndexTypeIndividual, IndexTypeConcept = create_individual_concept('IndexType', 'Base')

CompanyIndividual, CompanyConcept = create_individual_concept('Company', 'Base')
CompanyInfoIndividual, CompanyInfoConcept = create_individual_concept('CompanyInfo', 'Base')

PersonIndividual, PersonConcept = create_individual_concept('Person', 'Base')

IndustryIndividual, IndustryConcept = create_individual_concept('Industry', 'Base')
IndexIndividual, IndexConcept = create_individual_concept('Index', 'Base')
FinancialIndicatorIndividual, FinancialIndicatorConcept = create_individual_concept('FinancialIndicator', 'Base')
TradeDataIndicatorIndividual ,TradeDataIndicatorConcept = create_individual_concept('TradeDataIndicator', 'Base')

CommodityIndividual, CommodityConcept = create_individual_concept('Commodity', 'Base')
EventIndividual, EventConcept = create_individual_concept('Event', 'Base')

FutureIndividual, FutureConcept = create_individual_concept('Future', 'Base')
FutureNameIndividual, FutureNameConcept = create_individual_concept('FutureName', 'Base')
FutureInfoIndividual, FutureInfoConcept = create_individual_concept('FutureInfo', 'Base')
FutureQuoteIndicatorIndividual, FutureQuoteIndicatorConcept = create_individual_concept('FutureQuoteIndicator', 'Base')
ExchangeIndividual, ExchangeConcept = create_individual_concept('Exchange', 'Base')

CountryIndividual, CountryConcept = create_individual_concept('Country', 'Base')
CountryMacroIndicatorIndividual, CountryMacroIndicatorConcept = create_individual_concept('CountryMacroIndicator', 'Base')

BusinessIndividual, BusinessConcept = create_individual_concept('Business', 'Base')
BusinessSalesIndicatorIndividual, BusinessSalesIndicatorConcept = create_individual_concept('BusinessSalesIndicator', 'Base')
# 不过没啥复用需求的，用str,int之类的就也蛮好，只是需要改check scope里的判断。主要是因为，用其他推理引擎的话，我们倒也没必要考虑私有不私有了
